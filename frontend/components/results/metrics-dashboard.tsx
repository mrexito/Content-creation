"use client"

import type { PipelineResult } from "@/lib/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts"
import { Clock, CheckCircle, Layers, Percent } from "lucide-react"

interface MetricsDashboardProps {
  langchain?: PipelineResult
  langgraph?: PipelineResult
  hybrid?: PipelineResult
}

function StatCard({ icon: Icon, label, value, sub, color = "text-blue-600" }: {
  icon: React.ElementType
  label: string
  value: string
  sub?: string
  color?: string
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm space-y-1">
      <div className="flex items-center gap-2 text-gray-500">
        <Icon className={`h-4 w-4 ${color}`} />
        <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400">{sub}</p>}
    </div>
  )
}

function DonutChart({ result, label, color }: {
  result: PipelineResult
  label: string
  color: string
}) {
  const valid = result.metrics?.valid_variants ?? 0
  const invalid = (result.metrics?.total_variants ?? 0) - valid
  const donutData = [
    { name: "Valide", value: valid || 0.001, fill: color },
    { name: "Ungültig", value: invalid || 0.001, fill: "#fee2e2" },
  ]
  return (
    <div className="flex flex-col items-center gap-1">
      <span className="text-xs font-medium text-gray-500">{label}</span>
      <PieChart width={120} height={120}>
        <Pie
          data={donutData}
          cx={55} cy={55}
          innerRadius={32} outerRadius={50}
          dataKey="value"
          startAngle={90} endAngle={-270}
          paddingAngle={2}
        >
          {donutData.map((entry, i) => (
            <Cell key={i} fill={entry.fill} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 8 }}
          itemStyle={{ color: "#6b7280" }}
        />
      </PieChart>
      <span className="text-xs font-semibold text-gray-700">{valid} valide</span>
    </div>
  )
}

/** Build "LC: x · LG: y · HY: z" sub-text safely (skips undefined values). */
function fwSubText(
  lc: string | undefined,
  lg: string | undefined,
  hy: string | undefined,
): string | undefined {
  const parts = [
    lc != null ? `LC: ${lc}` : null,
    lg != null ? `LG: ${lg}` : null,
    hy != null ? `HY: ${hy}` : null,
  ].filter((p): p is string => p !== null)
  return parts.length > 1 ? parts.join(" · ") : undefined
}

export function MetricsDashboard({ langchain, langgraph, hybrid }: MetricsDashboardProps) {
  const available = [langchain, langgraph, hybrid].filter(
    (r): r is PipelineResult => r !== undefined
  )
  if (!available.length) return null

  const hasMultiple = available.length > 1

  // Gesamtzeit: maximum across all frameworks (parallel run – user cares about wall clock)
  const times = available
    .map((r) => r.metrics?.total_time)
    .filter((t): t is number => t != null)
  const maxTime = times.length ? Math.max(...times) : 0

  // Segmente: from first available (same PDF → same segments)
  const numSegments = available[0].metrics?.num_segments ?? 0

  // Valide Varianten: sum across all frameworks
  const totalValid = available.reduce((s, r) => s + (r.metrics?.valid_variants ?? 0), 0)
  const totalVariants = available.reduce((s, r) => s + (r.metrics?.total_variants ?? 0), 0)

  // Validierungsrate: average across all frameworks
  const rates = available
    .map((r) => r.metrics?.validation_rate)
    .filter((v): v is number => v != null)
  const avgRate = rates.length ? rates.reduce((a, b) => a + b, 0) / rates.length : 0

  // Sub-texts (null-safe)
  const timeSub = hasMultiple
    ? fwSubText(
        langchain?.metrics?.total_time != null
          ? `${langchain.metrics.total_time.toFixed(1)}s` : undefined,
        langgraph?.metrics?.total_time != null
          ? `${langgraph.metrics.total_time.toFixed(1)}s` : undefined,
        hybrid?.metrics?.total_time != null
          ? `${hybrid.metrics.total_time.toFixed(1)}s` : undefined,
      )
    : undefined

  const validSub = hasMultiple
    ? fwSubText(
        langchain?.metrics != null
          ? `${langchain.metrics.valid_variants}/${langchain.metrics.total_variants}` : undefined,
        langgraph?.metrics != null
          ? `${langgraph.metrics.valid_variants}/${langgraph.metrics.total_variants}` : undefined,
        hybrid?.metrics != null
          ? `${hybrid.metrics.valid_variants}/${hybrid.metrics.total_variants}` : undefined,
      )
    : undefined

  const rateSub = hasMultiple
    ? fwSubText(
        langchain?.metrics?.validation_rate != null
          ? `${(langchain.metrics.validation_rate * 100).toFixed(1)}%` : undefined,
        langgraph?.metrics?.validation_rate != null
          ? `${(langgraph.metrics.validation_rate * 100).toFixed(1)}%` : undefined,
        hybrid?.metrics?.validation_rate != null
          ? `${(hybrid.metrics.validation_rate * 100).toFixed(1)}%` : undefined,
      )
    : undefined

  // Chart data: only include frameworks with real timing data
  const timeData = [
    langchain?.metrics?.total_time != null &&
      { name: "LangChain", time: +langchain.metrics.total_time.toFixed(2), fill: "#3b82f6" },
    langgraph?.metrics?.total_time != null &&
      { name: "LangGraph", time: +langgraph.metrics.total_time.toFixed(2), fill: "#10b981" },
    hybrid?.metrics?.total_time != null &&
      { name: "Hybrid",    time: +hybrid.metrics.total_time.toFixed(2),    fill: "#f59e0b" },
  ].filter((d): d is { name: string; time: number; fill: string } => Boolean(d))

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
              <CardTitle className="text-sm font-semibold text-gray-700">Laufzeit (s)</CardTitle>
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
            <CardTitle className="text-sm font-semibold text-gray-700">Valide vs. Ungültig</CardTitle>
          </CardHeader>
          <CardContent className="py-4">
            <div className="flex justify-around items-center">
              {langchain && <DonutChart result={langchain} label="LangChain" color="#3b82f6" />}
              {langgraph && <DonutChart result={langgraph} label="LangGraph" color="#10b981" />}
              {hybrid    && <DonutChart result={hybrid}    label="Hybrid"    color="#f59e0b" />}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
