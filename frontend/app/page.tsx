"use client"

import { useState, useCallback, useEffect } from "react"
import type { Domain, Framework, OcrTool, LlmProvider, RunResult } from "@/lib/types"
import { FileUpload } from "@/components/upload/file-upload"
import { DomainSelector } from "@/components/upload/domain-selector"
import { ConfigPanel } from "@/components/upload/config-panel"
import { FrameworkSelector } from "@/components/execution/framework-selector"
import { ProgressTracker } from "@/components/execution/progress-tracker"
import { ComparisonView } from "@/components/results/comparison-view"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Play, Square } from "lucide-react"
import { toast } from "sonner"
import { generateRunId } from "@/lib/file-utils"

type AppState = "idle" | "uploading" | "running" | "done"

function loadHistory(): RunResult[] {
  if (typeof window === "undefined") return []
  try {
    return JSON.parse(localStorage.getItem("runs") ?? "[]")
  } catch {
    return []
  }
}

function saveHistory(runs: RunResult[]) {
  if (typeof window === "undefined") return
  localStorage.setItem("runs", JSON.stringify(runs.slice(0, 50)))
}

export default function HomePage() {
  const [files, setFiles] = useState<File[]>([])
  const [domain, setDomain] = useState<Domain>("auto")
  const [framework, setFramework] = useState<Framework>("all")
  const [numVariants, setNumVariants] = useState(2)
  const [maxRetries, setMaxRetries] = useState(3)
  const [ocrTool, setOcrTool] = useState<OcrTool>("auto")
  const [llmProvider, setLlmProvider] = useState<LlmProvider>("auto")
  const [llmModel, setLlmModel] = useState("")

  const [appState, setAppState] = useState<AppState>("idle")
  const [activeRunId, setActiveRunId] = useState<string | null>(null)
  const [currentRun, setCurrentRun] = useState<RunResult | null>(null)

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.code === "Space" && e.target === document.body) {
        e.preventDefault()
        if (appState === "idle") handleStart()
        else if (appState === "running") handleStop()
      }
      if (e.code === "Escape" && appState === "running") handleStop()
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [appState, handleStart, handleStop])

  const handleStart = useCallback(async () => {
    if (!files.length) {
      toast.error("Bitte mindestens ein PDF hochladen")
      return
    }

    setAppState("uploading")

    try {
      // 1. Upload PDFs
      const formData = new FormData()
      files.forEach((f) => formData.append("files", f))
      const uploadRes = await fetch("/api/upload", { method: "POST", body: formData })
      const uploadData = await uploadRes.json()

      if (!uploadData.success) throw new Error(uploadData.error)

      const pdfPath = uploadData.files[0].path // Process first file

      // 2. Start run
      const runRes = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdfPath, domain, framework, numVariants, maxRetries, ocrTool, llmProvider, llmModel }),
      })
      const runData = await runRes.json()
      if (!runData.success) throw new Error(runData.error)

      const runId = runData.runId
      setActiveRunId(runId)
      setAppState("running")
      toast.success("Pipeline gestartet")

      // Initialize run record
      const run: RunResult = {
        id: runId,
        timestamp: new Date().toISOString(),
        pdf_name: files[0].name,
        domain,
        framework,
        config: { numVariants, maxRetries, ocrTool, llmProvider, llmModel: llmModel || undefined },
        status: "running",
      }
      setCurrentRun(run)
    } catch (err) {
      toast.error(`Fehler: ${err instanceof Error ? err.message : String(err)}`)
      setAppState("idle")
    }
  }, [files, domain, framework, numVariants, maxRetries, ocrTool, llmProvider, llmModel])

  const handleStop = useCallback(() => {
    setAppState("idle")
    setActiveRunId(null)
    toast.info("Run gestoppt")
  }, [])

  const handleComplete = useCallback(
    (results: Record<string, unknown>) => {
      setAppState("done")
      if (!currentRun) return

      const updatedRun: RunResult = {
        ...currentRun,
        status: "complete",
        langchain: results.langchain as RunResult["langchain"],
        langgraph: results.langgraph as RunResult["langgraph"],
        hybrid: results.hybrid as RunResult["hybrid"],
        duration: Date.now() - new Date(currentRun.timestamp).getTime(),
      }
      setCurrentRun(updatedRun)

      // Persist to history
      const history = loadHistory()
      saveHistory([updatedRun, ...history])

      toast.success("Run abgeschlossen!")
    },
    [currentRun]
  )

  const canStart = appState === "idle" && files.length > 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Content Rewriting Demo</h1>
        <p className="text-gray-500 text-sm mt-1">
          LangChain · LangGraph · Hybrid – Master Thesis BFH
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Config */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-gray-700">1. PDF Upload</CardTitle>
            </CardHeader>
            <CardContent>
              <FileUpload files={files} onChange={setFiles} />
            </CardContent>
          </Card>

          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-gray-700">2. Domain</CardTitle>
            </CardHeader>
            <CardContent>
              <DomainSelector value={domain} onChange={setDomain} />
            </CardContent>
          </Card>

          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-gray-700">3. Framework</CardTitle>
            </CardHeader>
            <CardContent>
              <FrameworkSelector value={framework} onChange={setFramework} />
            </CardContent>
          </Card>

          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-gray-700">4. Konfiguration</CardTitle>
            </CardHeader>
            <CardContent>
              <ConfigPanel
                numVariants={numVariants}
                maxRetries={maxRetries}
                ocrTool={ocrTool}
                llmProvider={llmProvider}
                llmModel={llmModel}
                onVariantsChange={setNumVariants}
                onRetriesChange={setMaxRetries}
                onOcrToolChange={setOcrTool}
                onLlmProviderChange={setLlmProvider}
                onLlmModelChange={setLlmModel}
              />
            </CardContent>
          </Card>

          <div className="flex gap-2">
            <Button
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
              onClick={handleStart}
              disabled={!canStart}
            >
              <Play className="h-4 w-4 mr-2" />
              {appState === "uploading" ? "Uploading…" : "Start (Space)"}
            </Button>
            {appState === "running" && (
              <Button
                variant="outline"
                className="border-red-300 text-red-600 hover:bg-red-50"
                onClick={handleStop}
              >
                <Square className="h-4 w-4 mr-1" />
                Stop
              </Button>
            )}
          </div>

          <p className="text-xs text-gray-400 text-center">
            Space = Start/Stop · Esc = Stop
          </p>
        </div>

        {/* Right: Progress + Results */}
        <div className="lg:col-span-2 space-y-6">
          {activeRunId && (appState === "running" || appState === "done") && (
            <Card className="bg-white border-gray-200 shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-gray-700">Live Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <ProgressTracker
                  runId={activeRunId}
                  framework={framework}
                  onComplete={handleComplete}
                />
              </CardContent>
            </Card>
          )}

          {appState === "done" && currentRun && (currentRun.langchain || currentRun.langgraph || currentRun.hybrid) && (
            <>
              <Separator className="bg-gray-200" />
              <ComparisonView run={currentRun} />
            </>
          )}

          {appState === "idle" && !currentRun && (
            <div className="flex items-center justify-center h-48 border border-dashed border-gray-300 rounded-lg text-gray-400 text-sm">
              PDF hochladen und Run starten →
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
