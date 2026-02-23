"use client"

import { useEffect, useState, useCallback } from "react"
import type { ProgressState, Framework } from "@/lib/types"
import { Progress } from "@/components/ui/progress"
import { PhaseIndicator } from "./phase-indicator"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, XCircle, Loader2 } from "lucide-react"

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

export function ProgressTracker({ runId, framework, onComplete }: ProgressTrackerProps) {
  const [progress, setProgress] = useState<Record<string, ProgressState>>({})
  const [done, setDone] = useState(false)

  const frameworks: Array<"langchain" | "langgraph"> =
    framework === "both" ? ["langchain", "langgraph"] : [framework]

  const poll = useCallback(async () => {
    try {
      const res = await fetch(`/api/progress/${runId}`)
      if (!res.ok) return
      const data = await res.json()
      setProgress(data)

      const allDone = frameworks.every(
        (fw) => data[fw]?.status === "complete" || data[fw]?.status === "error"
      )
      if (allDone) {
        setDone(true)
        const rRes = await fetch(`/api/results/${runId}`)
        if (rRes.ok) {
          const results = await rRes.json()
          onComplete?.(results)
        }
      }
    } catch {}
  }, [runId, frameworks, onComplete])

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
                <span className="font-semibold text-gray-800 capitalize">{fw}</span>
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

            <Progress value={p?.progress_percent ?? 0} className="h-1.5" />

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
          </div>
        )
      })}
    </div>
  )
}
