"use client"

import type { PipelineResult } from "@/lib/types"

interface ComparisonTableProps {
  langchain?: PipelineResult
  langgraph?: PipelineResult
  hybrid?: PipelineResult
}

const FW_COLORS: Record<string, { header: string }> = {
  langchain: { header: "text-blue-700 bg-blue-50" },
  langgraph: { header: "text-emerald-700 bg-emerald-50" },
  hybrid:    { header: "text-amber-700 bg-amber-50" },
}

interface RowValue {
  key: string
  raw: number | null
  display: string
}

interface Row {
  label: string
  values: RowValue[]
  bestIsLow: boolean
}

function getBestIdx(values: RowValue[], bestIsLow: boolean): number {
  const valid = values
    .map((v, i) => ({ i, raw: v.raw }))
    .filter((v) => v.raw !== null)
  if (!valid.length) return -1
  if (bestIsLow) return valid.reduce((a, b) => (a.raw! < b.raw! ? a : b)).i
  return valid.reduce((a, b) => (a.raw! > b.raw! ? a : b)).i
}

export function ComparisonTable({ langchain, langgraph, hybrid }: ComparisonTableProps) {
  const frameworks = [
    { key: "langchain", label: "LangChain", result: langchain },
    { key: "langgraph", label: "LangGraph", result: langgraph },
    { key: "hybrid",    label: "Hybrid",    result: hybrid    },
  ].filter((fw): fw is { key: string; label: string; result: PipelineResult } =>
    fw.result !== undefined
  )

  if (frameworks.length < 2) return null

  const rows: Row[] = [
    {
      label: "Laufzeit",
      values: frameworks.map((fw) => ({
        key: fw.key,
        raw: fw.result.metrics?.total_time ?? null,
        display: fw.result.metrics?.total_time != null
          ? `${fw.result.metrics.total_time.toFixed(1)}s` : "–",
      })),
      bestIsLow: true,
    },
    {
      label: "Segmente",
      values: frameworks.map((fw) => ({
        key: fw.key,
        raw: fw.result.metrics?.num_segments ?? null,
        display: fw.result.metrics?.num_segments != null
          ? String(fw.result.metrics.num_segments) : "–",
      })),
      bestIsLow: false,
    },
    {
      label: "Valide / Total",
      values: frameworks.map((fw) => ({
        key: fw.key,
        raw: fw.result.metrics?.valid_variants ?? null,
        display: fw.result.metrics != null
          ? `${fw.result.metrics.valid_variants}/${fw.result.metrics.total_variants}` : "–",
      })),
      bestIsLow: false,
    },
    {
      label: "Validierungsrate",
      values: frameworks.map((fw) => ({
        key: fw.key,
        raw: fw.result.metrics?.validation_rate ?? null,
        display: fw.result.metrics?.validation_rate != null
          ? `${(fw.result.metrics.validation_rate * 100).toFixed(1)}%` : "–",
      })),
      bestIsLow: false,
    },
  ]

  return (
    <div className="rounded-xl border border-gray-200 overflow-hidden shadow-sm">
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700">Framework-Vergleich</h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500 w-40">
              Metrik
            </th>
            {frameworks.map((fw) => (
              <th
                key={fw.key}
                className={`text-center px-4 py-2.5 text-xs font-semibold ${
                  FW_COLORS[fw.key]?.header ?? ""
                }`}
              >
                {fw.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => {
            const bestIdx = getBestIdx(row.values, row.bestIsLow)
            return (
              <tr key={ri} className={ri % 2 === 0 ? "bg-white" : "bg-gray-50/50"}>
                <td className="px-4 py-2.5 text-xs text-gray-500 font-medium">
                  {row.label}
                </td>
                {row.values.map((v, vi) => (
                  <td key={vi} className="text-center px-4 py-2.5">
                    <span
                      className={`font-mono text-sm ${
                        vi === bestIdx
                          ? "font-semibold text-gray-900"
                          : "text-gray-500"
                      }`}
                    >
                      {v.display}
                    </span>
                    {vi === bestIdx && v.raw !== null && (
                      <span className="ml-1 text-xs">🏆</span>
                    )}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
