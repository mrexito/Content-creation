"use client";

import type { PipelineResult } from "@/lib/types";
import type { ResultEntry } from "./comparison-view";
import { FW_CONFIG } from "./comparison-view";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Clock, CheckCircle, Layers, Percent } from "lucide-react";

interface MetricsDashboardProps {
  results: ResultEntry[];
}

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  color = "text-blue-600",
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  sub?: string;
  color?: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm space-y-1">
      <div className="flex items-center gap-2 text-gray-500">
        <Icon className={`h-4 w-4 ${color}`} />
        <span className="text-xs font-medium uppercase tracking-wide">
          {label}
        </span>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400">{sub}</p>}
    </div>
  );
}

function DonutChart({
  result,
  label,
  color,
}: {
  result: PipelineResult;
  label: string;
  color: string;
}) {
  const valid = result.metrics?.valid_variants ?? 0;
  const invalid = (result.metrics?.total_variants ?? 0) - valid;
  const donutData = [
    { name: "Valide", value: valid || 0.001, fill: color },
    { name: "Ungültig", value: invalid || 0.001, fill: "#fee2e2" },
  ];
  return (
    <div className="flex flex-col items-center gap-1">
      <span className="text-xs font-medium text-gray-500">{label}</span>
      <PieChart width={120} height={120}>
        <Pie
          data={donutData}
          cx={55}
          cy={55}
          innerRadius={32}
          outerRadius={50}
          dataKey="value"
          startAngle={90}
          endAngle={-270}
          paddingAngle={2}
        >
          {donutData.map((entry, i) => (
            <Cell key={i} fill={entry.fill} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: "#fff",
            border: "1px solid #e5e7eb",
            borderRadius: 8,
          }}
          itemStyle={{ color: "#6b7280" }}
        />
      </PieChart>
      <span className="text-xs font-semibold text-gray-700">
        {valid} valide
      </span>
    </div>
  );
}

export function MetricsDashboard({ results }: MetricsDashboardProps) {
  if (!results.length) return null;

  const hasMultiple = results.length > 1;

  const times = results
    .map((e) => e.result.metrics?.total_time)
    .filter((t): t is number => t != null);
  const maxTime = times.length ? Math.max(...times) : 0;

  const numSegments = results[0].result.metrics?.num_segments ?? 0;

  const totalValid = results.reduce(
    (s, e) => s + (e.result.metrics?.valid_variants ?? 0),
    0,
  );
  const totalVariants = results.reduce(
    (s, e) => s + (e.result.metrics?.total_variants ?? 0),
    0,
  );

  const rates = results
    .map((e) => e.result.metrics?.validation_rate)
    .filter((v): v is number => v != null);
  const avgRate = rates.length
    ? rates.reduce((a, b) => a + b, 0) / rates.length
    : 0;

  const timeSub = hasMultiple
    ? results
        .filter((e) => e.result.metrics?.total_time != null)
        .map((e) => {
          const cfg = FW_CONFIG[e.key];
          const abbr =
            cfg?.label.replace(/[^A-Z+]/g, "") ||
            e.key.slice(0, 2).toUpperCase();
          return `${abbr}: ${e.result.metrics!.total_time!.toFixed(1)}s`;
        })
        .join(" · ") || undefined
    : undefined;

  const validSub = hasMultiple
    ? results
        .filter((e) => e.result.metrics != null)
        .map((e) => {
          const cfg = FW_CONFIG[e.key];
          const abbr =
            cfg?.label.replace(/[^A-Z+]/g, "") ||
            e.key.slice(0, 2).toUpperCase();
          return `${abbr}: ${e.result.metrics!.valid_variants}/${e.result.metrics!.total_variants}`;
        })
        .join(" · ") || undefined
    : undefined;

  const rateSub = hasMultiple
    ? results
        .filter((e) => e.result.metrics?.validation_rate != null)
        .map((e) => {
          const cfg = FW_CONFIG[e.key];
          const abbr =
            cfg?.label.replace(/[^A-Z+]/g, "") ||
            e.key.slice(0, 2).toUpperCase();
          return `${abbr}: ${(e.result.metrics!.validation_rate! * 100).toFixed(1)}%`;
        })
        .join(" · ") || undefined
    : undefined;

  const timeData = results
    .filter((e) => e.result.metrics?.total_time != null)
    .map((e) => ({
      name: FW_CONFIG[e.key]?.label ?? e.key,
      time: +e.result.metrics!.total_time!.toFixed(2),
      fill: FW_CONFIG[e.key]?.color ?? "#6b7280",
    }));

  return (
    <div className="space-y-4">
      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard
          icon={Clock}
          label="Gesamtzeit"
          value={`${maxTime.toFixed(1)}s`}
          sub={timeSub}
          color="text-blue-500"
        />
        <StatCard
          icon={Layers}
          label="Segmente"
          value={String(numSegments)}
          color="text-purple-500"
        />
        <StatCard
          icon={CheckCircle}
          label="Valide Varianten"
          value={`${totalValid}/${totalVariants}`}
          sub={validSub}
          color="text-emerald-500"
        />
        <StatCard
          icon={Percent}
          label="Ø Validierungsrate"
          value={`${(avgRate * 100).toFixed(1)}%`}
          sub={rateSub}
          color="text-amber-500"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {timeData.length > 0 && (
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-gray-700">
                Laufzeit (s)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={timeData}>
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#6b7280", fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "#9ca3af", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#fff",
                      border: "1px solid #e5e7eb",
                      borderRadius: 8,
                      boxShadow: "0 2px 8px rgba(0,0,0,.08)",
                    }}
                    labelStyle={{ color: "#111827", fontWeight: 600 }}
                    itemStyle={{ color: "#6b7280" }}
                  />
                  <Bar dataKey="time" radius={[4, 4, 0, 0]}>
                    {timeData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        <Card className="bg-white border-gray-200 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold text-gray-700">
              Valide vs. Ungültig
            </CardTitle>
          </CardHeader>
          <CardContent className="py-4">
            <div className="flex justify-around items-center flex-wrap gap-2">
              {results.map(({ key, result }) => (
                <DonutChart
                  key={key}
                  result={result}
                  label={FW_CONFIG[key]?.label ?? key}
                  color={FW_CONFIG[key]?.color ?? "#6b7280"}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
