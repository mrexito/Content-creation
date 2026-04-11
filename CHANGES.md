# CHANGES — Code-Bereinigung 2026-03-09

Dieses Dokument beschreibt alle Änderungen, die im Rahmen der systematischen
Code-Bereinigung vor der Thesis-Abgabe (22.05.2026) vorgenommen wurden.

---

## Neue Dateien

### `src/common/constants.py` (NEU)
Kanonische Konstanten für das gesamte Projekt:
- `DOMAIN_MATH = "mathematics"`, `DOMAIN_LANGUAGES`, `DOMAIN_ECONOMICS`, `DOMAIN_GENERAL`
- `VALID_DOMAINS` Set
- `BERT_THRESHOLD = 0.92` (gemeinsamer Schwellwert für alle drei Prototypen)
- `normalize_domain(domain: str) -> str` — normalisiert `'math'` → `'mathematics'` etc.

---

## Kritische Bug-Fixes

### Issue 1: LangGraph — Retry-State-Bug (Infinite Loop Fix)
**Dateien:** `src/langgraph_prototype/nodes/validation_node.py`,
`src/langgraph_prototype/edges/__init__.py`

**Problem:** LangGraph Edge-Funktionen persistieren keine State-Mutationen.
Die `retry_counts`-Inkrementierung und `current_phase = 'validation_failed'`
wurden in der Edge-Funktion `should_retry_after_validation()` gesetzt — beide
wurden von LangGraph still verworfen. Folge: `retry_count` blieb immer 0,
`is_retry` in `rewriting_node` war immer `False`.

**Fix:**
- `validation_node.py`: `retry_counts` inkrementieren und `current_phase` setzen
  (`'validation_failed'` bei Retry-Bedarf, `'validation_complete'` sonst)
- `edges/__init__.py`: Reine Routing-Funktion (keinerlei State-Mutationen)

Diese Architektur-Entscheidung ist analog zu `hybrid_prototype/graph/validation_node.py`
(dort bereits 2026-03-01 gefixt).

---

### Issue 2: Mistral OCR — Falscher API-Endpunkt
**Dateien:** `src/common/ocr_handler.py`,
`research/ocr_comparison/test_mistral_ocr.py`,
`docs/ocr_comparison.md`

**Problem:** `_ocr_mistral()` verwendete Bilder als Eingabe (seitenweise via pdf2image).
Das OCR-Script `test_mistral_ocr.py` nutzte noch `client.chat.complete(model="pixtral-12b-2409", ...)`
(Vision-Chat statt dediziertem OCR-Endpunkt).

**Fix:**
- `ocr_handler.py`: Bleibt bildbasiert (Mistral OCR unterstützt `image_url`),
  nutzt jetzt `client.ocr.process(model="mistral-ocr-latest", ...)`
- `test_mistral_ocr.py`: Neu auf `client.ocr.process()` mit PDF-direkt-Upload
  (`document_url: data:application/pdf;base64,...`) — kein pdf2image-Umweg
- `docs/ocr_comparison.md`: Modellname korrigiert auf `mistral-ocr-latest`,
  Hinweis auf Verfügbarkeit (März 2025) ergänzt

---

### Issue 3: Domain-Name-Inkonsistenz
**Dateien:** `src/common/ocr_handler.py`, `src/common/constants.py`,
`scripts/evaluate_all_domains.py`

**Problem:** OCR-Handler nutzte `'math'` als Schlüssel in `domain_preferences`,
alle Validierungsknoten und Rewriting-Nodes erwarten `'mathematics'` (LLM-Ausgabe).

**Fix:**
- `ocr_handler.py`: `domain_preferences` auf `DOMAIN_MATH = "mathematics"` umgestellt
- `_choose_tool()`: `normalize_domain()` aufgerufen vor Lookup
- `evaluate_all_domains.py`: `normalize_domain(config['domain'])` beim Pipeline-Aufruf

---

## Weitere Korrekturen

### Issue 4: Temperature-Paradox (BERTScore-Regression bei Retry)
**Dateien:** `src/langgraph_prototype/nodes/rewriting_node.py`,
`src/hybrid_prototype/graph/rewriting_node.py`,
`src/langchain_prototype/chains/rewriting_chain.py`

**Problem:** Bei Retry-Schleifen wurde die Temperature erhöht (+0.1 pro Retry).
Für `DOMAIN_LANGUAGES` ist das kontraproduktiv: BERTScore erfordert semantische
Nähe zum Original; höhere Temperature erzeugt mehr Abweichung → Score sinkt → Endlosschleife.

**Fix:** Domain-aware Temperature-Strategie:
```python
if domain == DOMAIN_LANGUAGES:
    temperature = 0.7  # Konstant für BERTScore-Stabilität
else:
    temperature = base + (retry_count * 0.05) + (attempt * 0.05)
    temperature = min(temperature, 1.0)
```

### Issue 5: BERTScore Default-Threshold Inkonsistenz
**Datei:** `src/common/validators/bert_validator.py`

**Problem:** `validate_paraphrase()` default `min_threshold=0.92`, aber
LangChain/LangGraph rufen explizit mit `0.7` auf. Hybrid-Prototype rief ohne
Argument auf — nutzte damit den strengeren 0.92-Schwellwert (Bug!).

**Fix:**
- Default auf `BERT_THRESHOLD = 0.92` geändert (aus constants.py)
- Verwirrende `threshold_passed: float(F1[0]) >= 0.92` in `calculate_similarity()`
  entfernt (war inkonsistent mit tatsächlicher Validierungslogik)

### Issue 6: print()-Statements in src/
**Datei:** `src/common/ocr_handler.py`

Alle `print()`-Statements entfernt → `logger.debug/info/warning/error`

### Issue 7: Leere OCR-Response nicht abgefangen
**Datei:** `src/common/ocr_handler.py`

`_ocr_mistral()` prüft jetzt `if not response.pages:` und gibt leeren String
zurück (statt Exception beim Iterieren über leere Liste).

### Issue 8: evaluate_all_domains.py — Exception-Logging und Hybrid
**Datei:** `scripts/evaluate_all_domains.py`

- `logger.exception()` statt `print(f"❌ Exception: ...")` in allen except-Blöcken
- Neuer Import: `from common.logger import setup_logger`
- `run_hybrid_test()` Funktion ergänzt
- Hybrid in `main()` eingebunden (Total: 9 Tests statt 6)

### Issue 9: Segmentierungs-Debug-Log
**Dateien:** `src/langchain_prototype/chains/segmentation_chain.py`,
`src/langgraph_prototype/nodes/segmentation_node.py`

Debug-Log am Ende der Segmentierung:
```python
logger.debug(f"Segmentierung: {len(segments)} Segmente aus {len(text)} Zeichen")
```
Kommentar: Beide Implementierungen teilen identische Prompts aus
`langchain_prototype.prompts.segmentation_prompts` — methodisch korrekt.

---

## Open Questions (dokumentiert, nicht gefixt)

1. ~~**LangChain Math-Validierung — Tolerance:**~~ **GELÖST** — `ValidationChain` ruft
   jetzt `validate_segment()` aus `src/common/validators/segment_validator.py` auf.
   Alle Prototypen (LangChain, LangGraph, Hybrid, Agent) nutzen identische
   Validierungslogik mit `EQUATION_COUNT_TOLERANCE = 1` aus `constants.py`.

2. **Tesseract für Math:** OCR-Handler bevorzugt Mistral für `DOMAIN_MATH`.
   Falls kein API-Key → Tesseract-Fallback, LaTeX-Erkennung dann eingeschränkt.

---

## Verifikation

```bash
python scripts/generate_test_pdfs.py  # ✅ Alle 3 PDFs erstellt
python scripts/test_validators.py      # ✅ Alle Tests grün
```
