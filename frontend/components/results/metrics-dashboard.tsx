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
}

function StatCard({ icon: Icon, label, value, sub, color = "text-blue-600" }: {
  icon: React.ElementType; label: string; value: string; sub?: string; color?: string
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

export function MetricsDashboard({ langchain, langgraph }: MetricsDashboardProps) {
  const timeData = [
    langchain && { name: "LangChain", time: +(langchain.metrics.total_time ?? 0).toFixed(2), fill: "#3b82f6" },
    langgraph && { name: "LangGraph", time: +(langgraph.metrics.total_time ?? 0).toFixed(2), fill: "#10b981" },
  ].filter(Boolean) as { name: string; time: number; fill: string }[]

  const validationData = [
    langchain && {
      name: "LangChain",
      valid: langchain.metrics.valid_variants,
      invalid: langchain.metrics.total_variants - langchain.metrics.valid_variants,
    },
    langgraph && {
      name: "LangGraph",
      valid: langgraph.metrics.valid_variants,
      invalid: langgraph.metrics.total_variants - langgraph.metrics.valid_variants,
    },
  ].filter(Boolean) as { name: string; valid: number; invalid: number }[]

  const active = langchain ?? langgraph
  if (!active) return null

  return (
    <div className="space-y-4">
      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard
          icon={Clock}
          label="Gesamtzeit"
          value={`${active.metrics.total_time.toFixed(1)}s`}
          sub={langchain && langgraph
            ? `LC: ${langchain.metrics.total_time.toFixed(1)}s · LG: ${langgraph.metrics.total_time.toFixed(1)}s`
            : undefined}
          color="text-blue-500"
        />
        <StatCard
          icon={Layers}
          label="Segmente"
          value={String(active.metrics.num_segments)}
          color="text-purple-500"
        />
        <StatCard
          icon={CheckCircle}
          label="Valide Varianten"
          value={`${active.metrics.valid_variants}/${active.metrics.total_variants}`}
          sub={langchain && langgraph
            ? `LC: ${langchain.metrics.valid_variants} · LG: ${langgraph.metrics.valid_variants}`
            : undefined}
          color="text-emerald-500"
        />
        <StatCard
          icon={Percent}
          label="Validierungsrate"
          value={`${(active.metrics.validation_rate * 100).toFixed(1)}%`}
          color="text-amber-500"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card className="bg-white border-gray-200 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold text-gray-700">Laufzeit (s)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={timeData}>
                <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 8, boxShadow: "0 2px 8px rgba(0,0,0,.08)" }}
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

        {validationData.length > 0 && (
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-gray-700">Valid vs. Invalid</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-around items-center">
              {validationData.map((d) => (
                <div key={d.name} className="flex flex-col items-center gap-1">
                  <span className="text-xs font-medium text-gray-500">{d.name}</span>
                  <PieChart width={100} height={100}>
                    <Pie
                      data={[{ value: d.valid }, { value: d.invalid }]}
                      cx={50} cy={50}
                      innerRadius={28} outerRadius={44}
                      dataKey="value" startAngle={90} endAngle={-270}
                    >
                      <Cell fill="#10b981" />
                      <Cell fill="#f87171" />
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 8 }}
                      itemStyle={{ color: "#6b7280" }}
                    />
                  </PieChart>
                  <span className="text-xs font-semibold text-emerald-600">{d.valid} valid</span>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
