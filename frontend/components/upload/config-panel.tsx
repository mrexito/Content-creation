"use client"

import type { OcrTool, LlmProvider } from "@/lib/types"

// ---------------------------------------------------------------------------
// Model lists per provider
// ---------------------------------------------------------------------------
const OPENAI_MODELS = [
  { value: "gpt-4o-mini", label: "GPT-4o mini" },
  { value: "gpt-4o",      label: "GPT-4o" },
  { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
]

const BFH_MODELS = [
  { value: "gpt-oss:120b", label: "GPT-OSS 120B" },
  { value: "gemma3:4b",    label: "Gemma 3 4B" },
]

function modelsForProvider(provider: LlmProvider) {
  if (provider === "bfh")    return BFH_MODELS
  if (provider === "openai") return OPENAI_MODELS
  return [...OPENAI_MODELS, ...BFH_MODELS]
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function Slider({
  label, value, min, max, onChange, hint,
}: {
  label: string; value: number; min: number; max: number
  onChange: (n: number) => void; hint: string
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-semibold text-blue-600 tabular-nums w-5 text-right">{value}</span>
      </div>
      <input
        type="range" min={min} max={max} value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-blue-600 cursor-pointer"
      />
      <p className="text-xs text-gray-400">{hint}</p>
    </div>
  )
}

function ButtonGroup<T extends string>({
  options, value, onChange,
}: {
  options: { value: T; label: string }[]
  value: T
  onChange: (v: T) => void
}) {
  return (
    <div className="flex rounded-md border border-gray-200 overflow-hidden text-xs">
      {options.map((opt, i) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={[
            "flex-1 py-1.5 px-2 font-medium transition-colors",
            i > 0 ? "border-l border-gray-200" : "",
            value === opt.value
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-600 hover:bg-gray-50",
          ].join(" ")}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface ConfigPanelProps {
  numVariants: number
  maxRetries: number
  ocrTool: OcrTool
  llmProvider: LlmProvider
  llmModel: string
  onVariantsChange: (n: number) => void
  onRetriesChange: (n: number) => void
  onOcrToolChange: (t: OcrTool) => void
  onLlmProviderChange: (p: LlmProvider) => void
  onLlmModelChange: (m: string) => void
}

export function ConfigPanel({
  numVariants, maxRetries, ocrTool, llmProvider, llmModel,
  onVariantsChange, onRetriesChange,
  onOcrToolChange, onLlmProviderChange, onLlmModelChange,
}: ConfigPanelProps) {
  const models = modelsForProvider(llmProvider)

  const handleProviderChange = (p: LlmProvider) => {
    onLlmProviderChange(p)
    // Reset model if not available for new provider
    const available = modelsForProvider(p)
    if (llmModel && !available.find((m) => m.value === llmModel)) {
      onLlmModelChange("")
    }
  }

  return (
    <div className="space-y-5">
      {/* Varianten & Retries */}
      <Slider
        label="Varianten pro Segment"
        value={numVariants} min={1} max={5}
        onChange={onVariantsChange}
        hint="Anzahl generierter Textvarianten"
      />
      <Slider
        label="Max. Retry-Versuche"
        value={maxRetries} min={0} max={5}
        onChange={onRetriesChange}
        hint="Versuche bei Validierungs-Fehler"
      />

      <div className="border-t border-gray-100 pt-4 space-y-4">
        {/* OCR Tool */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-gray-700">OCR-Tool</label>
          <ButtonGroup<OcrTool>
            options={[
              { value: "auto",      label: "Auto" },
              { value: "tesseract", label: "Tesseract" },
              { value: "mistral",   label: "Mistral" },
            ]}
            value={ocrTool}
            onChange={onOcrToolChange}
          />
          <p className="text-xs text-gray-400">
            {ocrTool === "mistral"
              ? "Mistral Vision – ideal für Formeln (benötigt API-Key)"
              : ocrTool === "tesseract"
              ? "Tesseract – lokal, geeignet für Fliesstext"
              : "Domain-abhängig (Math → Mistral, Text → Tesseract)"}
          </p>
        </div>

        {/* LLM Provider */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-gray-700">LLM-Provider</label>
          <ButtonGroup<LlmProvider>
            options={[
              { value: "auto",   label: "Auto" },
              { value: "openai", label: "OpenAI" },
              { value: "bfh",    label: "BFH" },
            ]}
            value={llmProvider}
            onChange={handleProviderChange}
          />
          <p className="text-xs text-gray-400">
            {llmProvider === "openai"
              ? "OpenAI API (benötigt OPENAI_API_KEY)"
              : llmProvider === "bfh"
              ? "BFH-Inferenz (benötigt BFH_LLM_API_KEY)"
              : "Automatisch anhand verfügbarer API-Keys"}
          </p>
        </div>

        {/* Modell */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-gray-700">Modell</label>
          <select
            value={llmModel}
            onChange={(e) => onLlmModelChange(e.target.value)}
            className="w-full text-sm border border-gray-200 rounded-md px-2.5 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Provider-Standard</option>
            {models.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
          <p className="text-xs text-gray-400">Leer = Standard-Modell des Providers</p>
        </div>
      </div>
    </div>
  )
}
