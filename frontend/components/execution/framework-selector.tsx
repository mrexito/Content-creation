"use client"

import type { Framework } from "@/lib/types"
import { GitBranch, Workflow, GitMerge, LayoutGrid } from "lucide-react"

const options: {
  value: Framework; label: string
  icon: React.ElementType; desc: string
}[] = [
  { value: "langchain", label: "LangChain", icon: GitBranch,  desc: "Chain-basiert"       },
  { value: "langgraph", label: "LangGraph", icon: Workflow,   desc: "State Machine"        },
  { value: "hybrid",    label: "Hybrid",    icon: GitMerge,   desc: "LC + LG kombiniert"   },
  { value: "all",       label: "Alle drei", icon: LayoutGrid, desc: "Vollvergleich"         },
]

const activeColors: Record<Framework, string> = {
  langchain: "border-blue-500 bg-blue-50 text-blue-700 shadow-sm",
  langgraph: "border-emerald-500 bg-emerald-50 text-emerald-700 shadow-sm",
  hybrid:    "border-amber-500 bg-amber-50 text-amber-700 shadow-sm",
  all:       "border-violet-500 bg-violet-50 text-violet-700 shadow-sm",
}

interface FrameworkSelectorProps {
  value: Framework
  onChange: (f: Framework) => void
}

export function FrameworkSelector({ value, onChange }: FrameworkSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {options.map(({ value: v, label, icon: Icon, desc }) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          className={`flex flex-col items-center gap-1 py-3 px-2 rounded-lg
            border text-sm transition-all ${
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
