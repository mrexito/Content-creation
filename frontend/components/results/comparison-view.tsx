"use client"

import { useState } from "react"
import type { RunResult, PipelineResult } from "@/lib/types"
import { MetricsDashboard } from "./metrics-dashboard"
import { ComparisonTable } from "./comparison-table"
import { SegmentComparison } from "./segment-comparison"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { CheckCircle, XCircle, Download, FileDown, ChevronDown, ChevronRight } from "lucide-react"

interface ComparisonViewProps {
  run: RunResult
}

function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function downloadPdf(runId: string, framework: string, filename: string) {
  const url = `/api/download/${runId}/${framework}/${filename}`
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
}

const FW_STATUS_STYLE: Record<string, string> = {
  langchain: "text-blue-700 border-blue-200 bg-blue-50",
  langgraph: "text-emerald-700 border-emerald-200 bg-emerald-50",
  hybrid:    "text-amber-700 border-amber-200 bg-amber-50",
}
const FW_LABEL: Record<string, string> = {
  langchain: "LangChain",
  langgraph: "LangGraph",
  hybrid:    "Hybrid",
}
const FW_PDF_COLORS: Record<string, { tasks: string; solutions: string }> = {
  langchain: {
    tasks:     "border-blue-300 text-blue-600 hover:text-blue-800 hover:bg-blue-50",
    solutions: "border-blue-200 text-blue-500 hover:text-blue-700 hover:bg-blue-50",
  },
  langgraph: {
    tasks:     "border-emerald-300 text-emerald-600 hover:text-emerald-800 hover:bg-emerald-50",
    solutions: "border-emerald-200 text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50",
  },
  hybrid: {
    tasks:     "border-amber-300 text-amber-600 hover:text-amber-800 hover:bg-amber-50",
    solutions: "border-amber-200 text-amber-500 hover:text-amber-700 hover:bg-amber-50",
  },
}

function JsonAccordion({ result, fwKey }: { result: PipelineResult; fwKey: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-4 py-3 bg-gray-50
          hover:bg-gray-100 transition-colors text-left"
      >
        {open
          ? <ChevronDown className="h-4 w-4 text-gray-400 shrink-0" />
          : <ChevronRight className="h-4 w-4 text-gray-400 shrink-0" />}
        <span className="text-sm font-medium text-gray-700">
          {FW_LABEL[fwKey] ?? fwKey} – result.json
        </span>
        <button
          onClick={(e) => {
            e.stopPropagation()
            downloadJson(result, `${fwKey}_result.json`)
          }}
          className="ml-auto text-xs text-gray-400 hover:text-gray-700 flex items-center gap-1"
        >
          <Download className="h-3 w-3" />
          Download
        </button>
      </button>
      {open && (
        <div className="border-t border-gray-200 bg-white p-4 max-h-96 overflow-auto">
          <pre className="text-xs text-gray-600 font-mono leading-relaxed">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export function ComparisonView({ run }: ComparisonViewProps) {
  const { langchain, langgraph, hybrid } = run

  const resultEntries: { key: string; result: PipelineResult }[] = [
    langchain && { key: "langchain", result: langchain },
    langgraph && { key: "langgraph", result: langgraph },
    hybrid    && { key: "hybrid",    result: hybrid    },
  ].filter((x): x is { key: string; result: PipelineResult } => Boolean(x))

  if (!resultEntries.length) {
    return <p className="text-gray-500">Keine Ergebnisse verfügbar.</p>
  }

  const hasMultiple = resultEntries.length > 1
  const numSegments = (langchain ?? langgraph ?? hybrid)?.segments?.length ?? 0

  return (
    <div className="space-y-6">

      {/* ── [1] Header ─────────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div className="space-y-1.5">
          <h2 className="text-lg font-bold text-gray-900">
            {run.pdf_name}
            {hasMultiple && (
              <span className="ml-2 text-sm font-medium text-violet-600">
                · Dreifach-Vergleich
              </span>
            )}
          </h2>
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="text-xs text-gray-600">{run.domain}</Badge>
            {resultEntries.map(({ key, result }) => (
              <Badge
                key={key}
                variant="outline"
                className={`text-xs flex items-center gap-1 ${
                  result.success
                    ? "text-emerald-600 border-emerald-200 bg-emerald-50"
                    : "text-red-600 border-red-200 bg-red-50"
                }`}
              >
                {result.success
                  ? <CheckCircle className="h-3 w-3" />
                  : <XCircle className="h-3 w-3" />}
                {FW_LABEL[key] ?? key}
              </Badge>
            ))}
            <span className="text-xs text-gray-400">
              {new Date(run.timestamp).toLocaleString("de-CH")}
            </span>
          </div>
        </div>

        {/* Export + PDF downloads */}
        <div className="flex flex-col items-end gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => downloadJson(run, `${run.id}.json`)}
            className="border-gray-300 text-gray-600 hover:text-gray-900 hover:bg-gray-50"
          >
            <Download className="h-4 w-4 mr-1.5" />
            Export JSON
          </Button>

          {resultEntries.some((e) => e.result.pdf_files) && (
            <div className="flex flex-wrap justify-end gap-1.5">
              {resultEntries.map(({ key, result }) =>
                result.pdf_files ? (
                  <div key={key} className="flex items-center gap-1">
                    <span
                      className={`text-xs font-medium px-1.5 py-0.5 rounded border
                        ${FW_STATUS_STYLE[key] ?? "text-gray-600 bg-gray-100 border-gray-200"}`}
                    >
                      {FW_LABEL[key] ?? key}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadPdf(run.id, key, "tasks.pdf")}
                      className={FW_PDF_COLORS[key]?.tasks ?? ""}
                    >
                      <FileDown className="h-3.5 w-3.5 mr-1" />
                      Aufgaben
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadPdf(run.id, key, "solutions.pdf")}
                      className={FW_PDF_COLORS[key]?.solutions ?? ""}
                    >
                      <FileDown className="h-3.5 w-3.5 mr-1" />
                      Lösungen
                    </Button>
                  </div>
                ) : null
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── [2] StatCards + Diagramme ──────────────────────────────────────── */}
      <MetricsDashboard langchain={langchain} langgraph={langgraph} hybrid={hybrid} />

      {/* ── [3] Framework-Vergleichstabelle ────────────────────────────────── */}
      {hasMultiple && (
        <ComparisonTable langchain={langchain} langgraph={langgraph} hybrid={hybrid} />
      )}

      {/* ── [4] Segment-für-Segment Vergleich ─────────────────────────────── */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          Segment-Vergleich
          {numSegments > 0 && (
            <span className="ml-2 text-xs font-normal text-gray-400">
              ({numSegments} Segment{numSegments !== 1 ? "e" : ""})
            </span>
          )}
        </h3>
        <SegmentComparison langchain={langchain} langgraph={langgraph} hybrid={hybrid} />
      </div>

      {/* ── [5] Rohdaten ──────────────────────────────────────────────────── */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Rohdaten</h3>
        <div className="space-y-2">
          {resultEntries.map(({ key, result }) => (
            <JsonAccordion key={key} result={result} fwKey={key} />
          ))}
        </div>
      </div>
    </div>
  )
}
