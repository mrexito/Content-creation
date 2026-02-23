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

### Two Parallel Implementations

Both implement the same 6-step pipeline but with different orchestration patterns:

**LangChain** (`src/langchain_prototype/`): Chain-based, sequential. `LangChainPipeline` in `pipeline.py` calls chains in order. Each step (`parsing_chain`, `segmentation_chain`, etc.) is independent and invoked manually.

**LangGraph** (`src/langgraph_prototype/`): State-machine-based. `create_workflow_graph()` in `graph.py` builds a `StateGraph` where nodes communicate via `WorkflowState` (a `TypedDict`). Has a conditional edge after validation to either assemble or end with error.

### Shared Components (`src/common/`)

- `llm_handler.py`: Singleton `LLMHandler` wrapping OpenAI SDK for both OpenAI and BFH (OpenAI-compatible). Use `get_llm_handler()` / `reset_llm_handler()` to manage the singleton. Call `reset_llm_handler()` before switching providers.
- `ocr_handler.py`: Wraps Tesseract and Mistral OCR.
- `config.py`: Loads `.env.dev` at import time. Exposes `Config` class with all settings as class attributes.
- `validators/`: Domain-specific validators:
  - `SymPyValidator` — math domain (validates equation correctness)
  - `BERTValidator` — languages domain (BERTScore semantic similarity)
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
