"use client"

import type { Phase } from "@/lib/types"
import { Check, Loader2 } from "lucide-react"

const PHASES: Phase[] = [
  "parsing",
  "segmentation",
  "classification",
  "rewriting",
  "validation",
  "assembly",
]

const PHASE_LABELS: Record<string, string> = {
  parsing: "Parsing",
  segmentation: "Segmentierung",
  classification: "Klassifizierung",
  rewriting: "Rewriting",
  validation: "Validierung",
  assembly: "Assembly",
}

interface PhaseIndicatorProps {
  currentPhase: Phase
  phasesCompleted: Phase[]
}

export function PhaseIndicator({ currentPhase, phasesCompleted }: PhaseIndicatorProps) {
  return (
    <div className="flex items-center gap-1 flex-wrap">
      {PHASES.map((phase, i) => {
        const done = phasesCompleted.includes(phase)
        const active = currentPhase === phase && !done
        return (
          <div key={phase} className="flex items-center gap-1">
            <div
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-all ${
                done
                  ? "bg-emerald-100 text-emerald-700"
                  : active
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-400"
              }`}
            >
              {done ? (
                <Check className="h-3 w-3" />
              ) : active ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <span className="h-3 w-3 flex items-center justify-center text-[10px]">{i + 1}</span>
              )}
              {PHASE_LABELS[phase]}
            </div>
            {i < PHASES.length - 1 && (
              <span className="text-gray-300 text-xs">→</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
