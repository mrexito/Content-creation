"use client"

import { useState, useEffect } from "react"
import type { RunResult, Domain, Framework } from "@/lib/types"
import { RunsTable } from "@/components/history/runs-table"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { Search } from "lucide-react"

function loadHistory(): RunResult[] {
  if (typeof window === "undefined") return []
  try {
    return JSON.parse(localStorage.getItem("runs") ?? "[]")
  } catch {
    return []
  }
}

function saveHistory(runs: RunResult[]) {
  localStorage.setItem("runs", JSON.stringify(runs))
}

export default function HistoryPage() {
  const [runs, setRuns] = useState<RunResult[]>([])
  const [search, setSearch] = useState("")
  const router = useRouter()

  useEffect(() => {
    setRuns(loadHistory())
  }, [])

  const filtered = runs.filter((r) =>
    r.pdf_name.toLowerCase().includes(search.toLowerCase()) ||
    r.framework.includes(search) ||
    r.domain.includes(search)
  )

  const handleDelete = (id: string) => {
    const updated = runs.filter((r) => r.id !== id)
    setRuns(updated)
    saveHistory(updated)
    toast.success("Run gelöscht")
  }

  const handleRerun = (run: RunResult) => {
    // Store rerun config in sessionStorage, navigate to home
    sessionStorage.setItem("rerun", JSON.stringify({
      domain: run.domain as Domain,
      framework: run.framework as Framework,
      numVariants: run.config.numVariants,
      maxRetries: run.config.maxRetries,
    }))
    router.push("/")
    toast.info("Konfiguration übernommen – PDF neu hochladen")
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Run History</h1>
        <p className="text-gray-500 text-sm mt-1">{runs.length} gespeicherte Runs</p>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Suchen…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9 bg-white border-gray-300 text-gray-800 placeholder:text-gray-400 shadow-sm"
        />
      </div>

      <RunsTable runs={filtered} onDelete={handleDelete} onRerun={handleRerun} />
    </div>
  )
}
