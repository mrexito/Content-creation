After completing a task that involves tool use, provide a quick summary of the work you've done

By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed, using tools to discover any missing details instead of guessing. Try to infer the user's intent about whether a tool call (e.g. file edit or read) is intended or not, and act accordingly.

Use parallel tool calls:
If you intend to call multiple tools and there are no dependencies
between the tool calls, make all of the independent tool calls in
parallel. Prioritize calling tools simultaneously whenever the
actions can be done in parallel rather than sequentially. For
example, when reading 3 files, run 3 tool calls in parallel to read
all 3 files into context at the same time. Maximize use of parallel
tool calls where possible to increase speed and efficiency.
However, if some tool calls depend on previous calls to inform
dependent values like the parameters, do not call these tools in
parallel and instead call them sequentially. Never use placeholders
or guess missing parameters in tool calls.

If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.

Reduce hallucinations:
Never speculate about code you have not opened. If the user
references a specific file, you MUST read the file before
answering. Make sure to investigate and read relevant files BEFORE
answering questions about the codebase. Never make any claims about
code before investigating unless you are certain of the correct
answer - give grounded and hallucination-free answers.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Master thesis project (Berner Fachhochschule) comparing LangChain, LangGraph, and hybrid approaches for automated content rewriting of learning materials (PDFs → variant documents). The pipeline: PDF → OCR → Segmentation → Classification → Rewriting → Validation → Assembly.

## Setup & Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate test PDFs (needed before running pipelines)
python scripts/generate_test_pdfs.py

# Run the main pipeline comparison (4 OCR×LLM combinations)
python scripts/pipeline_comparison.py
python scripts/pipeline_comparison.py data/input/math/equations_simple.pdf
python scripts/pipeline_comparison.py data/input/math/equations_simple.pdf --combos 1,3

# Evaluate LangChain vs LangGraph across all domains
python scripts/evaluate_all_domains.py

# Individual test scripts
python scripts/test_langgraph_complete.py
python scripts/test_langchain_chains.py
python scripts/test_langgraph_nodes.py
python scripts/test_llm_handler.py
python scripts/test_validators.py

# Run with pytest (if tests are structured for it)
pytest scripts/
```

## Python Path

Scripts add `src/` to the path via `sys.path.insert(0, ...)`. When running scripts from the project root, this is handled automatically. For direct imports outside of scripts, set `PYTHONPATH=src`.

## Configuration

All config lives in `.env.dev` (not `.env`). Copy and edit it:

```bash
cp .env.dev .env.dev.local
```

Key config options:

- `LLM_PROVIDER`: `'openai'`, `'bfh'`, or `'auto'` (auto-detects from available API keys)
- `OCR_DEFAULT_TOOL`: `'tesseract'`, `'mistral'`, or `'auto'`
- `OCR_DOMAIN_MATH/LANGUAGES/ECONOMICS`: per-domain OCR tool overrides
- BFH LLM endpoint uses OpenAI-compatible API at `https://inference.mlmp.ti.bfh.ch/api/v1`

## Architecture

### Three Implementations

All three implement the same 6-step pipeline but with different orchestration patterns:

**LangChain** (`src/langchain_prototype/`): Chain-based, sequential. `LangChainPipeline` in `pipeline.py` calls chains in order. Each step (`parsing_chain`, `segmentation_chain`, etc.) is independent and invoked manually.

**LangGraph** (`src/langgraph_prototype/`): State-machine-based. `create_workflow_graph()` in `graph.py` builds a `StateGraph` where nodes communicate via `WorkflowState` (a `TypedDict`). Conditional edge after validation routes to retry or assembly. **IMPORTANT:** State mutations MUST happen in nodes, never in edge functions (edge mutations are silently discarded by LangGraph).

**Hybrid** (`src/hybrid_prototype/`): 3-Phase architecture. Phase 1: LangChain (OCR+Segmentation+Classification). Phase 2: LangGraph StateGraph (Rewriting↔Validation retry loop). Phase 3: LangChain (Assembly+Export).

### Shared Components (`src/common/`)

- `constants.py`: **Kanonische Domain-Konstanten** (`DOMAIN_MATH = "mathematics"`, etc.) und `BERT_THRESHOLD = 0.70`. Enthält `normalize_domain()` Funktion die `'math'` → `'mathematics'` normalisiert. Muss für alle Domain-Vergleiche im Code verwendet werden.
- `llm_handler.py`: Singleton `LLMHandler` wrapping OpenAI SDK for both OpenAI and BFH (OpenAI-compatible). Use `get_llm_handler()` / `reset_llm_handler()` to manage the singleton. Call `reset_llm_handler()` before switching providers.
- `ocr_handler.py`: Wraps Tesseract and Mistral OCR (`mistral-ocr-latest` via `client.ocr.process()`). Domain-Präferenzen nutzen kanonische Konstanten.
- `config.py`: Loads `.env.dev` at import time. Exposes `Config` class with all settings as class attributes.
- `validators/`: Domain-specific validators:
  - `SymPyValidator` — math domain (validates equation correctness)
  - `BERTValidator` — languages domain (BERTScore semantic similarity, threshold `BERT_THRESHOLD=0.70`)
  - `ConsistencyValidator` — economics domain (numeric consistency checks)

### Test Domains

Three domains in `data/input/`:

- `math/equations_simple.pdf` — uses Mistral OCR + SymPy validation
- `languages/grammar_exercise.pdf` — uses Tesseract + BERTScore
- `economics/balance_sheet.pdf` — uses Tesseract + consistency checks

### Pipeline Comparison Script

`scripts/pipeline_comparison.py` tests 4 combinations: {Mistral OCR, Tesseract} × {BFH LLM, GPT-4}. Key metric: ≥30% number change in rewritten variants. Outputs JSON reports to `data/output/comparison/`.

### Output Structure

- `data/output/langchain/` — LangChain results
- `data/output/langgraph/` — LangGraph results
- `data/output/comparison/` — pipeline comparison JSON reports
- `data/output/evaluation/` — evaluation reports (LangChain vs LangGraph)

## Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev     # http://localhost:3000
npm run build   # production build check
```

**Stack:** Next.js 16 (App Router), TypeScript strict, Tailwind CSS v4, shadcn/ui, recharts, lucide-react

**Key files:**

- `frontend/app/page.tsx` — main page: upload + run + live progress
- `frontend/app/history/page.tsx` — past runs (localStorage)
- `frontend/app/results/[id]/page.tsx` — result detail view
- `frontend/lib/types.ts` — all shared TypeScript types
- `frontend/lib/python-runner.ts` — server-side: spawns Python scripts, reads progress/result JSON
- `frontend/lib/file-utils.ts` — client-safe utilities (no Node built-ins)
- `frontend/lib/server-utils.ts` — server-only file utilities (fs/path)

**How the frontend invokes Python:**

1. `POST /api/upload` saves PDFs to `data/input/frontend-uploads/`
2. `POST /api/run` spawns `scripts/run_langchain_pipeline.py` or `run_langgraph_pipeline.py` via `child_process.spawn` with `PYTHONPATH=src`
3. `GET /api/progress/[runId]` reads `data/output/{framework}/{runId}/progress.json` (polled every 500ms)
4. `GET /api/results/[runId]` reads `data/output/{framework}/{runId}/result.json`

**Frontend pipeline scripts** (`scripts/run_langchain_pipeline.py`, `scripts/run_langgraph_pipeline.py`):

- Accept `--pdf`, `--domain`, `--variants`, `--retries`, `--output-dir`, `--progress`, `--run-id`
- Write progress updates to `--progress` path throughout execution
- Write `result.json` with a standardized `PipelineResult` schema on completion
