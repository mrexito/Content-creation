"use client"

import type { RunResult } from "@/lib/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Trash2, ArrowRight, RefreshCw, CheckCircle, XCircle, Loader2 } from "lucide-react"
import Link from "next/link"

interface RunsTableProps {
  runs: RunResult[]
  onDelete: (id: string) => void
  onRerun: (run: RunResult) => void
}

const STATUS_ICONS = {
  complete: <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />,
  error: <XCircle className="h-3.5 w-3.5 text-red-400" />,
  running: <Loader2 className="h-3.5 w-3.5 text-blue-400 animate-spin" />,
  pending: <Loader2 className="h-3.5 w-3.5 text-slate-300" />,
}

const FRAMEWORK_COLORS: Record<string, string> = {
  both: "bg-purple-500/20 text-purple-300 border-purple-800",
  langchain: "bg-blue-500/20 text-blue-300 border-blue-800",
  langgraph: "bg-emerald-500/20 text-emerald-300 border-emerald-800",
}

export function RunsTable({ runs, onDelete, onRerun }: RunsTableProps) {
  if (!runs.length) {
    return (
      <div className="text-center py-16 text-slate-300">
        <p className="text-sm">Noch keine Runs. Starte einen Run auf der Hauptseite.</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {runs.map((run) => {
        const lc = run.langchain
        const lg = run.langgraph
        const validRate = lc?.metrics.validation_rate ?? lg?.metrics.validation_rate
        const totalTime = lc?.metrics.total_time ?? lg?.metrics.total_time

        return (
          <div
            key={run.id}
            className="flex items-center gap-4 bg-slate-600/40 rounded-lg px-4 py-3 border border-slate-600 hover:border-slate-500 transition-colors"
          >
            <div className="flex items-center gap-2 shrink-0">
              {STATUS_ICONS[run.status]}
            </div>

            <div className="flex-1 min-w-0 space-y-0.5">
              <p className="text-sm font-medium text-slate-200 truncate">{run.pdf_name}</p>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant="outline" className={`text-xs ${FRAMEWORK_COLORS[run.framework] ?? ""}`}>
                  {run.framework}
                </Badge>
                <Badge variant="outline" className="text-xs">{run.domain}</Badge>
                <span className="text-xs text-slate-300">
                  {new Date(run.timestamp).toLocaleString("de-CH")}
                </span>
              </div>
            </div>

            <div className="hidden sm:flex items-center gap-4 shrink-0 text-right">
              {totalTime !== undefined && (
                <div>
                  <p className="text-xs text-slate-300">Zeit</p>
                  <p className="text-sm font-mono text-slate-200">{totalTime.toFixed(1)}s</p>
                </div>
              )}
              {validRate !== undefined && (
                <div>
                  <p className="text-xs text-slate-300">Validierung</p>
                  <p className="text-sm font-mono text-slate-200">{(validRate * 100).toFixed(0)}%</p>
                </div>
              )}
            </div>

            <div className="flex items-center gap-1 shrink-0">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-slate-300 hover:text-slate-200"
                onClick={() => onRerun(run)}
                title="Erneut ausführen"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-slate-300 hover:text-red-400"
                onClick={() => onDelete(run.id)}
                title="Löschen"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
              {run.status === "complete" && (
                <Link href={`/results/${run.id}`}>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-300 hover:text-blue-400">
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
