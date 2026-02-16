# Copilot Instructions

## Projektüberblick

- Ziel: Vergleich von LangChain, LangGraph und Hybrid-Ansatz für automatisiertes Content-Rewriting (Masterarbeit).
- Zentrale Konfiguration und alle relevanten Pfade laufen über [src/common/config.py](src/common/config.py). Diese lädt **.env.dev** (nicht .env) und initialisiert Datenordner.

## Architektur & Datenfluss

- Eingabedaten: PDFs liegen unter [data/input/](data/input/). Ergebnisse werden nach [data/parsed/](data/parsed/) (OCR) und [data/output/](data/output/) geschrieben. Diese Ordner sind git-ignoriert.
- OCR-Research und Vergleichsskripte: [research/ocr_comparison/](research/ocr_comparison/). Die Entscheidung für Tesseract ist in [docs/ocr_comparison.md](docs/ocr_comparison.md) dokumentiert.
- Prototypen/Ansätze sind strikt getrennt: [src/langchain_prototype/](src/langchain_prototype/), [src/langgraph_prototype/](src/langgraph_prototype/), [src/hybrid_prototype/](src/hybrid_prototype/).
- Ergebnisdaten folgen dem Schema: `data/parsed/<tool>/<domain>/<file>.{json,txt}` (siehe [research/ocr_comparison/test_tesseract.py](research/ocr_comparison/test_tesseract.py)).

## Projektkonventionen & Patterns

- Research-Skripte fügen `src` manuell zu `sys.path` hinzu (siehe z.B. [research/ocr_comparison/test_tesseract.py](research/ocr_comparison/test_tesseract.py)). Folge diesem Muster für neue Skripte unter `research/`.
- Logging erfolgt zentral via `setup_logger()` aus [src/common/logger.py](src/common/logger.py).
- OCR- und LLM-Output wird immer in strukturierter Form (JSON/TXT) abgelegt, keine Mischformate.
- Prototypen sind modular aufgebaut: Trennung in `agents/`, `processing/`, `postprocessing/` etc. (siehe z.B. [src/hybrid_prototype/](src/hybrid_prototype/)).

## Workflows & wichtige Kommandos

- Python-Dependencies: `pip install -r requirements.txt` (siehe [requirements.txt](requirements.txt)).
- Tests: `pytest tests/` (siehe [README.md](README.md)).
- Frontend: `cd frontend && npm install && npm run dev` (siehe [README.md](README.md)).
- OCR-Tests: z.B. `python research/ocr_comparison/test_tesseract.py <PDF>`
- Vergleichsskripte: z.B. `python research/ocr_comparison/compare_results.py`

## Integrationen & externe Abhängigkeiten

- OCR/LLM: Tesseract, Mistral API (pixtral), Nougat (experimentell, siehe [docs/ocr_comparison.md](docs/ocr_comparison.md)). API-Keys aus **.env.dev** (siehe [src/common/config.py](src/common/config.py)).
- Für Nougat ist `albumentations<2.0.0` in [requirements.txt](requirements.txt) fixiert.

## Hinweise für AI Agents

- Nutze immer die zentrale Konfiguration aus [src/common/config.py](src/common/config.py) für Pfade und Umgebungsvariablen.
- Halte dich an die Output-Struktur in `data/parsed/` und `data/output/`.
- Neue Research-Skripte immer mit sys.path-Anpassung und zentralem Logging ausstatten.
- Bei neuen Prototypen/Modulen: Trenne strikt nach Ansatz (langchain, langgraph, hybrid) und folge der bestehenden Modulstruktur.

## Beispiele für typische Aufgaben

- OCR-Output vergleichen: `python research/ocr_comparison/compare_results.py`
- Neuen Prototypen anlegen: Siehe Struktur in [src/hybrid_prototype/](src/hybrid_prototype/) und [src/langchain_prototype/](src/langchain_prototype/)
- Logging in Skripten: `from src.common.logger import setup_logger; logger = setup_logger(__name__)`

---

Feedback zu unklaren oder fehlenden Abschnitten erwünscht!
