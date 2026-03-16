import { NextRequest, NextResponse } from "next/server"
import { generateRunId } from "@/lib/file-utils"
import { runPipeline, getProgressPath } from "@/lib/python-runner"
import { spawn } from "child_process"
import fs from "fs"
import path from "path"

const PROJECT_ROOT = path.resolve(process.cwd(), "..")

/** Run OCR once and write result to outputPath. Returns true on success. */
async function runOCR(opts: {
  pdfPath: string
  domain: string
  ocrTool: string
  outputPath: string
}): Promise<boolean> {
  const scriptPath = path.join(PROJECT_ROOT, "scripts", "run_ocr.py")
  return new Promise((resolve) => {
    const proc = spawn("python", [
      scriptPath,
      "--pdf", opts.pdfPath,
      "--domain", opts.domain,
      "--ocr-tool", opts.ocrTool,
      "--output", opts.outputPath,
    ], {
      cwd: PROJECT_ROOT,
      env: {
        ...process.env,
        PYTHONPATH: path.join(PROJECT_ROOT, "src"),
        PYTHONUNBUFFERED: "1",
      },
    })
    proc.on("close", (code) => resolve(code === 0))
    proc.on("error", () => resolve(false))
  })
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { pdfPath, domain, framework, numVariants, maxRetries, ocrTool, llmProvider, llmModel } = body

    if (!pdfPath || !framework) {
      return NextResponse.json({ error: "pdfPath and framework are required" }, { status: 400 })
    }

    const runId = generateRunId()
    type SingleFW = "langchain" | "langgraph" | "hybrid" | "agent_orchestrator" | "agent_multi" | "hybrid_agent"
    const ALL_FWS = ["langchain", "langgraph", "hybrid", "agent_orchestrator", "agent_multi", "hybrid_agent"]
    const frameworks: SingleFW[] =
      framework === "all"
        ? ["langchain", "langgraph", "hybrid"] // agent variants excluded from bulk "all"
        : (ALL_FWS as string[]).includes(framework)
        ? [framework as SingleFW]
        : ["langchain"] // Fallback für alte History-Einträge mit "both"

    // ── Write initial progress immediately so polling shows something ────────
    for (const fw of frameworks) {
      const progressPath = getProgressPath(runId, fw)
      fs.writeFileSync(progressPath, JSON.stringify({
        status: "running",
        current_phase: "parsing",
        phases_completed: [],
        progress_percent: 0,
        metadata: {
          pdf_name: path.basename(pdfPath),
          framework: fw,
          domain: domain || "auto",
          ocr_running: true,
        },
      }, null, 2))
    }

    // ── Return immediately so the client can start polling ───────────────────
    // OCR + pipeline run fully in the background.
    const sharedDir = path.join(PROJECT_ROOT, "data", "output", "shared", runId)
    fs.mkdirSync(sharedDir, { recursive: true })
    const ocrResultPath = path.join(sharedDir, "ocr_result.json")

    ;(async () => {
      // ── OCR pre-step ───────────────────────────────────────────────────────
      const ocrSuccess = await runOCR({
        pdfPath,
        domain: domain || "auto",
        ocrTool: ocrTool || "auto",
        outputPath: ocrResultPath,
      })

      if (!ocrSuccess) {
        // Mark all frameworks as failed — no point running them without text
        for (const fw of frameworks) {
          const progressPath = getProgressPath(runId, fw)
          try {
            const existing = JSON.parse(fs.readFileSync(progressPath, "utf-8"))
            if (existing.status === "complete" || existing.status === "error") continue
          } catch {}
          fs.writeFileSync(progressPath, JSON.stringify({
            status: "error",
            current_phase: "error",
            phases_completed: [],
            progress_percent: 0,
            metadata: {
              pdf_name: path.basename(pdfPath),
              framework: fw,
              domain: domain || "auto",
              error: "OCR-Vorverarbeitung fehlgeschlagen. Prüfe OCR-Tool und PDF.",
            },
          }, null, 2))
        }
        return
      }

      // Update progress: OCR/parsing done, framework processing starts
      for (const fw of frameworks) {
        const progressPath = getProgressPath(runId, fw)
        fs.writeFileSync(progressPath, JSON.stringify({
          status: "running",
          current_phase: "segmentation",
          phases_completed: ["parsing"],
          progress_percent: 10,
          metadata: {
            pdf_name: path.basename(pdfPath),
            framework: fw,
            domain: domain || "auto",
          },
        }, null, 2))
      }

      // ── Fire-and-forget: start all frameworks in parallel ──────────────────
      for (const fw of frameworks) {
        const progressPath = getProgressPath(runId, fw)
        runPipeline({
          pdfPath,
          domain: domain || "auto",
          framework: fw,
          numVariants: numVariants ?? 1,
          maxRetries: maxRetries ?? 3,
          runId,
          progressPath,
          ocrTool: ocrTool || "auto",
          llmProvider: llmProvider || "auto",
          llmModel: llmModel || "",
          preParsedTextPath: ocrResultPath,
        }).then(({ success, error }) => {
          // Only write if Python didn't already write a final status.
          // Python writes its own complete/error progress with detailed messages;
          // overwriting it would destroy the error message from the Python log.
          try {
            const existing = JSON.parse(fs.readFileSync(progressPath, "utf-8"))
            if (existing.status === "complete" || existing.status === "error") return
          } catch {}
          // Fallback: Python didn't reach a final write (e.g. killed) — write ourselves
          const prog = {
            status: success ? "complete" : "error",
            current_phase: success ? "complete" : "error",
            phases_completed: success
              ? ["parsing", "segmentation", "classification", "rewriting", "validation", "assembly"]
              : [],
            progress_percent: success ? 100 : 0,
            metadata: {
              pdf_name: path.basename(pdfPath),
              framework: fw,
              domain: domain || "auto",
              ...(error && { error }),
            },
          }
          try {
            fs.writeFileSync(progressPath, JSON.stringify(prog, null, 2))
          } catch {}
        })
      }
    })().catch((err) => {
      // Background error: write to all progress files that haven't finished yet
      for (const fw of frameworks) {
        try {
          const progressPath = getProgressPath(runId, fw)
          const existing = JSON.parse(fs.readFileSync(progressPath, "utf-8"))
          if (existing.status === "complete" || existing.status === "error") continue
          fs.writeFileSync(progressPath, JSON.stringify({
            status: "error",
            current_phase: "error",
            phases_completed: [],
            progress_percent: 0,
            metadata: {
              pdf_name: path.basename(pdfPath),
              framework: fw,
              domain: domain || "auto",
              error: String(err),
            },
          }, null, 2))
        } catch {}
      }
    })

    return NextResponse.json({
      success: true,
      runId,
      frameworks,
      pdfName: path.basename(pdfPath),
    })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
