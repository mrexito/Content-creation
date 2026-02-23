import { spawn } from "child_process"
import path from "path"
import fs from "fs"

const PROJECT_ROOT = path.resolve(process.cwd(), "..")
const SCRIPTS_DIR = path.join(PROJECT_ROOT, "scripts")
const DATA_OUTPUT_DIR = path.join(PROJECT_ROOT, "data", "output")

export interface RunOptions {
  pdfPath: string
  domain: string
  framework: "langchain" | "langgraph"
  numVariants: number
  maxRetries: number
  runId: string
  progressPath: string
  ocrTool?: string      // "auto" | "tesseract" | "mistral"
  llmProvider?: string  // "auto" | "openai" | "bfh"
  llmModel?: string     // model name, empty = provider default
}

export function runPipeline(opts: RunOptions): Promise<{ success: boolean; error?: string }> {
  const scriptName =
    opts.framework === "langchain"
      ? "run_langchain_pipeline.py"
      : "run_langgraph_pipeline.py"

  const scriptPath = path.join(SCRIPTS_DIR, scriptName)
  const outputDir = path.join(DATA_OUTPUT_DIR, opts.framework, opts.runId)

  fs.mkdirSync(outputDir, { recursive: true })

  const args = [
    scriptPath,
    "--pdf", opts.pdfPath,
    "--domain", opts.domain,
    "--variants", String(opts.numVariants),
    "--retries", String(opts.maxRetries),
    "--output-dir", outputDir,
    "--progress", opts.progressPath,
    "--run-id", opts.runId,
    "--ocr-tool", opts.ocrTool ?? "auto",
    "--llm-provider", opts.llmProvider ?? "auto",
    ...(opts.llmModel ? ["--llm-model", opts.llmModel] : []),
  ]

  return new Promise((resolve) => {
    const proc = spawn("python", args, {
      cwd: PROJECT_ROOT,
      env: { ...process.env, PYTHONPATH: path.join(PROJECT_ROOT, "src") },
    })

    let stderr = ""
    proc.stderr.on("data", (data) => {
      stderr += data.toString()
    })

    proc.on("close", (code) => {
      if (code === 0) {
        resolve({ success: true })
      } else {
        resolve({ success: false, error: stderr.slice(-500) })
      }
    })

    proc.on("error", (err) => {
      resolve({ success: false, error: err.message })
    })
  })
}

export function readProgress(progressPath: string) {
  try {
    if (!fs.existsSync(progressPath)) return null
    const raw = fs.readFileSync(progressPath, "utf-8")
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function readResult(runId: string, framework: string) {
  try {
    const resultPath = path.join(DATA_OUTPUT_DIR, framework, runId, "result.json")
    if (!fs.existsSync(resultPath)) return null
    return JSON.parse(fs.readFileSync(resultPath, "utf-8"))
  } catch {
    return null
  }
}

export function getProgressPath(runId: string, framework: string) {
  const dir = path.join(DATA_OUTPUT_DIR, framework, runId)
  fs.mkdirSync(dir, { recursive: true })
  return path.join(dir, "progress.json")
}

