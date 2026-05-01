"use client";

import type { ResultEntry } from "./comparison-view";
import { FW_CONFIG } from "./comparison-view";

interface ComparisonTableProps {
  results: ResultEntry[];
}

interface RowValue {
  key: string;
  raw: number | null;
  display: string;
}

interface Row {
  label: string;
  values: RowValue[];
  bestIsLow: boolean;
}

function getBestIdx(values: RowValue[], bestIsLow: boolean): number {
  const valid = values
    .map((v, i) => ({ i, raw: v.raw }))
    .filter((v) => v.raw !== null);
  if (!valid.length) return -1;
  if (bestIsLow) return valid.reduce((a, b) => (a.raw! < b.raw! ? a : b)).i;
  return valid.reduce((a, b) => (a.raw! > b.raw! ? a : b)).i;
}

export function ComparisonTable({ results }: ComparisonTableProps) {
  if (results.length < 2) return null;

  const rows: Row[] = [
    {
      label: "Laufzeit",
      values: results.map((e) => ({
        key: e.key,
        raw: e.result.metrics?.total_time ?? null,
        display:
          e.result.metrics?.total_time != null
            ? `${e.result.metrics.total_time.toFixed(1)}s`
            : "–",
      })),
      bestIsLow: true,
    },
    {
      label: "Segmente",
      values: results.map((e) => ({
        key: e.key,
        raw: e.result.metrics?.num_segments ?? null,
        display:
          e.result.metrics?.num_segments != null
            ? String(e.result.metrics.num_segments)
            : "–",
      })),
      bestIsLow: false,
    },
    {
      label: "Valide / Total",
      values: results.map((e) => ({
        key: e.key,
        raw: e.result.metrics?.valid_variants ?? null,
        display:
          e.result.metrics != null
            ? `${e.result.metrics.valid_variants}/${e.result.metrics.total_variants}`
            : "–",
      })),
      bestIsLow: false,
    },
    {
      label: "Validierungsrate",
      values: results.map((e) => ({
        key: e.key,
        raw: e.result.metrics?.validation_rate ?? null,
        display:
          e.result.metrics?.validation_rate != null
            ? `${(e.result.metrics.validation_rate * 100).toFixed(1)}%`
            : "–",
      })),
      bestIsLow: false,
    },
  ];

  return (
    <div className="rounded-xl border border-gray-200 overflow-hidden shadow-sm">
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700">
          Framework-Vergleich
        </h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500 w-40">
              Metrik
            </th>
            {results.map((e) => {
              const cfg = FW_CONFIG[e.key];
              return (
                <th
                  key={e.key}
                  className={`text-center px-4 py-2.5 text-xs font-semibold ${
                    cfg
                      ? `${cfg.headerText} ${cfg.headerBg}`
                      : "text-gray-700 bg-gray-50"
                  }`}
                >
                  {cfg?.label ?? e.key}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => {
            const bestIdx = getBestIdx(row.values, row.bestIsLow);
            return (
              <tr
                key={ri}
                className={ri % 2 === 0 ? "bg-white" : "bg-gray-50/50"}
              >
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
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
