"use client";

import { useState } from "react";
import type { RunResult, PipelineResult } from "@/lib/types";
import { MetricsDashboard } from "./metrics-dashboard";
import { ComparisonTable } from "./comparison-table";
import { SegmentComparison } from "./segment-comparison";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  CheckCircle,
  XCircle,
  Download,
  FileDown,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

interface ComparisonViewProps {
  run: RunResult;
}

// Zentrale Konfiguration für alle 6 Frameworks
export const FW_CONFIG: Record<
  string,
  {
    label: string;
    color: string;
    statusStyle: string;
    pdfTaskStyle: string;
    pdfSolStyle: string;
    headerBg: string;
    headerText: string;
    headerBorder: string;
    dot: string;
  }
> = {
  langchain: {
    label: "LangChain",
    color: "#3b82f6",
    statusStyle: "text-blue-700 border-blue-200 bg-blue-50",
    pdfTaskStyle:
      "border-blue-300 text-blue-600 hover:text-blue-800 hover:bg-blue-50",
    pdfSolStyle:
      "border-blue-200 text-blue-500 hover:text-blue-700 hover:bg-blue-50",
    headerBg: "bg-blue-50",
    headerText: "text-blue-700",
    headerBorder: "border-blue-200",
    dot: "bg-blue-500",
  },
  langgraph: {
    label: "LangGraph",
    color: "#10b981",
    statusStyle: "text-emerald-700 border-emerald-200 bg-emerald-50",
    pdfTaskStyle:
      "border-emerald-300 text-emerald-600 hover:text-emerald-800 hover:bg-emerald-50",
    pdfSolStyle:
      "border-emerald-200 text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50",
    headerBg: "bg-emerald-50",
    headerText: "text-emerald-700",
    headerBorder: "border-emerald-200",
    dot: "bg-emerald-500",
  },
  hybrid: {
    label: "Hybrid",
    color: "#f59e0b",
    statusStyle: "text-amber-700 border-amber-200 bg-amber-50",
    pdfTaskStyle:
      "border-amber-300 text-amber-600 hover:text-amber-800 hover:bg-amber-50",
    pdfSolStyle:
      "border-amber-200 text-amber-500 hover:text-amber-700 hover:bg-amber-50",
    headerBg: "bg-amber-50",
    headerText: "text-amber-700",
    headerBorder: "border-amber-200",
    dot: "bg-amber-500",
  },
  agent_orchestrator: {
    label: "Agent A",
    color: "#f43f5e",
    statusStyle: "text-rose-700 border-rose-200 bg-rose-50",
    pdfTaskStyle:
      "border-rose-300 text-rose-600 hover:text-rose-800 hover:bg-rose-50",
    pdfSolStyle:
      "border-rose-200 text-rose-500 hover:text-rose-700 hover:bg-rose-50",
    headerBg: "bg-rose-50",
    headerText: "text-rose-700",
    headerBorder: "border-rose-200",
    dot: "bg-rose-500",
  },
  agent_multi: {
    label: "Agent B",
    color: "#f97316",
    statusStyle: "text-orange-700 border-orange-200 bg-orange-50",
    pdfTaskStyle:
      "border-orange-300 text-orange-600 hover:text-orange-800 hover:bg-orange-50",
    pdfSolStyle:
      "border-orange-200 text-orange-500 hover:text-orange-700 hover:bg-orange-50",
    headerBg: "bg-orange-50",
    headerText: "text-orange-700",
    headerBorder: "border-orange-200",
    dot: "bg-orange-500",
  },
  hybrid_agent: {
    label: "Hybrid+Agent",
    color: "#14b8a6",
    statusStyle: "text-teal-700 border-teal-200 bg-teal-50",
    pdfTaskStyle:
      "border-teal-300 text-teal-600 hover:text-teal-800 hover:bg-teal-50",
    pdfSolStyle:
      "border-teal-200 text-teal-500 hover:text-teal-700 hover:bg-teal-50",
    headerBg: "bg-teal-50",
    headerText: "text-teal-700",
    headerBorder: "border-teal-200",
    dot: "bg-teal-500",
  },
};

export type ResultEntry = { key: string; result: PipelineResult };

function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function downloadPdf(runId: string, framework: string, filename: string) {
  const url = `/api/download/${runId}/${framework}/${filename}`;
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
}

function JsonAccordion({
  result,
  fwKey,
}: {
  result: PipelineResult;
  fwKey: string;
}) {
  const [open, setOpen] = useState(false);
  const label = FW_CONFIG[fwKey]?.label ?? fwKey;
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-4 py-3 bg-gray-50
          hover:bg-gray-100 transition-colors text-left"
      >
        {open ? (
          <ChevronDown className="h-4 w-4 text-gray-400 shrink-0" />
        ) : (
          <ChevronRight className="h-4 w-4 text-gray-400 shrink-0" />
        )}
        <span className="text-sm font-medium text-gray-700">
          {label} – result.json
        </span>
        <span
          role="button"
          tabIndex={0}
          onClick={(e) => {
            e.stopPropagation();
            downloadJson(result, `${fwKey}_result.json`);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.stopPropagation();
              downloadJson(result, `${fwKey}_result.json`);
            }
          }}
          className="ml-auto text-xs text-gray-400 hover:text-gray-700 flex items-center gap-1 cursor-pointer"
        >
          <Download className="h-3 w-3" />
          Download
        </span>
      </button>
      {open && (
        <div className="border-t border-gray-200 bg-white p-4 max-h-96 overflow-auto">
          <pre className="text-xs text-gray-600 font-mono leading-relaxed">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export function ComparisonView({ run }: ComparisonViewProps) {
  // Alle 6 Frameworks einlesen
  const ALL_FW_KEYS = [
    "langchain",
    "langgraph",
    "hybrid",
    "agent_orchestrator",
    "agent_multi",
    "hybrid_agent",
  ] as const;

  const resultEntries: ResultEntry[] = ALL_FW_KEYS.flatMap((key) => {
    const result = run[key as keyof RunResult] as PipelineResult | undefined;
    return result ? [{ key, result } satisfies ResultEntry] : [];
  });

  if (!resultEntries.length) {
    return <p className="text-gray-500">Keine Ergebnisse verfügbar.</p>;
  }

  const hasMultiple = resultEntries.length > 1;
  const numSegments = resultEntries[0]?.result?.segments?.length ?? 0;

  return (
    <div className="space-y-6">
      {/* ── [1] Header ─────────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div className="space-y-1.5">
          <h2 className="text-lg font-bold text-gray-900">
            {run.pdf_name}
            {hasMultiple && (
              <span className="ml-2 text-sm font-medium text-violet-600">
                · {resultEntries.length}-fach-Vergleich
              </span>
            )}
          </h2>
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="text-xs text-gray-600">
              {run.domain}
            </Badge>
            {resultEntries.map(({ key, result }) => {
              const cfg = FW_CONFIG[key];
              return (
                <Badge
                  key={key}
                  variant="outline"
                  className={`text-xs flex items-center gap-1 ${
                    result.success
                      ? "text-emerald-600 border-emerald-200 bg-emerald-50"
                      : "text-red-600 border-red-200 bg-red-50"
                  }`}
                >
                  {result.success ? (
                    <CheckCircle className="h-3 w-3" />
                  ) : (
                    <XCircle className="h-3 w-3" />
                  )}
                  {cfg?.label ?? key}
                </Badge>
              );
            })}
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
              {resultEntries.map(({ key, result }) => {
                const cfg = FW_CONFIG[key];
                return result.pdf_files ? (
                  <div key={key} className="flex items-center gap-1">
                    <span
                      className={`text-xs font-medium px-1.5 py-0.5 rounded border
                        ${cfg?.statusStyle ?? "text-gray-600 bg-gray-100 border-gray-200"}`}
                    >
                      {cfg?.label ?? key}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadPdf(run.id, key, "tasks.pdf")}
                      className={cfg?.pdfTaskStyle ?? ""}
                    >
                      <FileDown className="h-3.5 w-3.5 mr-1" />
                      Aufgaben
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadPdf(run.id, key, "solutions.pdf")}
                      className={cfg?.pdfSolStyle ?? ""}
                    >
                      <FileDown className="h-3.5 w-3.5 mr-1" />
                      Lösungen
                    </Button>
                  </div>
                ) : null;
              })}
            </div>
          )}
        </div>
      </div>

      {/* ── [2] StatCards + Diagramme ──────────────────────────────────────── */}
      <MetricsDashboard results={resultEntries} />

      {/* ── [3] Framework-Vergleichstabelle (nur bei mehreren Frameworks) ──── */}
      {hasMultiple && <ComparisonTable results={resultEntries} />}

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
        <SegmentComparison results={resultEntries} />
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
  );
}
