import { NextRequest, NextResponse } from "next/server"
import { generateRunId } from "@/lib/file-utils"
import { runPipeline, getProgressPath } from "@/lib/python-runner"
import fs from "fs"
import path from "path"

const PROJECT_ROOT = path.resolve(process.cwd(), "..")

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { pdfPath, domain, framework, numVariants, maxRetries, ocrTool, llmProvider, llmModel } = body

    if (!pdfPath || !framework) {
      return NextResponse.json({ error: "pdfPath and framework are required" }, { status: 400 })
    }

    const runId = generateRunId()
    const frameworks: Array<"langchain" | "langgraph"> =
      framework === "both" ? ["langchain", "langgraph"] : [framework]

    // Write initial progress for each framework
    for (const fw of frameworks) {
      const progressPath = getProgressPath(runId, fw)
      const initial = {
        status: "running",
        current_phase: "parsing",
        phases_completed: [],
        progress_percent: 0,
        metadata: {
          pdf_name: path.basename(pdfPath),
          framework: fw,
          domain: domain || "auto",
        },
      }
      fs.writeFileSync(progressPath, JSON.stringify(initial, null, 2))
    }

    // Fire-and-forget: run in background
    for (const fw of frameworks) {
      const progressPath = getProgressPath(runId, fw)
      runPipeline({
        pdfPath,
        domain: domain || "auto",
        framework: fw,
        numVariants: numVariants ?? 2,
        maxRetries: maxRetries ?? 3,
        runId,
        progressPath,
        ocrTool: ocrTool || "auto",
        llmProvider: llmProvider || "auto",
        llmModel: llmModel || "",
      }).then(({ success, error }) => {
        // Update progress to final state on completion
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
