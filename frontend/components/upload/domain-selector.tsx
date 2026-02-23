"use client"

import type { Domain } from "@/lib/types"
import { Calculator, Languages, TrendingUp, Sparkles } from "lucide-react"

const domains: { value: Domain; label: string; icon: React.ElementType; desc: string }[] = [
  { value: "auto", label: "Auto", icon: Sparkles, desc: "Auto-detect" },
  { value: "math", label: "Mathematik", icon: Calculator, desc: "SymPy validation" },
  { value: "languages", label: "Sprachen", icon: Languages, desc: "BERTScore" },
  { value: "economics", label: "Wirtschaft", icon: TrendingUp, desc: "Consistency checks" },
]

interface DomainSelectorProps {
  value: Domain
  onChange: (d: Domain) => void
}

export function DomainSelector({ value, onChange }: DomainSelectorProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
      {domains.map(({ value: v, label, icon: Icon, desc }) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          className={`flex flex-col items-center gap-1 p-3 rounded-lg border text-sm transition-all ${
            value === v
              ? "border-blue-500 bg-blue-500/10 text-blue-300"
              : "border-slate-500 bg-slate-600/40 text-slate-300 hover:border-slate-400 hover:text-slate-100"
          }`}
        >
          <Icon className="h-5 w-5" />
          <span className="font-medium">{label}</span>
          <span className="text-xs opacity-70">{desc}</span>
        </button>
      ))}
    </div>
  )
}
