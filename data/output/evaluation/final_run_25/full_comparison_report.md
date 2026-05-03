# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-04-22 01:11:16  |  **Varianten/Segment:** 1  |  **Frameworks:** 3  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 64.7 | 83% | – | – |
| LangGraph | Node → StateGraph → Node | 196.4 | 88% | 3.2 | – |
| Hybrid | LC → LangGraph → LC | 115.4 | 89% | – | – |


## 2. Architektur-Übersicht

| Framework | Phase 1 | Phase 2 | Phase 3 |
|-----------|---------|---------|---------|
| **LangChain** | Chain | Chain | Chain |
| **LangGraph** | Node | StateGraph | Node |
| **Hybrid** | LangChain | LangGraph | LangChain |
| **Hybrid+Agent** | LangChain | AgentExecutor | LangChain |
| **Agent Orchestrator** | Chain | AgentExecutor | Chain |
| **Agent Multi-Step** | Chain | 3× AgentExecutor | Chain |



---

## 3. Ergebnisse pro Domain

---

## 3.1 Domäne: Mathematik (`math`)

**PDFs:** `math/equations_simple.pdf` | `math/equations_advanced.pdf` | `math/word_problems.pdf` | `math/geometry_area.pdf` | `math/percentage_ratio.pdf` | **Validator:** SymPy


### Metriken

**PDF:** `equations_simple.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 59.0 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 171.2 | mistral | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 106.2 | mistral | – | – | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 63.3 | mistral | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 201.1 | mistral | – | 3 | – |
| Hybrid | 5 | 3 / 4 | 75% | 129.7 | mistral | – | – | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 4 / 4 | 100% | 66.6 | mistral | – | – | – |
| LangGraph | 4 | 4 / 4 | 100% | 60.1 | mistral | – | 0 | – |
| Hybrid | 5 | 4 / 4 | 100% | 128.2 | mistral | – | – | – |

**PDF:** `geometry_area.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 4 / 5 | 80% | 68.4 | mistral | – | – | – |
| LangGraph | 6 | 4 / 5 | 80% | 217.5 | mistral | – | 3 | – |
| Hybrid | 6 | 4 / 5 | 80% | 144.5 | mistral | – | – | – |

**PDF:** `percentage_ratio.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 83.1 | mistral | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 187.7 | mistral | – | 3 | – |
| Hybrid | 6 | 5 / 5 | 100% | 102.8 | mistral | – | – | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `equations_simple.pdf`_

#### Segment 1 — `title` — _# Mathematik-Übungen_

**Original:**
```
# Mathematik-Übungen
```

**🔗 LangChain** — Klassifiziert als `general / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 2 — `task` — _Aufgabe 1: Löse die Gleichung: $2x + 5 = 13$_

**Original:**
```
Aufgabe 1: Löse die Gleichung: $2x + 5 = 13$
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 18$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 18$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 17$
```
</details>


#### Segment 3 — `task` — _Aufgabe 2: Vereinfache: $3(x + 2) - 2(x - 1)$_

**Original:**
```
Aufgabe 2: Vereinfache: $3(x + 2) - 2(x - 1)$
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $5(x + 3) - 3(x - 2)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $5\bigl(x + 3\bigr) - 5\bigl(x - 2\bigr)$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $4\bigl(x + 3\bigr) \;-\; 3\bigl(x - 2\bigr)$
```
</details>


#### Segment 4 — `task` — _Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten: a = 5 cm, b = 7 cm…_

**Original:**
```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 5 cm, b = 7 cm, c = 9 cm
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 8 cm, b = 10 cm, c = 13 cm
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 8 cm, b = 11 cm, c = 13 cm
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 7 cm, b = 10 cm, c = 12 cm
```
</details>


#### Segment 5 — `task` — _Aufgabe 4: Ein Kapital von 1000 € wird zu 3% Zinsen angelegt. Wie hoch ist das E…_

**Original:**
```
Aufgabe 4: Ein Kapital von 1000 € wird zu 3% Zinsen angelegt.
Wie hoch ist das Endkapital nach 5 Jahren?
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1350 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1500 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Betrag von 1300 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


---

## 3.2 Domäne: Sprachen (`languages`)

**PDFs:** `languages/grammar_exercise.pdf` | `languages/sentence_construction.pdf` | `languages/verb_conjugation.pdf` | `languages/text_transformation.pdf` | `languages/word_forms.pdf` | **Validator:** BERTScore


### Metriken

**PDF:** `grammar_exercise.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 2 / 3 | 67% | 33.2 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 101.2 | tesseract | – | 4 | – |
| Hybrid | 4 | 3 / 3 | 100% | 40.7 | tesseract | – | – | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 50.8 | tesseract | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 141.3 | tesseract | – | 3 | – |
| Hybrid | 6 | 5 / 5 | 100% | 70.9 | tesseract | – | – | – |

**PDF:** `verb_conjugation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 99.4 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 195.9 | tesseract | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 104.7 | tesseract | – | – | – |

**PDF:** `text_transformation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 58.8 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 166.3 | tesseract | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 94.1 | tesseract | – | – | – |

**PDF:** `word_forms.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 4 / 4 | 100% | 55.4 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 144.2 | tesseract | – | 3 | – |
| Hybrid | 4 | 4 / 4 | 100% | 48.8 | tesseract | – | – | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `grammar_exercise.pdf`_

#### Segment 1 — `title` — _Grammatik-Übungen_

**Original:**
```
Grammatik-Übungen
```

**🔗 LangChain** — Klassifiziert als `general / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🔀 Hybrid** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 2 — `task` — _Aufgabe 1: Setze die richtigen Artikel ein:  __ Haus steht auf __ Hügel. __ Kind…_

**Original:**
```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Haus steht auf __ Hügel.
__ Kinder spielen in __ Garten.
```

**🔗 LangChain** — Klassifiziert als `languages / task` — 0/1 valide

<details>
<summary>Variante 1 — ❌ INVALID</summary>

```
__ Villa thront auf __ Anhöhe.
__ Jugendliche tollen in __ Park.
```

> **Issues:** BERTScore 0.787 unter Schwellwert 0.81
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Villa thront auf __ Anhöhe.
__ Jugendliche toben in __ Park.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Gebäude steht auf __ Anhöhe.
__ Kinder spielen in __ Park.
```
</details>


#### Segment 3 — `task` — _Aufgabe 2: Bilde das Perfekt:  Ich gehe in die Schule. — Er liest ein Buch. —_

**Original:**
```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. —
Er liest ein Buch. —
```

**🔗 LangChain** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich fahre zur Universität. —  
Sie schreibt einen Brief. —
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Wir laufen zum Park. —
Sie malt ein Bild. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Wir laufen zum Gymnasium. —
Sie schreibt einen Brief. —
```
</details>


#### Segment 4 — `task` — _Aufgabe 3: Welche Wörter sind Synonyme?  schnell - rasch - langsam - zügig_

**Original:**
```
Aufgabe 3: Welche Wörter sind Synonyme?

schnell - rasch - langsam - zügig
```

**🔗 LangChain** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink - hurtig - träge - eilig
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink – geschwind – träge – eilig
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink – hurtig – träge – eilig
```
</details>


---

## 3.3 Domäne: Wirtschaft (`economics`)

**PDFs:** `economics/balance_sheet.pdf` | `economics/income_statement.pdf` | `economics/investment_calculation.pdf` | `economics/cost_analysis.pdf` | `economics/market_analysis.pdf` | **Validator:** ConsistencyCheck


### Metriken

**PDF:** `balance_sheet.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 2 / 3 | 67% | 49.7 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 190.4 | tesseract | – | 4 | – |
| Hybrid | 4 | 3 / 3 | 100% | 98.3 | tesseract | – | – | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 2 / 4 | 50% | 65.1 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 224.4 | tesseract | – | 3 | – |
| Hybrid | 5 | 3 / 4 | 75% | 148.0 | tesseract | – | – | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 1 / 4 | 25% | 73.7 | tesseract | – | – | – |
| LangGraph | 5 | 1 / 4 | 25% | 365.9 | tesseract | – | 5 | – |
| Hybrid | 5 | 1 / 4 | 25% | 196.5 | tesseract | – | – | – |

**PDF:** `cost_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 87.0 | tesseract | – | – | – |
| LangGraph | 6 | 4 / 5 | 80% | 351.1 | tesseract | – | 5 | – |
| Hybrid | 6 | 4 / 5 | 80% | 161.2 | tesseract | – | – | – |

**PDF:** `market_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 57.2 | tesseract | – | – | – |
| LangGraph | 6 | 3 / 5 | 60% | 228.2 | tesseract | – | 3 | – |
| Hybrid | 6 | 4 / 4 | 100% | 156.3 | tesseract | – | – | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `balance_sheet.pdf`_

#### Segment 1 — `title` — _Bilanzanalyse - Fallstudie_

**Original:**
```
Bilanzanalyse - Fallstudie
```

**🔗 LangChain** — Klassifiziert als `general / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🔀 Hybrid** — Klassifiziert als `economics / theory` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 2 — `data` — _Unternehmen: TechStart GmbH Bilanz zum 31.12.2024: AKTIVA:  Anlagevermögen: 150.…_

**Original:**
```
Unternehmen: TechStart GmbH
Bilanz zum 31.12.2024:
AKTIVA:

Anlagevermögen: 150.000 €
Umlaufvermögen: 80.000 €

Gesamt: 230.000 €
PASSIVA:

Eigenkapital: 120.000 €
Fremdkapital: 110.000 €
Gesamt: 230.000 €
```

**🔗 LangChain** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: InnoTech AG  
Bilanz zum 31.12.2024:

**AKTIVA:**  

- Anlagevermögen: 210.000 €  
- Umlaufvermögen: 120.000 €  

*Gesamt:* 330.000 €

**PASSIVA:**  

- Eigenkapitalanteil: 160.000 €  
- Fremdkapitalbestand: 170.000 €  

*Gesamt:* 330.000 €
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaTech AG  
Bilanz zum 31.12.2025:

**AKTIVA**

- Anlagevermögen: 210.000 CHF  
- Umlaufvermögen: 108.000 CHF  

Gesamt: 320.000 CHF  

**PASSIVA**

- Eigenkapital: 170.000 CHF  
- Fremdkapital: 150.000 CHF  

Gesamt: 320.000 CHF
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaTech AG  
Bilanz zum 31.12.2024:

**AKTIVA:**  

- Anlagevermögen: 200.000 CHF  
- Umlaufvermögen: 110.000 CHF  

**Gesamt:** 310.000 CHF  

**PASSIVA:**  

- Eigenkapital: 160.000 CHF  
- Fremdkapital: 150.000 CHF  

**Gesamt:** 310.000 CHF
```
</details>


#### Segment 3 — `task` — _Aufgabe 1: Berechne die Eigenkapitalquote._

**Original:**
```
Aufgabe 1: Berechne die Eigenkapitalquote.
```

**🔗 LangChain** — Klassifiziert als `economics / task` — 0/1 valide

<details>
<summary>Variante 1 — ❌ INVALID</summary>

```
Der Eigenkapitalanteil der fiktiven Nordsee GmbH beträgt 180 000 CHF, das Gesamtkapital liegt bei 620 000 CHF. Bestimme den Eigenkapitalanteil am Gesamtkapital.
```

> **Issues:** Semantische Ähnlichkeit zu gering (Wirtschaft): BERTScore 0.715 < 0.72 | Länge weicht stark ab: 160 vs 42 Zeichen (Ratio: 3.81, erlaubt: 0.3–3.5)
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Eigenkapitalanteil beträgt 142 000 CHF und das gesamte Kapital 368 000 CHF. Ermitteln Sie den Eigenkapitalanteil am Gesamtvermögen.
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimme den Eigenkapitalanteil der AlphaTech AG, wenn das Eigenkapital 560 000 CHF und das Gesamtkapital 1 400 000 CHF beträgt.
```
</details>


#### Segment 4 — `task` — _Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 € Wie hoch ist der Gew…_

**Original:**
```
Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 €
Wie hoch ist der Gewinn?
```

**🔗 LangChain** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Jahreserlös der AlpineTech AG betrug 720 000 CHF und die Betriebsausgaben lagen bei 540 000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Jahreserlös der AlpineTech GmbH betrug 770 000 CHF, die Betriebsausgaben beliefen sich auf 620 000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Jahreserlös der Beispiel GmbH betrug 820.000 CHF und die Betriebsausgaben 620.000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>



---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. Keine automatischen Beobachtungen generierbar (zu wenige erfolgreiche Runs oder unzureichende Datenbasis).

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **LangChain** / economics / Seg 3 / V1: Ratio 3.8×
- **LangGraph** / economics / Seg 3 / V1: Ratio 3.2×
- **Hybrid** / economics / Seg 3 / V1: Ratio 3.0×
- **Hybrid** / economics / Seg 3 / V1: Ratio 3.1×
- **LangChain** / economics / Seg 3 / V1: Ratio 4.9×
- **LangChain** / economics / Seg 4 / V1: Ratio 4.3×
- **LangGraph** / economics / Seg 3 / V1: Ratio 4.6×
- **LangGraph** / economics / Seg 4 / V1: Ratio 4.9×
- **Hybrid** / economics / Seg 3 / V1: Ratio 3.6×
- **Hybrid** / economics / Seg 4 / V1: Ratio 3.5×
- **Hybrid** / economics / Seg 5 / V1: Ratio 3.4×
- **LangGraph** / economics / Seg 3 / V1: Ratio 3.1×
