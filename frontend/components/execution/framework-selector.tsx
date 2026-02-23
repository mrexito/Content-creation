"use client"

import type { Framework } from "@/lib/types"
import { GitBranch, Workflow, Layers } from "lucide-react"

const options: { value: Framework; label: string; icon: React.ElementType; desc: string }[] = [
  { value: "langchain", label: "LangChain", icon: GitBranch, desc: "Chain-basiert" },
  { value: "langgraph", label: "LangGraph", icon: Workflow, desc: "State Machine" },
  { value: "both", label: "Beide", icon: Layers, desc: "Parallel Vergleich" },
]

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
              ? v === "both"
                ? "border-purple-500 bg-purple-500/10 text-purple-300"
                : "border-emerald-500 bg-emerald-500/10 text-emerald-300"
              : "border-slate-500 bg-slate-600/40 text-slate-300 hover:border-slate-400 hover:text-slate-100"
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
