# Pre-Implementation Verification Report

Datum: 2026-03-15

## Check-Resultate

- [x] Check 1: LCEL-Refactoring
- [x] Check 2: Bestehende Tests
- [x] Check 3: Agent-Abhängigkeiten
- [x] Check 4: Validators importierbar
- [x] Check 5: Output-Verzeichnisse
- [x] Check 6: Ordnerstruktur

---

## Check 1: LCEL-Refactoring ✅

Alle 6 Chains in `src/langchain_prototype/chains/` korrekt umgestellt:

| Datei | Status | LCEL-Komponente |
|-------|--------|-----------------|
| `segmentation_chain.py` | ✅ LCEL | `ChatPromptTemplate \| ChatOpenAI \| StrOutputParser` |
| `classification_chain.py` | ✅ LCEL | `ChatPromptTemplate \| ChatOpenAI \| StrOutputParser` |
| `rewriting_chain.py` | ✅ LCEL | `_build_rewriting_chain()` per Attempt + Temperature-Paradox |
| `validation_chain.py` | ✅ RunnableLambda | Kein LLM — SymPy/BERTScore/Consistency |
| `parsing_chain.py` | ✅ RunnableLambda | Kein LLM — OCR-Handler |
| `assembly_chain.py` | ✅ RunnableLambda | Kein LLM — Dokument-Aggregation |

`src/langchain_prototype/lcel_llm.py` vorhanden mit:
- `get_lcel_llm(temperature, max_tokens)` — OpenAI + BFH via `base_url`
- `_extract_json(text)` — JSON-Parser mit Markdown-Fence und Backslash-Handling

---

## Check 2: Bestehende Tests ✅

| Test | Ergebnis | Anmerkung |
|------|----------|-----------|
| `test_langchain_chains.py` | ✅ | Parsing, Segmentation, Classification OK |
| `test_rewriting_validation.py` | ✅ | 2/3 Varianten + 1/3 valide (BFH-LLM) |
| `test_complete_pipeline.py math` | ✅ | 7/8 valide Varianten, 15.23s |
| `test_langgraph_complete.py` | ✅ | 7/8 valide Varianten, 37.68s, Retry-Loop korrekt |

---

## Check 3: Agent-Abhängigkeiten ✅

Alle Imports verfügbar nach Behebung des Versions-Konflikts (siehe unten):

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor  ✅
from langchain_core.tools import tool                                   ✅
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder ✅
from langchain_openai import ChatOpenAI                                 ✅
from langchain_core.messages import HumanMessage, AIMessage             ✅
```

---

## Check 4: Validators importierbar ✅

```python
from common.validators.sympy_validator import SymPyValidator       ✅
from common.validators.bert_validator import BERTValidator          ✅
from common.validators.consistency_validator import ConsistencyValidator ✅
from common.constants import DOMAIN_MATH, DOMAIN_LANGUAGES, DOMAIN_ECONOMICS ✅
from common.ocr_handler import get_ocr_handler                     ✅
```

Werte: `DOMAIN_MATH='mathematics'`, `DOMAIN_LANGUAGES='languages'`, `DOMAIN_ECONOMICS='economics'`

---

## Check 5: Output-Verzeichnisse ✅

Erstellt:
- `data/output/langchain_agent/`
- `data/output/langchain_agent/orchestrator/`
- `data/output/langchain_agent/multi_agent/`

---

## Check 6: Ordnerstruktur ✅

```
src/langchain_agent_prototype/
├── __init__.py
├── tools/
│   └── __init__.py
├── orchestrator/
│   └── __init__.py
└── multi_agent/
    └── __init__.py
```

---

## Gefundene Probleme und Korrekturen

### Problem 1: `langchain_openai` nicht installiert
`langchain-openai` fehlte in `requirements.txt` und war nicht installiert.

**Aktion:** `pip install langchain-openai` → installierte Version 1.1.11, welche jedoch
`langchain-core` von 0.3.83 auf 1.2.19 hochstuffte.

### Problem 2: Versions-Konflikt `langchain-core`
`langchain-core 1.2.19` inkompatibel mit `langchain 0.3.27` und `langgraph 0.2.76`.
Symptom: `ModuleNotFoundError: No module named 'langchain_core.memory'` bei
`from langchain.agents import AgentExecutor`.

**Aktion:**
```bash
pip install "langchain-core==0.3.83" "langchain-openai<1.0.0"
```
Installiert: `langchain-core==0.3.83`, `langchain-openai==0.3.35`

**requirements.txt aktualisiert:** `langchain-openai==0.3.35`

---

## Bereit für Implementierung

**JA**

Alle 6 Checks bestanden. Beide bestehenden Prototypen laufen korrekt durch
(LangChain: 7/8 valide Varianten, LangGraph: 7/8 valide Varianten mit Retry-Loop).
Alle Agent-Abhängigkeiten importierbar, Verzeichnisstruktur vorhanden.

---

## Nächster Schritt

Implementation von `src/langchain_agent_prototype/` mit zwei Varianten:

**Variante A — Orchestrierungsagent** (`orchestrator/`)
- `create_tool_calling_agent` + `AgentExecutor`
- Ein Agent erhält alle Tools und entscheidet selbstständig über Reihenfolge
- Tools: `classify_tool`, `rewrite_tool`, `validate_tool`, `assemble_tool`

**Variante B — Multi-Agent Pipeline** (`multi_agent/`)
- 3 spezialisierte Einzelagenten (Classifier, Rewriter, Validator)
- Jeder Agent ist fokussiert auf einen Schritt, koordiniert über Pipeline-Logik
- Gemeinsame Tool-Definitionen in `tools/`

**Gemeinsame Tools** (`tools/`):
- `classify_tool` — ruft ClassificationChain (LCEL) auf
- `rewrite_tool` — ruft RewritingChain (LCEL) auf mit Domain-Parameter
- `validate_tool` — ruft ValidationChain auf, gibt strukturiertes Ergebnis zurück
- `ocr_tool` — optional: ruft OCR-Handler auf für Parsing-Step
