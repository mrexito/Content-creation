"use client"

import type { Framework } from "@/lib/types"
import { GitBranch, Workflow, Layers } from "lucide-react"

const options: { value: Framework; label: string; icon: React.ElementType; desc: string }[] = [
  { value: "langchain", label: "LangChain", icon: GitBranch, desc: "Chain-basiert" },
  { value: "langgraph", label: "LangGraph", icon: Workflow, desc: "State Machine" },
  { value: "both", label: "Beide", icon: Layers, desc: "Parallel Vergleich" },
]

const activeColors: Record<Framework, string> = {
  langchain: "border-blue-500 bg-blue-50 text-blue-700 shadow-sm",
  langgraph: "border-emerald-500 bg-emerald-50 text-emerald-700 shadow-sm",
  both: "border-purple-500 bg-purple-50 text-purple-700 shadow-sm",
}

interface FrameworkSelectorProps {
  value: Framework
  onChange: (f: Framework) => void
}

export function FrameworkSelector({ value, onChange }: FrameworkSelectorProps) {
  return (
    <div className="flex gap-2">
      {options.map(({ value: v, label, icon: Icon, desc }) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          className={`flex-1 flex flex-col items-center gap-1 py-3 px-2 rounded-lg border text-sm transition-all ${
            value === v
              ? activeColors[v]
              : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50"
          }`}
        >
          <Icon className="h-5 w-5" />
          <span className="font-semibold">{label}</span>
          <span className="text-xs opacity-70">{desc}</span>
        </button>
      ))}
    </div>
  )
}
