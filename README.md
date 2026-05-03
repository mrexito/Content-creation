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

| Komponente | Version | Installation (macOS) |
|---|---|---|
| Python | 3.12 | `brew install python@3.12` |
| Node.js | ≥ 18 | `brew install node` |
| Tesseract OCR | aktuell | `brew install tesseract tesseract-lang` |

Für die Mathematikdomäne wird zusätzlich ein **Mistral API-Key** benötigt (kostenpflichtig, Pay-per-use). Ohne diesen Key schaltet das System automatisch auf Tesseract um, wobei die Formelerkennungsqualität eingeschränkt ist.

---

## Installation

```bash
# 1. Repository klonen
git clone https://github.com/Kuenzlij/langchain-langgraph-comparison
cd langchain-langgraph-comparison

# 2. Python-Abhängigkeiten installieren (ca. 3–5 Minuten)
pip install -r requirements.txt

# 3. Umgebungsvariablen einrichten
cp .env.dev .env.dev.local
```

---

## Konfiguration

Alle Einstellungen werden in `.env.dev.local` gesetzt. Die Datei enthält folgende Variablen:

```env
# Virtuelles Environment (optional, nur lokal relevant)
# source venv/bin/activate

# --- LLM Allgemein ---
LLM_PROVIDER=bfh              # 'bfh', 'openai' oder 'auto'
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
MAX_ITERATIONS=3
BERT_SCORE_THRESHOLD=0.92

# --- BFH LLM (empfohlen) ---
BFH_LLM_ENDPOINT=https://inference.mlmp.ti.bfh.ch/api/v1
BFH_LLM_API_KEY=              # Pflichtfeld
BFH_LLM_MODEL=gpt-oss:120b

# --- OpenAI (alternativ) ---
OPENAI_API_KEY=               # nur bei LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# --- OCR ---
OCR_DEFAULT_TOOL=auto         # 'auto', 'tesseract' oder 'mistral'
OCR_DPI=300
OCR_TESSERACT_LANG=deu+eng
OCR_DOMAIN_MATH=mistral       # Mistral für Mathematik (Formelerkennung)
OCR_DOMAIN_LANGUAGES=tesseract
OCR_DOMAIN_ECONOMICS=tesseract
MISTRAL_API_KEY=              # Pflichtfeld für Mathematikdomäne

# --- Logging ---
LOG_LEVEL=INFO

# --- Pfade (nicht ändern) ---
DATA_INPUT_PATH=data/input
DATA_OUTPUT_PATH=data/output
DATA_PARSED_PATH=data/parsed
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

### Einzeln

```bash
# LangChain Pipeline
python src/langchain_prototype/run_langchain.py

# LangGraph StateGraph
python src/langgraph_prototype/run_langgraph.py

# Hybrid (LC + LG + LC)
python src/hybrid_prototype/run_hybrid.py
```

### Mit Parametern

```bash
python src/langchain_prototype/run_langchain.py \
  --pdf data/input/math/equations_simple.pdf \
  --domain math \
  --variants 1 \
  --retries 3
```

### PYTHONPATH

Skripte setzen `src/` automatisch auf den Python-Pfad. Für direkte Importe ausserhalb der Skriptumgebung:

```bash
export PYTHONPATH=src
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

Führt alle drei Frameworks über alle drei Domänen aus (540 Einzelläufe). Ergebnisse werden als JSON-Reports mit Zeitstempel abgelegt:

```
data/output/evaluation/
└── [zeitstempel]/
    ├── report.json      # Aggregierte Metriken
    ├── report.md        # Lesbare Zusammenfassung
    └── segments/        # Einzelergebnisse pro Segment
```

### LangChain-Variantenvergleich (Pipeline vs. Orchestrator vs. Multi-Agent)

```bash
python scripts/pipeline_comparison.py
python scripts/pipeline_comparison.py data/input/math/equations_simple.pdf
python scripts/pipeline_comparison.py data/input/math/equations_simple.pdf --combos 1,3
```

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
│   └── hybrid_prototype/        # Dreiphasige Hybridarchitektur
├── frontend/                    # Next.js Demonstrationsumgebung
├── scripts/                     # Evaluations- und Hilfsskripte
├── data/
│   ├── input/                   # Test-PDFs (nach generate_test_pdfs.py)
│   ├── output/                  # Evaluationsergebnisse
│   └── parsed/                  # Zwischenergebnisse OCR
├── tests/
├── requirements.txt
├── .env.dev                     # Vorlage für Umgebungsvariablen
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
