"use client"

import type { RunResult } from "@/lib/types"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MetricsDashboard } from "./metrics-dashboard"
import { SegmentsTable } from "./segments-table"
import { JsonViewer } from "./json-viewer"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, XCircle, Download } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ComparisonViewProps {
  run: RunResult
}

function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function ComparisonView({ run }: ComparisonViewProps) {
  const { langchain, langgraph } = run
  const hasBoth = langchain && langgraph
  const active = langchain ?? langgraph

  if (!active) return <p className="text-gray-500">Keine Ergebnisse verfügbar.</p>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="space-y-1">
          <h2 className="text-lg font-bold text-gray-900">{run.pdf_name}</h2>
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="text-xs text-gray-600">{run.domain}</Badge>
            <Badge variant="outline" className="text-xs text-gray-600">{run.framework}</Badge>
            <span className="text-xs text-gray-400">{new Date(run.timestamp).toLocaleString("de-CH")}</span>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => downloadJson(run, `${run.id}.json`)}
          className="border-gray-300 text-gray-600 hover:text-gray-900 hover:bg-gray-50"
        >
          <Download className="h-4 w-4 mr-1.5" />
          Export JSON
        </Button>
      </div>

      {/* Metrics */}
      <MetricsDashboard langchain={langchain} langgraph={langgraph} />

      {/* Detail tabs */}
      {hasBoth ? (
        <Tabs defaultValue="langchain">
          <TabsList className="bg-gray-100 border border-gray-200">
            <TabsTrigger value="langchain" className="data-[state=active]:bg-white data-[state=active]:shadow-sm">
              LangChain
              {langchain.success
                ? <CheckCircle className="h-3 w-3 ml-1.5 text-emerald-500" />
                : <XCircle className="h-3 w-3 ml-1.5 text-red-500" />}
            </TabsTrigger>
            <TabsTrigger value="langgraph" className="data-[state=active]:bg-white data-[state=active]:shadow-sm">
              LangGraph
              {langgraph.success
                ? <CheckCircle className="h-3 w-3 ml-1.5 text-emerald-500" />
                : <XCircle className="h-3 w-3 ml-1.5 text-red-500" />}
            </TabsTrigger>
            <TabsTrigger value="json" className="data-[state=active]:bg-white data-[state=active]:shadow-sm">JSON</TabsTrigger>
          </TabsList>
          <TabsContent value="langchain" className="mt-4">
            <SegmentsTable result={langchain} />
          </TabsContent>
          <TabsContent value="langgraph" className="mt-4">
            <SegmentsTable result={langgraph} />
          </TabsContent>
          <TabsContent value="json" className="mt-4 grid sm:grid-cols-2 gap-4">
            <JsonViewer data={langchain} title="langchain_result.json" />
            <JsonViewer data={langgraph} title="langgraph_result.json" />
          </TabsContent>
        </Tabs>
      ) : (
        <Tabs defaultValue="segments">
          <TabsList className="bg-gray-100 border border-gray-200">
            <TabsTrigger value="segments" className="data-[state=active]:bg-white data-[state=active]:shadow-sm">Segmente</TabsTrigger>
            <TabsTrigger value="json" className="data-[state=active]:bg-white data-[state=active]:shadow-sm">JSON</TabsTrigger>
          </TabsList>
          <TabsContent value="segments" className="mt-4">
            <SegmentsTable result={active} />
          </TabsContent>
          <TabsContent value="json" className="mt-4">
            <JsonViewer data={active} title="result.json" />
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
