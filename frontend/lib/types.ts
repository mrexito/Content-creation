export type Framework = "langchain" | "langgraph" | "hybrid" | "all"
export type Domain = "math" | "languages" | "economics" | "auto"
export type OcrTool = "tesseract" | "mistral" | "auto"
export type LlmProvider = "openai" | "bfh" | "auto"
export type Phase =
  | "idle"
  | "parsing"
  | "segmentation"
  | "classification"
  | "rewriting"
  | "validation"
  | "assembly"
  | "complete"
  | "error"

export type RunStatus = "pending" | "running" | "complete" | "error"

export interface RunConfig {
  pdfs: File[]
  domain: Domain
  framework: Framework
  numVariants: number
  maxRetries: number
  ocrTool: OcrTool
  llmProvider: LlmProvider
  llmModel: string
}

export interface ProgressState {
  status: RunStatus
  current_phase: Phase
  phases_completed: Phase[]
  progress_percent: number
  metadata: {
    pdf_name: string
    framework: string
    domain: string
    error?: string
  }
}

export interface VariantResult {
  variant_id: number
  text: string
  is_valid: boolean
  validation_issues: string[]
  numbers_changed_pct?: number
  diversity_score?: number
}

export interface SegmentResult {
  original_segment: {
    text: string
    type: string
  }
  classification: {
    domain: string
    type: string
    complexity: string
  }
  validated_variants: VariantResult[]
  validation_statistics: {
    total: number
    valid: number
    avg_diversity: number
    skipped?: boolean
  }
}

export interface PipelineMetrics {
  total_time: number
  ocr_time?: number
  ocr_tool?: string
  num_segments: number
  total_variants: number
  valid_variants: number
  validation_rate: number
}

export interface PipelineResult {
  success: boolean
  framework: string
  domain: string
  pdf_name: string
  metrics: PipelineMetrics
  segments: SegmentResult[]
  error?: string
  output_files?: string[]
  pdf_files?: {
    tasks: string
    solutions: string
  }
}

export interface RunResult {
  id: string
  timestamp: string
  pdf_name: string
  domain: Domain
  framework: Framework
  config: {
    numVariants: number
    maxRetries: number
    ocrTool?: OcrTool
    llmProvider?: LlmProvider
    llmModel?: string
  }
  status: RunStatus
  langchain?: PipelineResult
  langgraph?: PipelineResult
  hybrid?: PipelineResult
  duration?: number
}
