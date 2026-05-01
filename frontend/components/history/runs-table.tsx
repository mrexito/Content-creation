"use client";

import type { RunResult } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Trash2,
  ArrowRight,
  RefreshCw,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";
import Link from "next/link";

interface RunsTableProps {
  runs: RunResult[];
  onDelete: (id: string) => void;
  onRerun: (run: RunResult) => void;
}

const STATUS_ICONS = {
  complete: <CheckCircle className="h-4 w-4 text-emerald-500" />,
  error: <XCircle className="h-4 w-4 text-red-400" />,
  running: <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />,
  pending: <Loader2 className="h-4 w-4 text-gray-400" />,
};

const FRAMEWORK_STYLES: Record<string, string> = {
  langchain: "bg-blue-100 text-blue-700 border-blue-200",
  langgraph: "bg-emerald-100 text-emerald-700 border-emerald-200",
  hybrid: "bg-amber-100 text-amber-700 border-amber-200",
  both: "bg-purple-100 text-purple-700 border-purple-200",
  all: "bg-violet-100 text-violet-700 border-violet-200",
};

const FRAMEWORK_LABELS: Record<string, string> = {
  langchain: "LangChain",
  langgraph: "LangGraph",
  hybrid: "Hybrid",
  both: "Beide",
  all: "Alle drei",
};

export function RunsTable({ runs, onDelete, onRerun }: RunsTableProps) {
  if (!runs.length) {
    return (
      <div className="text-center py-16 border border-dashed border-gray-300 rounded-lg">
        <p className="text-sm text-gray-500">
          Noch keine Runs. Starte einen Run auf der Hauptseite.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {runs.map((run) => {
        const lc = run.langchain;
        const lg = run.langgraph;
        const hy = run.hybrid;
        const validRate =
          lc?.metrics.validation_rate ??
          lg?.metrics.validation_rate ??
          hy?.metrics.validation_rate;
        const totalTime =
          lc?.metrics.total_time ??
          lg?.metrics.total_time ??
          hy?.metrics.total_time;

        return (
          <div
            key={run.id}
            className="flex items-center gap-4 bg-white rounded-lg px-4 py-3 border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center gap-2 shrink-0">
              {STATUS_ICONS[run.status]}
            </div>

            <div className="flex-1 min-w-0 space-y-0.5">
              <p className="text-sm font-semibold text-gray-800 truncate">
                {run.pdf_name}
              </p>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge
                  variant="outline"
                  className={`text-xs ${FRAMEWORK_STYLES[run.framework] ?? ""}`}
                >
                  {FRAMEWORK_LABELS[run.framework] ?? run.framework}
                </Badge>
                <Badge
                  variant="outline"
                  className="text-xs text-gray-500 border-gray-200"
                >
                  {run.domain}
                </Badge>
                <span className="text-xs text-gray-400">
                  {new Date(run.timestamp).toLocaleString("de-CH")}
                </span>
              </div>
            </div>

            <div className="hidden sm:flex items-center gap-6 shrink-0">
              {totalTime !== undefined && (
                <div className="text-right">
                  <p className="text-xs text-gray-400">Zeit</p>
                  <p className="text-sm font-semibold text-gray-700 tabular-nums">
                    {totalTime.toFixed(1)}s
                  </p>
                </div>
              )}
              {validRate !== undefined && (
                <div className="text-right">
                  <p className="text-xs text-gray-400">Validierung</p>
                  <p className="text-sm font-semibold text-gray-700 tabular-nums">
                    {(validRate * 100).toFixed(0)}%
                  </p>
                </div>
              )}
            </div>

            <div className="flex items-center gap-1 shrink-0">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-gray-400 hover:text-gray-700"
                onClick={() => onRerun(run)}
                title="Erneut ausführen"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-gray-400 hover:text-red-500"
                onClick={() => onDelete(run.id)}
                title="Löschen"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
              {run.status === "complete" && (
                <Link href={`/results/${run.id}`}>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-gray-400 hover:text-blue-600"
                  >
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
