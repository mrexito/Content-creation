# LangChain vs. LangGraph — Automatisiertes Content-Rewriting

Dieses Repository enthält den vollständigen Quellcode zum Vergleich von LangChain, LangGraph und einem hybriden Ansatz für die automatisierte Variantenerstellung von Lern- und Trainingsmaterialien.

---

## Inhalt

- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Testdokumente generieren](#testdokumente-generieren)
- [Prototypen ausführen](#prototypen-ausführen)
- [Frontend starten](#frontend-starten)
- [Evaluation](#evaluation)
- [Projektstruktur](#projektstruktur)

---

## Voraussetzungen

| Komponente | Version | macOS | Windows |
|---|---|---|---|
| Python | 3.12 | `brew install python@3.12` | [python.org/downloads](https://python.org/downloads) → Installer |
| Node.js | ≥ 18 | `brew install node` | [nodejs.org](https://nodejs.org) → LTS Installer |
| Tesseract OCR | aktuell | `brew install tesseract tesseract-lang` | [UB-Mannheim Installer](https://github.com/UB-Mannheim/tesseract/wiki) → Sprachpaket `deu+eng` auswählen |
| Poppler (pdftoppm) | aktuell | `brew install poppler` | [poppler-windows](https://github.com/oschwartz10612/poppler-windows) → ZIP entpacken, `bin/` zu PATH hinzufügen |
| Git | aktuell | `brew install git` | [git-scm.com](https://git-scm.com) → Installer |

Für die Mathematikdomäne wird zusätzlich ein **Mistral API-Key** benötigt (kostenpflichtig, Pay-per-use). Ohne diesen Key schaltet das System automatisch auf Tesseract um, wobei die Formelerkennungsqualität eingeschränkt ist.

Die korrekte Installation kann mit folgenden Befehlen geprüft werden:

```bash
python --version
node --version
git --version
tesseract --version
pdftoppm -v
```

---

## Installation

```bash
# 1. Repository klonen
git clone https://github.com/Kuenzlij/langchain-langgraph-comparison
cd langchain-langgraph-comparison

# 2. Python-Abhängigkeiten installieren (ca. 3–5 Minuten)
pip install -r requirements.txt

# 3. Konfigurationsdatei einrichten
cp env.template .env.dev       # macOS
copy env.template .env.dev     # Windows
```

**Hinweis zu Versionskonflikten:** Falls es beim Installieren zu Konflikten zwischen `openai`, `langchain-openai` und abhängigen Paketen kommt, empfiehlt es sich, die Versionsangaben für diese Pakete aus `requirements.txt` zu entfernen und pip die Auflösung selbst übernehmen zu lassen. Alternativ kann die Umgebung in einem neuen Virtual Environment aufgesetzt werden:

```bash
# macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Konfiguration
**ACHTUNG:** Der BFH Endpunkt kann nur via VPN der BFH benutzt werden.
Das Repository enthält eine Vorlagedatei `env.template` mit allen verfügbaren Einstellungen. Nach dem Kopieren (siehe Installation) werden die Pflichtfelder in `.env.dev` eingetragen:

```env
# --- BFH LLM (empfohlen) ---
BFH_LLM_ENDPOINT=https://inference.mlmp.ti.bfh.ch/api/v1
BFH_LLM_API_KEY=              # Pflichtfeld — siehe https://infra.pages.ti.bfh.ch/mlmp/src/llm/
BFH_LLM_MODEL=gpt-oss:120b

# --- OpenAI (alternativ) ---
OPENAI_API_KEY=               # nur bei LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# --- OCR ---
MISTRAL_API_KEY=              # Pflichtfeld für Mathematikdomäne
```

**Pflichtfelder:** `BFH_LLM_API_KEY` und `MISTRAL_API_KEY`. Alle anderen Werte können unverändert übernommen werden.

---

## Testdokumente generieren

Vor dem ersten Ausführen müssen die 15 Test-PDFs generiert werden:

```bash
python scripts/generate_test_pdfs.py
```

Dies legt folgende Dokumente an:

```
data/input/
├── math/          # 5 PDFs: Gleichungen, Geometrie, Textaufgaben
├── languages/     # 5 PDFs: Grammatikübungen, Satzkonstruktionen
└── economics/     # 5 PDFs: Bilanzen, Kostenrechnung, Investition
```

---

## Prototypen ausführen

### Hybrid-Prototyp (direkt via src/)

Der Hybrid-Prototyp verfügt über einen eigenständigen Einstiegspunkt:

```bash
python src/hybrid_prototype/run_hybrid.py
python src/hybrid_prototype/run_hybrid.py --domain math --variants 2
python src/hybrid_prototype/run_hybrid.py --pdf data/input/economics/case_study.pdf
```

| Parameter | Beschreibung | Standardwert |
|---|---|---|
| `--pdf` | Pfad zur Input-PDF | erstes verfügbares Test-PDF |
| `--domain` | `math`, `languages`, `economics` | Auto-Detect |
| `--variants` | Anzahl Varianten pro Segment | 3 |
| `--retries` | Maximale Retry-Iterationen im LangGraph-Loop | 2 |

### LangChain- und LangGraph-Prototypen (via scripts/)

LangChain und LangGraph werden über die Frontend-Wrapper-Skripte ausgeführt, die Fortschritt und Ergebnis als JSON schreiben:

```bash
# LangChain LCEL-Pipeline
python scripts/run_langchain_pipeline.py \
  --pdf data/input/math/equations_simple.pdf \
  --domain math \
  --variants 2 \
  --output-dir data/output/langchain/test-run \
  --progress data/output/langchain/test-run/progress.json \
  --run-id test-run

# LangGraph StateGraph
python scripts/run_langgraph_pipeline.py \
  --pdf data/input/math/equations_simple.pdf \
  --domain math \
  --variants 2 \
  --output-dir data/output/langgraph/test-run \
  --progress data/output/langgraph/test-run/progress.json \
  --run-id test-run
```

| Parameter | Beschreibung |
|---|---|
| `--pdf` | Pfad zur Input-PDF (Pflichtfeld) |
| `--domain` | `math`, `languages`, `economics` (Standard: `auto`) |
| `--variants` | Anzahl Varianten pro Segment (Standard: 2) |
| `--retries` | Maximale Retry-Iterationen (Standard: 3) |
| `--output-dir` | Output-Verzeichnis (Pflichtfeld) |
| `--progress` | Pfad zur progress.json (Pflichtfeld) |
| `--run-id` | Eindeutige Run-ID (optional) |
| `--ocr-tool` | `auto`, `tesseract`, `mistral` (Standard: `auto`) |

Diese Skripte schreiben während der Ausführung kontinuierlich `progress.json` und legen nach Abschluss `result.json` im angegebenen Output-Verzeichnis ab. Das Frontend ruft sie intern via `child_process.spawn` auf.

### PYTHONPATH

Alle Skripte setzen `src/` via `sys.path.insert` automatisch auf den Python-Pfad. Für direkte Importe ausserhalb der Skriptumgebung:

```bash
export PYTHONPATH=src        # macOS
set PYTHONPATH=src           # Windows CMD
$env:PYTHONPATH = "src"      # Windows PowerShell
```

---

## Frontend starten

Das Frontend dient als Demonstrationsumgebung und steuert alle Prototypen einheitlich an.

```bash
cd frontend
npm install
npm run dev
```

Anschliessend unter `http://localhost:3000` erreichbar.

**Funktionen:** PDF-Upload, Framework- und OCR-Auswahl, Echtzeit-Fortschrittsanzeige, Segment-für-Segment-Vergleich von Original und Variante, History-Ansicht abgeschlossener Runs.

---

## Evaluation

### Vollständiger Vergleichslauf (alle Frameworks, alle Domänen)

```bash
python scripts/evaluate_all_frameworks.py
```

Führt alle drei Haupt-Frameworks (LangChain, LangGraph, Hybrid) über alle drei Domänen aus. Ergebnisse werden als JSON- und Markdown-Reports mit Zeitstempel abgelegt:

```
data/output/evaluation/
└── [zeitstempel]/
    ├── full_comparison_raw.json   # Aggregierte Metriken aller Runs
    ├── full_comparison_raw.md     # Lesbare Zusammenfassung
    └── [domäne]/                  # Einzelergebnisse pro Segment und Domäne
```

### LangChain-Variantenvergleich (Pipeline vs. Orchestrator vs. Multi-Agent)

```bash
# Alle drei Domänen mit Default-PDFs
python scripts/compare_langchain_variants.py --all-domains

# Einzelne Domäne mit explizitem PDF
python scripts/compare_langchain_variants.py \
  --pdf data/input/math/equations_simple.pdf \
  --domain mathematics

# Selektive Varianten (z.B. nur Pipeline und Orchestrator)
python scripts/compare_langchain_variants.py --all-domains --skip-multi
```

| Parameter | Beschreibung |
|---|---|
| `--all-domains` | Alle drei Domänen mit Default-PDFs ausführen |
| `--pdf` | Pfad zur Input-PDF (erforderlich ohne `--all-domains`) |
| `--domain` | `mathematics`, `languages`, `economics` (erforderlich ohne `--all-domains`) |
| `--variants` | Anzahl Varianten pro Segment (Standard: 1) |
| `--retries` | Max. Retries für Orchestrator (Standard: 3) |
| `--skip-pipeline` | `langchain_pipeline`-Variante überspringen |
| `--skip-orchestrator` | `agent_orchestrator`-Variante überspringen |
| `--skip-multi` | `agent_multi`-Variante überspringen |

Ergebnisse werden in `data/output/langchain_comparison/` gespeichert.

### BERTScore-Kalibrierung

```bash
# Schritt 1: Paare extrahieren
python scripts/calibrate_bert_threshold.py --step1

# Schritt 2: Nach manueller Bewertung in calibration_pairs.json
python scripts/calibrate_bert_threshold.py --step2
```

### Tests

```bash
pytest tests/
```

---

## Projektstruktur

```
langchain-langgraph-comparison/
├── src/
│   ├── common/                  # Gemeinsame Komponenten (OCR, Validatoren, Config)
│   │   ├── config.py
│   │   ├── constants.py         # Schwellwerte und Domain-Konstanten
│   │   ├── ocr_handler.py
│   │   └── validators/
│   │       ├── bert_validator.py
│   │       ├── sympy_validator.py
│   │       └── consistency_validator.py
│   ├── langchain_prototype/     # LangChain LCEL-Pipeline
│   ├── langgraph_prototype/     # LangGraph StateGraph
│   └── hybrid_prototype/        # Dreiphasige Hybridarchitektur (LC + LG + LC)
├── frontend/                    # Next.js Demonstrationsumgebung
├── scripts/                     # Evaluations- und Hilfsskripte
│   ├── evaluate_all_frameworks.py      # Hauptevaluationsskript (alle Frameworks)
│   ├── compare_langchain_variants.py   # LangChain-Variantenvergleich
│   ├── run_langchain_pipeline.py       # Frontend-Wrapper LangChain
│   ├── run_langgraph_pipeline.py       # Frontend-Wrapper LangGraph
│   ├── generate_test_pdfs.py           # Test-PDFs generieren
│   └── calibrate_bert_threshold.py     # BERTScore-Schwellwert kalibrieren
├── data/
│   ├── input/                   # Test-PDFs (nach generate_test_pdfs.py)
│   ├── output/                  # Evaluationsergebnisse
│   └── parsed/                  # Zwischenergebnisse OCR
├── tests/
├── requirements.txt
├── env.template                 # Vorlage für Umgebungsvariablen
└── README.md
```

---

## Domänen und Validierung

| Domäne | Validierungsinstrument | Schwellwert |
|---|---|---|
| Mathematik | SymPy (algebraische Prüfung) + LLM-Plausibilitäts-Check | Zahlenänderung ≥ 30% |
| Sprache | BERTScore F1 (bert-base-multilingual-cased) | F1 ≥ 0.81 |
| Wirtschaft | ConsistencyCheck + BERTScore + LLM-Plausibilitäts-Check | BERTScore F1 ≥ 0.72 |

---

## Lizenz

Dieses Repository dient ausschliesslich wissenschaftlichen Zwecken im Rahmen der Masterthesis an der Berner Fachhochschule.
