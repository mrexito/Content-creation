"use client"

interface ConfigPanelProps {
  numVariants: number
  maxRetries: number
  onVariantsChange: (n: number) => void
  onRetriesChange: (n: number) => void
}

function Slider({
  label,
  value,
  min,
  max,
  onChange,
  hint,
}: {
  label: string
  value: number
  min: number
  max: number
  onChange: (n: number) => void
  hint: string
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className="text-sm text-slate-300">{label}</label>
        <span className="text-sm font-mono font-semibold text-blue-300 w-6 text-right">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-blue-500 cursor-pointer"
      />
      <p className="text-xs text-slate-300">{hint}</p>
    </div>
  )
}

export function ConfigPanel({ numVariants, maxRetries, onVariantsChange, onRetriesChange }: ConfigPanelProps) {
  return (
    <div className="space-y-5">
      <Slider
        label="Varianten pro Segment"
        value={numVariants}
        min={1}
        max={5}
        onChange={onVariantsChange}
        hint="Anzahl generierter Textvarianten"
      />
      <Slider
        label="Max. Retry-Versuche"
        value={maxRetries}
        min={0}
        max={5}
        onChange={onRetriesChange}
        hint="Versuche bei Validierungs-Fehler"
      />
    </div>
  )
}
