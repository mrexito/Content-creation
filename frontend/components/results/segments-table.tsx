"use client";

import { useState } from "react";
import type { PipelineResult } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { ChevronDown, ChevronRight, CheckCircle, XCircle } from "lucide-react";
import { MathText } from "./math-text";

const DOMAIN_STYLES: Record<string, string> = {
  math: "bg-blue-100 text-blue-700",
  languages: "bg-purple-100 text-purple-700",
  economics: "bg-amber-100 text-amber-700",
  general: "bg-gray-100 text-gray-600",
};

interface SegmentsTableProps {
  result: PipelineResult;
}

export function SegmentsTable({ result }: SegmentsTableProps) {
  const [expanded, setExpanded] = useState<number | null>(0);

  if (!result.segments?.length) {
    return <p className="text-gray-500 text-sm">Keine Segmente verfügbar.</p>;
  }

  return (
    <div className="space-y-2">
      {result.segments.map((seg, i) => {
        const isOpen = expanded === i;
        const domain = seg.classification?.domain ?? "general";
        const validCount =
          seg.validated_variants?.filter((v) => v.is_valid).length ?? 0;
        const totalCount = seg.validated_variants?.length ?? 0;

        return (
          <div
            key={i}
            className="border border-gray-200 rounded-lg overflow-hidden shadow-sm"
          >
            <button
              className="w-full flex items-center justify-between px-4 py-3 bg-white hover:bg-gray-50 transition-colors text-left"
              onClick={() => setExpanded(isOpen ? null : i)}
            >
              <div className="flex items-center gap-3 min-w-0">
                {isOpen ? (
                  <ChevronDown className="h-4 w-4 text-gray-400 shrink-0" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-gray-400 shrink-0" />
                )}
                <span className="text-sm font-semibold text-gray-800">
                  Segment {i + 1}
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium ${DOMAIN_STYLES[domain] ?? DOMAIN_STYLES.general}`}
                >
                  {domain}
                </span>
              </div>
              <span
                className={`text-xs font-medium shrink-0 ml-2 ${
                  validCount === totalCount
                    ? "text-emerald-600"
                    : "text-amber-600"
                }`}
              >
                {validCount}/{totalCount} valid
              </span>
            </button>

            {isOpen && (
              <div className="p-4 space-y-4 bg-gray-50 border-t border-gray-200">
                {/* Original */}
                <div>
                  <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
                    Original
                  </p>
                  <div className="max-h-40 overflow-y-auto rounded border border-gray-100 bg-white px-3 py-2">
                    <MathText
                      text={seg.original_segment?.text ?? ""}
                      emptyFallback="–"
                      className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap"
                    />
                  </div>
                </div>

                {/* Variants */}
                {seg.validated_variants?.map((variant, vi) => (
                  <div
                    key={vi}
                    className="border border-gray-200 rounded-lg p-3 bg-white space-y-2"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-500">
                        Variante {vi + 1}
                      </span>
                      {variant.is_valid ? (
                        <Badge className="text-xs bg-emerald-100 text-emerald-700 border-emerald-200 hover:bg-emerald-100">
                          <CheckCircle className="h-3 w-3 mr-1" /> Valid
                        </Badge>
                      ) : (
                        <Badge className="text-xs bg-red-100 text-red-600 border-red-200 hover:bg-red-100">
                          <XCircle className="h-3 w-3 mr-1" /> Invalid
                        </Badge>
                      )}
                      {variant.diversity_score !== undefined && (
                        <span className="text-xs text-gray-400">
                          Diversity: {variant.diversity_score.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <div className="max-h-48 overflow-y-auto rounded bg-gray-50 px-3 py-2">
                      <MathText
                        text={variant.text}
                        className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap"
                      />
                    </div>
                    {variant.validation_issues?.length > 0 && (
                      <ul className="text-xs text-red-600 space-y-0.5">
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
        );
      })}
    </div>
  );
}
