"use client"

import type { PipelineResult } from "@/lib/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts"
import { Clock, CheckCircle, Layers, Percent } from "lucide-react"

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]

interface MetricsDashboardProps {
  langchain?: PipelineResult
  langgraph?: PipelineResult
}

function StatCard({ icon: Icon, label, value, sub }: {
  icon: React.ElementType; label: string; value: string; sub?: string
}) {
  return (
    <div className="bg-slate-600/50 rounded-lg p-4 space-y-1">
      <div className="flex items-center gap-2 text-slate-400">
        <Icon className="h-4 w-4" />
        <span className="text-xs">{label}</span>
      </div>
      <p className="text-xl font-bold text-slate-100">{value}</p>
      {sub && <p className="text-xs text-slate-300">{sub}</p>}
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
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard
          icon={Clock}
          label="Gesamtzeit"
          value={`${active.metrics.total_time.toFixed(1)}s`}
          sub={langchain && langgraph
            ? `LC: ${langchain.metrics.total_time.toFixed(1)}s | LG: ${langgraph.metrics.total_time.toFixed(1)}s`
            : undefined}
        />
        <StatCard
          icon={Layers}
          label="Segmente"
          value={String(active.metrics.num_segments)}
        />
        <StatCard
          icon={CheckCircle}
          label="Valide Varianten"
          value={`${active.metrics.valid_variants}/${active.metrics.total_variants}`}
          sub={langchain && langgraph
            ? `LC: ${langchain.metrics.valid_variants} | LG: ${langgraph.metrics.valid_variants}`
            : undefined}
        />
        <StatCard
          icon={Percent}
          label="Validierungsrate"
          value={`${(active.metrics.validation_rate * 100).toFixed(1)}%`}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Time comparison bar chart */}
        <Card className="bg-slate-700 border-slate-600">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-slate-300">Laufzeit (s)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={timeData}>
                <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "#334155", border: "1px solid #475569", borderRadius: 6 }}
                  labelStyle={{ color: "#e2e8f0" }}
                  itemStyle={{ color: "#94a3b8" }}
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

        {/* Validation pie */}
        {validationData.length > 0 && (
          <Card className="bg-slate-700 border-slate-600">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-slate-300">Valid vs. Invalid</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-around">
              {validationData.map((d) => (
                <div key={d.name} className="flex flex-col items-center gap-1">
                  <span className="text-xs text-slate-400">{d.name}</span>
                  <PieChart width={100} height={100}>
                    <Pie
                      data={[{ value: d.valid }, { value: d.invalid }]}
                      cx={50} cy={50}
                      innerRadius={28} outerRadius={44}
                      dataKey="value" startAngle={90} endAngle={-270}
                    >
                      <Cell fill="#10b981" />
                      <Cell fill="#ef4444" />
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: "#334155", border: "1px solid #475569" }}
                      itemStyle={{ color: "#94a3b8" }}
                    />
                  </PieChart>
                  <span className="text-xs font-semibold text-emerald-400">{d.valid} valid</span>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
