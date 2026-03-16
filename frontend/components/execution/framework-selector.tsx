"use client"

import type { Framework } from "@/lib/types"
import { cn } from "@/lib/utils"
import { GitBranch, Workflow, GitMerge, LayoutGrid, Bot, GitFork, Layers } from "lucide-react"

const coreOptions: {
  value: Framework; label: string
  icon: React.ElementType; desc: string
}[] = [
  { value: "langchain", label: "LangChain", icon: GitBranch,  desc: "Chain-basiert"       },
  { value: "langgraph", label: "LangGraph", icon: Workflow,   desc: "State Machine"        },
  { value: "hybrid",    label: "Hybrid",    icon: GitMerge,   desc: "LC + LG kombiniert"   },
  { value: "all",       label: "Alle drei", icon: LayoutGrid, desc: "Vollvergleich"         },
]

const agentOptions: {
  value: Framework; label: string
  icon: React.ElementType; desc: string
}[] = [
  { value: "agent_orchestrator", label: "Agent A",      icon: Bot,     desc: "Orchestrator (ReAct)"  },
  { value: "agent_multi",        label: "Agent B",      icon: GitFork, desc: "Multi-Agent Pipeline"  },
  { value: "hybrid_agent",       label: "Hybrid+Agent", icon: Layers,  desc: "LC Pre/Post + Agent"   },
]

const activeColors: Record<Framework, string> = {
  langchain:          "border-blue-500 bg-blue-50 text-blue-700 shadow-sm",
  langgraph:          "border-emerald-500 bg-emerald-50 text-emerald-700 shadow-sm",
  hybrid:             "border-amber-500 bg-amber-50 text-amber-700 shadow-sm",
  all:                "border-violet-500 bg-violet-50 text-violet-700 shadow-sm",
  agent_orchestrator: "border-rose-500 bg-rose-50 text-rose-700 shadow-sm",
  agent_multi:        "border-orange-500 bg-orange-50 text-orange-700 shadow-sm",
  hybrid_agent:       "border-teal-500 bg-teal-50 text-teal-700 shadow-sm",
}

const isAgentFramework = (v: Framework) =>
  v === "agent_orchestrator" || v === "agent_multi" || v === "hybrid_agent"

interface FrameworkSelectorProps {
  value: Framework
  onChange: (f: Framework) => void
}

export function FrameworkSelector({ value, onChange }: FrameworkSelectorProps) {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        {coreOptions.map(({ value: v, label, icon: Icon, desc }) => (
          <button
            key={v}
            onClick={() => onChange(v)}
            className={cn(
              "flex flex-col items-center gap-1 py-3 px-2 rounded-lg border text-sm transition-all",
              value === v ? activeColors[v] : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50"
            )}
          >
            <Icon className="h-5 w-5" />
            <span className="font-semibold">{label}</span>
            <span className="text-xs opacity-70">{desc}</span>
          </button>
        ))}
      </div>

      <div className="space-y-1.5">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">
          Agenten-Varianten (Thesis)
        </p>
        <div className="grid grid-cols-2 gap-2">
          {agentOptions.map(({ value: v, label, icon: Icon, desc }) => (
            <button
              key={v}
              onClick={() => onChange(v)}
              className={cn(
                "flex flex-col items-center gap-1 py-3 px-2 rounded-lg border text-sm transition-all",
                value === v ? activeColors[v] : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50"
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="font-semibold">{label}</span>
              <span className="text-xs opacity-70">{desc}</span>
            </button>
          ))}
        </div>
        {isAgentFramework(value) && (
          <p className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded px-2 py-1">
            {{
              agent_orchestrator: "Erwartete Laufzeit: 5–10 Min. (60–75 sequenzielle LLM-Calls pro Dokument)",
              agent_multi:        "Erwartete Laufzeit: 3–6 Min. (keine Retry-Koordination zwischen Agenten)",
              hybrid_agent:       "Erwartete Laufzeit: 3–5 Min. (Agent nur in Phase 2, Pre/Post deterministisch)",
            }[value as "agent_orchestrator" | "agent_multi" | "hybrid_agent"]}
          </p>
        )}
      </div>
    </div>
  )
}
