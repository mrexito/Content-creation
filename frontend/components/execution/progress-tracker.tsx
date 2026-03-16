"use client"

import { useEffect, useState, useCallback, useMemo } from "react"
import type { ProgressState, Framework } from "@/lib/types"
import { Progress } from "@/components/ui/progress"
import { PhaseIndicator } from "./phase-indicator"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, XCircle, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface ProgressTrackerProps {
  runId: string
  framework: Framework
  onComplete?: (results: Record<string, unknown>) => void
}

const STATUS_STYLES = {
  running: "text-blue-600 border-blue-200 bg-blue-50",
  complete: "text-emerald-600 border-emerald-200 bg-emerald-50",
  error: "text-red-600 border-red-200 bg-red-50",
  pending: "text-gray-500 border-gray-200 bg-gray-50",
}

const FW_LABELS: Record<string, string> = {
  langchain:          "LangChain",
  langgraph:          "LangGraph",
  hybrid:             "Hybrid",
  agent_orchestrator: "Agent A (Orchestrator)",
  agent_multi:        "Agent B (Multi-Agent)",
  hybrid_agent:       "Hybrid+Agent",
}

const ALL_TRACKED_FRAMEWORKS = [
  "langchain", "langgraph", "hybrid",
  "agent_orchestrator", "agent_multi", "hybrid_agent",
] as const
type TrackedFramework = typeof ALL_TRACKED_FRAMEWORKS[number]

export function ProgressTracker({ runId, framework, onComplete }: ProgressTrackerProps) {
  const [progress, setProgress] = useState<Record<string, ProgressState>>({})
  const [done, setDone] = useState(false)

  const frameworks: TrackedFramework[] = useMemo(() => {
    if (framework === "all") return ["langchain", "langgraph", "hybrid"]
    if ((framework as string) === "both") return ["langchain", "langgraph"] // backwards compat
    if (ALL_TRACKED_FRAMEWORKS.includes(framework as TrackedFramework))
      return [framework as TrackedFramework]
    return ["langchain"]
  }, [framework])

  const poll = useCallback(async () => {
    try {
      const res = await fetch(`/api/progress/${runId}`)
      if (!res.ok) return
      const data = await res.json()
      setProgress(data)

      const allDone = frameworks.every(
        (fw) => data[fw]?.status === "complete" || data[fw]?.status === "error"
      )
      if (allDone && !done) {
        setDone(true)
        // Always call onComplete, even when some frameworks failed (no result.json)
        const rRes = await fetch(`/api/results/${runId}`)
        const results = rRes.ok ? await rRes.json() : {}
        onComplete?.(results)
      }
    } catch {}
  }, [runId, frameworks, onComplete, done])

  useEffect(() => {
    if (done) return
    poll()
    const interval = setInterval(poll, 500)
    return () => clearInterval(interval)
  }, [poll, done])

  return (
    <div className="space-y-3">
      {frameworks.map((fw) => {
        const p = progress[fw]
        const status = p?.status ?? "pending"
        return (
          <div key={fw} className="bg-white rounded-lg border border-gray-200 p-4 space-y-3 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-800">{FW_LABELS[fw] ?? fw}</span>
                <Badge
                  variant="outline"
                  className={`text-xs ${STATUS_STYLES[status as keyof typeof STATUS_STYLES] ?? ""}`}
                >
                  {status === "running" && <Loader2 className="h-3 w-3 mr-1 animate-spin" />}
                  {status === "complete" && <CheckCircle className="h-3 w-3 mr-1" />}
                  {status === "error" && <XCircle className="h-3 w-3 mr-1" />}
                  {status}
                </Badge>
              </div>
              <span className="text-sm font-medium text-gray-500">{p?.progress_percent ?? 0}%</span>
            </div>

            <Progress
              value={status === "error" ? 100 : (p?.progress_percent ?? 0)}
              className={cn(
                "h-1.5",
                status === "error" && "[&>div]:bg-red-400",
                status === "complete" && "[&>div]:bg-emerald-500",
                status === "running" && "[&>div]:bg-blue-500",
              )}
            />

            {p && (
              <PhaseIndicator
                currentPhase={p.current_phase}
                phasesCompleted={p.phases_completed ?? []}
              />
            )}

            {p?.metadata?.error && (
              <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded p-2 font-mono">
                {p.metadata.error}
              </p>
            )}
            {status === "error" && !p?.metadata?.error && (
              <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded p-2">
                Pipeline fehlgeschlagen.{" "}
                <a
                  href={`/api/logs/${runId}/${fw}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline hover:text-red-800"
                >
                  Logs anzeigen
                </a>
              </p>
            )}
            {status === "error" && (
              <div className="text-right">
                <a
                  href={`/api/logs/${runId}/${fw}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-gray-400 hover:text-gray-600 underline"
                >
                  run.log
                </a>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
