"use client"

import { useState } from "react"
import type { PipelineResult } from "@/lib/types"
import { ChevronDown, ChevronRight, CheckCircle, XCircle } from "lucide-react"

interface SegmentComparisonProps {
  langchain?: PipelineResult
  langgraph?: PipelineResult
  hybrid?: PipelineResult
}

const FW_CONFIG = {
  langchain: {
    label: "LangChain",
    headerBg: "bg-blue-50",
    headerText: "text-blue-700",
    headerBorder: "border-blue-200",
    dot: "bg-blue-500",
  },
  langgraph: {
    label: "LangGraph",
    headerBg: "bg-emerald-50",
    headerText: "text-emerald-700",
    headerBorder: "border-emerald-200",
    dot: "bg-emerald-500",
  },
  hybrid: {
    label: "Hybrid",
    headerBg: "bg-amber-50",
    headerText: "text-amber-700",
    headerBorder: "border-amber-200",
    dot: "bg-amber-500",
  },
} as const

const NON_REWRITABLE_SEGMENT_TYPES = new Set(["title", "solution", "metadata"])

const SEGMENT_TYPE_LABELS: Record<string, string> = {
  title:    "Titel",
  solution: "Musterlösung",
  metadata: "Metadaten",
}

const DOMAIN_STYLES: Record<string, string> = {
  math: "bg-blue-100 text-blue-700",
  economics: "bg-amber-100 text-amber-700",
  languages: "bg-purple-100 text-purple-700",
  general: "bg-gray-100 text-gray-600",
}

export function SegmentComparison({ langchain, langgraph, hybrid }: SegmentComparisonProps) {
  const base = langchain ?? langgraph ?? hybrid
  const numSegments = base?.segments?.length ?? 0
  const [expanded, setExpanded] = useState<number | null>(0)

  if (!numSegments) {
    return (
      <p className="text-sm text-gray-400 italic text-center py-8">
        Keine Segmente verfügbar.
      </p>
    )
  }

  type FwKey = keyof typeof FW_CONFIG
  const activeFrameworks = (
    [
      { key: "langchain" as FwKey, result: langchain },
      { key: "langgraph" as FwKey, result: langgraph },
      { key: "hybrid"    as FwKey, result: hybrid    },
    ] as const
  ).filter((fw): fw is { key: FwKey; result: PipelineResult } =>
    fw.result !== undefined && (fw.result.segments?.length ?? 0) > 0
  )

  const colClass =
    activeFrameworks.length === 3
      ? "grid-cols-3"
      : activeFrameworks.length === 2
      ? "grid-cols-2"
      : "grid-cols-1"

  return (
    <div className="space-y-2">
      {Array.from({ length: numSegments }, (_, i) => {
        const isOpen = expanded === i

        const segData = activeFrameworks.map((fw) => ({
          key: fw.key,
          config: FW_CONFIG[fw.key],
          segment: fw.result.segments?.[i] ?? null,
        }))

        const domain =
          segData.find((s) => s.segment)?.segment?.classification?.domain ?? "general"

        const segmentType =
          segData.find((s) => s.segment)?.segment?.original_segment?.type ?? "unknown"
        const isSkipped = NON_REWRITABLE_SEGMENT_TYPES.has(segmentType)

        const summaries = segData.map((s) => {
          const seg = s.segment
          if (!seg) return { key: s.key, config: s.config, text: "–", hasData: false, allValid: false, noneValid: true }
          const valid = seg.validated_variants?.filter((v) => v.is_valid).length ?? 0
          const total = seg.validated_variants?.length ?? 0
          return {
            key: s.key,
            config: s.config,
            text: `${valid}/${total}`,
            hasData: true,
            allValid: valid === total && total > 0,
            noneValid: valid === 0,
          }
        })

        const originalText =
          segData.find((s) => s.segment)?.segment?.original_segment?.text ?? ""

        return (
          <div key={i} className="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            {/* Accordion header */}
            <button
              className="w-full flex items-center justify-between px-4 py-3
                bg-white hover:bg-gray-50 transition-colors text-left gap-3"
              onClick={() => setExpanded(isOpen ? null : i)}
            >
              <div className="flex items-center gap-3 min-w-0">
                {isOpen
                  ? <ChevronDown className="h-4 w-4 text-gray-400 shrink-0" />
                  : <ChevronRight className="h-4 w-4 text-gray-400 shrink-0" />}
                <span className="text-sm font-semibold text-gray-800 shrink-0">
                  Segment {i + 1}
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium shrink-0 ${
                    DOMAIN_STYLES[domain] ?? DOMAIN_STYLES.general
                  }`}
                >
                  {domain}
                </span>
                <div className="flex items-center gap-1.5 ml-1">
                  {isSkipped ? (
                    <span className="text-xs px-1.5 py-0.5 rounded font-medium bg-gray-100 text-gray-400 italic">
                      {SEGMENT_TYPE_LABELS[segmentType] ?? segmentType} – übersprungen
                    </span>
                  ) : (
                    summaries.map((s) => (
                      <span
                        key={s.key}
                        className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                          s.hasData
                            ? s.allValid
                              ? "bg-emerald-100 text-emerald-700"
                              : s.noneValid
                              ? "bg-red-100 text-red-600"
                              : "bg-amber-100 text-amber-700"
                            : "bg-gray-100 text-gray-400"
                        }`}
                      >
                        {s.config.label.replace("Lang", "")}:{s.text}
                      </span>
                    ))
                  )}
                </div>
              </div>
            </button>

            {isOpen && (
              <div className="border-t border-gray-200 bg-gray-50">
                {/* Original text */}
                <div className="px-4 py-3 border-b border-gray-200 bg-white">
                  <p className="text-xs font-semibold text-gray-400 mb-1.5 uppercase tracking-wider">
                    Originaltext
                  </p>
                  <div className="max-h-32 overflow-y-auto rounded bg-gray-50 border border-gray-100 px-3 py-2">
                    <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap font-mono">
                      {originalText || "Kein Originaltext verfügbar"}
                    </p>
                  </div>
                </div>

                {/* Skipped or framework columns */}
                {isSkipped ? (
                  <div className="px-4 py-5 text-center bg-gray-50">
                    <p className="text-xs text-gray-400 italic">
                      {SEGMENT_TYPE_LABELS[segmentType] ?? segmentType} — wird nicht umgeschrieben
                    </p>
                  </div>
                ) : null}

                {/* Framework columns */}
                {!isSkipped && (
                <div className={`grid gap-px bg-gray-200 ${colClass}`}>
                  {segData.map(({ key, config, segment }) => (
                    <div key={key} className="bg-white">
                      {/* Framework header */}
                      <div
                        className={`px-3 py-2 ${config.headerBg} border-b ${config.headerBorder}`}
                      >
                        <div className="flex items-center gap-1.5">
                          <span className={`w-2 h-2 rounded-full ${config.dot}`} />
                          <span className={`text-xs font-semibold ${config.headerText}`}>
                            {config.label}
                          </span>
                          {segment && (
                            <span className="ml-auto text-xs text-gray-500">
                              {segment.validated_variants?.filter((v) => v.is_valid).length ?? 0}
                              /{segment.validated_variants?.length ?? 0} valid
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Variants */}
                      <div className="p-3 space-y-2.5">
                        {!segment ? (
                          <div className="flex items-center justify-center h-20 text-gray-400
                            text-xs italic border border-dashed border-gray-200 rounded-lg">
                            Nicht verfügbar
                          </div>
                        ) : (
                          segment.validated_variants?.map((variant, vi) => (
                            <div
                              key={vi}
                              className={`rounded-lg border p-2.5 space-y-1.5 ${
                                variant.is_valid
                                  ? "border-emerald-200 bg-emerald-50/30"
                                  : "border-red-200 bg-red-50/30"
                              }`}
                            >
                              {/* Variant header */}
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <span className="text-xs text-gray-500 font-medium">
                                  Variante {vi + 1}
                                </span>
                                {variant.is_valid ? (
                                  <span className="flex items-center gap-0.5 text-xs text-emerald-700 font-medium">
                                    <CheckCircle className="h-3 w-3" />
                                    valide
                                  </span>
                                ) : (
                                  <span className="flex items-center gap-0.5 text-xs text-red-600 font-medium">
                                    <XCircle className="h-3 w-3" />
                                    ungültig
                                  </span>
                                )}
                                {variant.numbers_changed_pct != null && (
                                  <span
                                    className={`text-xs px-1 rounded ${
                                      variant.numbers_changed_pct >= 0.3
                                        ? "text-emerald-600 bg-emerald-50"
                                        : "text-amber-600 bg-amber-50"
                                    }`}
                                  >
                                    Δ{(variant.numbers_changed_pct * 100).toFixed(0)}%
                                  </span>
                                )}
                                {variant.diversity_score != null && (
                                  <span className="text-xs text-gray-400">
                                    div:{variant.diversity_score.toFixed(2)}
                                  </span>
                                )}
                              </div>

                              {/* Variant text */}
                              <div className="max-h-28 overflow-y-auto rounded bg-white border border-gray-100 px-2.5 py-1.5">
                                <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap font-mono">
                                  {variant.text || "—"}
                                </p>
                              </div>

                              {/* Validation issues */}
                              {!variant.is_valid &&
                                (variant.validation_issues?.length ?? 0) > 0 && (
                                  <ul className="text-xs text-red-600 space-y-0.5">
                                    {variant.validation_issues.slice(0, 2).map((issue, ii) => (
                                      <li key={ii} className="truncate">• {issue}</li>
                                    ))}
                                  </ul>
                                )}
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
