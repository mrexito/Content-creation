# CHANGES — Code-Bereinigung 2026-03-09

Dieses Dokument beschreibt alle Änderungen, die im Rahmen der systematischen
Code-Bereinigung vor der Thesis-Abgabe (22.05.2026) vorgenommen wurden.

## BERTScore Threshold-Kalibrierung (2026-04-12)

### BERT_THRESHOLD: 0.92 → 0.81
**Dateien:** `src/common/constants.py`, `CLAUDE.md`, `CHANGES.md`,
`scripts/compare_validation_improvements.py`

**Problem:** Der BERTScore-Threshold 0.92 (Vorstudie Anhang c, Tabelle 3)
war zu restriktiv für `bert-base-multilingual-cased` mit deutschen
Paraphrasen. Gute Varianten mit korrekter lexikalischer Variation
(z.B. Synonym-Austausch) wurden fälschlich abgelehnt.

**Methodik:** 24 Original-Variante-Paare aus dem LangChain-Vergleich
(11.04.2026) wurden manuell als GUT/SCHLECHT/GRENZFALL bewertet.
Für jeden Threshold von 0.70 bis 0.95 wurde der F1-Score der
binären Klassifikation (GUT vs. SCHLECHT) berechnet.

**Ergebnis:** Optimaler Threshold = 0.81 (maximaler F1-Score).

**Fix:** `BERT_THRESHOLD` in `constants.py` auf 0.81 gesetzt.
Alle Dokumentationsdateien aktualisiert.

---

## Neue Dateien

### `src/common/constants.py` (NEU)
Kanonische Konstanten für das gesamte Projekt:
- `DOMAIN_MATH = "mathematics"`, `DOMAIN_LANGUAGES`, `DOMAIN_ECONOMICS`, `DOMAIN_GENERAL`
- `VALID_DOMAINS` Set
- `BERT_THRESHOLD = 0.81` (empirisch kalibriert, gemeinsamer Schwellwert für alle drei Prototypen)
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
- Default auf `BERT_THRESHOLD = 0.81` geändert (aus constants.py, empirisch kalibriert)
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

---

## Prompt-Update: 30%-Zahlenvariation (Vorstudie Tabelle 1)

**Datum:** 2026-04-11

### Problem
Der Validator (`segment_validator.py`) prüft `MIN_NUMBER_CHANGE_MATH = 0.30` als
hartes Gate, aber die Rewriting-Prompts informierten das LLM nicht über diese
Mindestabweichung. Das LLM änderte Zahlen konservativ (~15%) und scheiterte
systematisch an der Validierung (LangChain: 25% statt erwartet ~80%+).

### Geänderte Dateien
1. `src/langchain_prototype/prompts/rewriting_prompts.py`
   - `REWRITING_MATH_SYSTEM_PROMPT`: "mindestens 30% Abweichung" ergänzt
   - `REWRITING_USER_PROMPT_TEMPLATE`: 30%-Hinweis für Mathematik ergänzt
   - `REWRITING_ECONOMICS_SYSTEM_PROMPT`: "mindestens 30%" statt "±50%"

2. `src/langchain_agent_prototype/orchestrator/agent.py`
   - Validierungskriterien (30%, BERTScore, Konsistenz) im System-Prompt
   - Hinweis: FINALE_VARIANTE muss vollständigen Text enthalten

3. `src/hybrid_agent_prototype/agent_phase.py`
   - Validierungskriterien im System-Prompt
   - Hinweis: RESULT muss vollständigen Text enthalten

4. `src/langchain_agent_prototype/multi_agent/pipeline.py`
   - Rewriter-Agent: Domain-spezifische Hinweise ergänzt

### Auswirkung
Alle bisherigen Evaluationsdaten müssen neu erhoben werden, da die Prompts
direkt die generierten Varianten beeinflussen. Betrifft alle 6 Prototypen
(alle nutzen `rewriting_prompts.py`; Agent-Varianten zusätzlich eigene Prompts).

---

## Fix: Zahlenänderungs-Check — Aufgabennummern-Filter

**Datum:** 2026-04-11

### Problem
Der 30%-Zahlenänderungs-Check in `segment_validator.py` extrahierte ALLE Zahlen
aus dem Text, inklusive Aufgabennummern ("Aufgabe 1:", "Aufgabe 3:"). Da
Aufgabennummern in Original und Variante identisch bleiben (0% Änderung),
drückten sie den Durchschnitt systematisch unter die 30%-Schwelle.

Konkretes Beispiel:
- "Aufgabe 1: 2x + 5 = 13" → "Aufgabe 1: 3a + 7 = 17"
- Ohne Filter: [1,2,5,13] vs [1,3,7,17] → avg 24% → INVALID
- Mit Filter:  [2,5,13] vs [3,7,17] → avg 40% → VALID

### Fix
Neue Hilfsfunktion `_extract_math_numbers()` in `segment_validator.py`:
- Entfernt Aufgabennummern-Patterns via Regex vor der Zahlenextraktion
- Fügt Debug-Daten (`numbers_original`, `numbers_variant`) zum Result hinzu
- Kernlogik (Durchschnitt ≥ 30%) bleibt unverändert

### Auswirkung
Alle Evaluationsdaten müssen neu erhoben werden.
