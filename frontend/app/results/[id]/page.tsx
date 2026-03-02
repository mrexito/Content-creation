"use client"

import { useEffect, useState } from "react"
import type { RunResult } from "@/lib/types"
import { ComparisonView } from "@/components/results/comparison-view"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { use } from "react"

interface PageProps {
  params: Promise<{ id: string }>
}

function loadRunFromHistory(id: string): RunResult | null {
  try {
    const runs: RunResult[] = JSON.parse(localStorage.getItem("runs") ?? "[]")
    return runs.find((r) => r.id === id) ?? null
  } catch {
    return null
  }
}

export default function ResultPage({ params }: PageProps) {
  const { id } = use(params)
  const [run, setRun] = useState<RunResult | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fromHistory = loadRunFromHistory(id)
    if (fromHistory) {
      setRun(fromHistory)
      setLoading(false)
      return
    }

    // Try fetching from API (if run is still in progress)
    fetch(`/api/results/${id}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.langchain || data.langgraph) {
          setRun({
            id,
            timestamp: new Date().toISOString(),
            pdf_name: data.langchain?.pdf_name ?? data.langgraph?.pdf_name ?? "unknown.pdf",
            domain: data.langchain?.domain ?? data.langgraph?.domain ?? "auto",
            framework: data.hybrid || (data.langchain && data.langgraph) ? "all" : data.langchain ? "langchain" : "langgraph",
            config: { numVariants: 2, maxRetries: 3 },
            status: "complete",
            langchain: data.langchain,
            langgraph: data.langgraph,
          })
        }
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-sm">
        Lade Ergebnisse…
      </div>
    )
  }

  if (!run) {
    return (
      <div className="space-y-4">
        <p className="text-gray-500">Run nicht gefunden: {id}</p>
        <Link href="/history">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück zur History
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Link href="/history">
        <Button variant="ghost" size="sm" className="text-gray-500 hover:text-gray-700 -ml-2">
          <ArrowLeft className="h-4 w-4 mr-2" />
          History
        </Button>
      </Link>
      <ComparisonView run={run} />
    </div>
  )
}
