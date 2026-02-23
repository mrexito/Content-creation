"use client"

import { useState } from "react"
import type { PipelineResult } from "@/lib/types"
import { Badge } from "@/components/ui/badge"
import { ChevronDown, ChevronRight, CheckCircle, XCircle } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

const DOMAIN_COLOR: Record<string, string> = {
  math: "bg-blue-500/20 text-blue-300",
  languages: "bg-purple-500/20 text-purple-300",
  economics: "bg-amber-500/20 text-amber-300",
  general: "bg-slate-500 text-slate-200",
}

interface SegmentsTableProps {
  result: PipelineResult
}

export function SegmentsTable({ result }: SegmentsTableProps) {
  const [expanded, setExpanded] = useState<number | null>(0)

  if (!result.segments?.length) {
    return <p className="text-slate-300 text-sm">Keine Segmente verfügbar.</p>
  }

  return (
    <div className="space-y-2">
      {result.segments.map((seg, i) => {
        const isOpen = expanded === i
        const domain = seg.classification?.domain ?? "general"
        const validCount = seg.validated_variants?.filter((v) => v.is_valid).length ?? 0
        const totalCount = seg.validated_variants?.length ?? 0

        return (
          <div key={i} className="border border-slate-600 rounded-lg overflow-hidden">
            <button
              className="w-full flex items-center justify-between px-4 py-3 bg-slate-600/40 hover:bg-slate-600/70 transition-colors text-left"
              onClick={() => setExpanded(isOpen ? null : i)}
            >
              <div className="flex items-center gap-3 min-w-0">
                {isOpen ? <ChevronDown className="h-4 w-4 text-slate-400 shrink-0" /> : <ChevronRight className="h-4 w-4 text-slate-400 shrink-0" />}
                <span className="text-sm font-medium text-slate-200">Segment {i + 1}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${DOMAIN_COLOR[domain] ?? DOMAIN_COLOR.general}`}>
                  {domain}
                </span>
              </div>
              <span className="text-xs text-slate-400 shrink-0 ml-2">
                {validCount}/{totalCount} valid
              </span>
            </button>

            {isOpen && (
              <div className="p-4 space-y-4 bg-slate-700/40">
                {/* Original */}
                <div>
                  <p className="text-xs text-slate-300 mb-1 uppercase tracking-wide">Original</p>
                  <ScrollArea className="max-h-32">
                    <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                      {seg.original_segment?.text ?? "–"}
                    </p>
                  </ScrollArea>
                </div>

                {/* Variants */}
                {seg.validated_variants?.map((variant, vi) => (
                  <div key={vi} className="border border-slate-600 rounded p-3 space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-300">Variante {vi + 1}</span>
                      {variant.is_valid ? (
                        <Badge className="text-xs bg-emerald-500/20 text-emerald-300 border-emerald-800">
                          <CheckCircle className="h-3 w-3 mr-1" /> Valid
                        </Badge>
                      ) : (
                        <Badge className="text-xs bg-red-500/20 text-red-300 border-red-800">
                          <XCircle className="h-3 w-3 mr-1" /> Invalid
                        </Badge>
                      )}
                      {variant.diversity_score !== undefined && (
                        <span className="text-xs text-slate-300">
                          Diversity: {variant.diversity_score.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <ScrollArea className="max-h-32">
                      <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                        {variant.text}
                      </p>
                    </ScrollArea>
                    {variant.validation_issues?.length > 0 && (
                      <ul className="text-xs text-red-400 space-y-0.5">
                        {variant.validation_issues.map((issue, ii) => (
                          <li key={ii}>• {issue}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
