# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-04-22 20:56:50  |  **Varianten/Segment:** 1  |  **Frameworks:** 3  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 65.1 | 80% | – | – |
| LangGraph | Node → StateGraph → Node | 204.4 | 90% | 3.4 | – |
| Hybrid | LC → LangGraph → LC | 107.4 | 90% | – | – |


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
| LangChain | 5 | 4 / 4 | 100% | 61.9 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 174.6 | mistral | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 62.4 | mistral | – | – | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 57.4 | mistral | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 194.1 | mistral | – | 3 | – |
| Hybrid | 5 | 3 / 4 | 75% | 122.2 | mistral | – | – | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 61.0 | mistral | – | – | – |
| LangGraph | 4 | 4 / 4 | 100% | 59.7 | mistral | – | 0 | – |
| Hybrid | 4 | 4 / 4 | 100% | 49.4 | mistral | – | – | – |

**PDF:** `geometry_area.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 4 / 5 | 80% | 71.3 | mistral | – | – | – |
| LangGraph | 6 | 4 / 5 | 80% | 233.7 | mistral | – | 3 | – |
| Hybrid | 6 | 4 / 5 | 80% | 148.8 | mistral | – | – | – |

**PDF:** `percentage_ratio.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 76.1 | mistral | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 249.4 | mistral | – | 4 | – |
| Hybrid | 6 | 5 / 5 | 100% | 129.5 | mistral | – | – | – |


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


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 8 = 18$
```
</details>


#### Segment 2 — `task` — _Aufgabe 1: Löse die Gleichung: $2x + 5 = 13$_

**Original:**
```
Aufgabe 1: Löse die Gleichung: $2x + 5 = 13$
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 18$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 19$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $5(x + 3) - 4(x - 2)$
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
Aufgabe 2: Vereinfache: $5(a + 3)\;-\;3(a - 2)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $4(a + 3) - 3(a - 2)$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
p = 7 cm, q = 10 cm, r = 13 cm
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
a = 7 cm, b = 10 cm, c = 12 cm
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 8 cm, b = 10 cm, c = 13 cm
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1 400 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 8 Jahren?
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
Aufgabe 4: Ein Kapital von 1300 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1300 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🔀 Hybrid:** _(kein Segment #5)_

---

## 3.2 Domäne: Sprachen (`languages`)

**PDFs:** `languages/grammar_exercise.pdf` | `languages/sentence_construction.pdf` | `languages/verb_conjugation.pdf` | `languages/text_transformation.pdf` | `languages/word_forms.pdf` | **Validator:** BERTScore


### Metriken

**PDF:** `grammar_exercise.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 3 / 3 | 100% | 30.5 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 87.9 | tesseract | – | 3 | – |
| Hybrid | 4 | 3 / 3 | 100% | 48.4 | tesseract | – | – | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 51.4 | tesseract | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 135.1 | tesseract | – | 3 | – |
| Hybrid | 6 | 5 / 5 | 100% | 68.5 | tesseract | – | – | – |

**PDF:** `verb_conjugation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 90.9 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 219.0 | tesseract | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 126.1 | tesseract | – | – | – |

**PDF:** `text_transformation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 50.8 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 164.1 | tesseract | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 84.4 | tesseract | – | – | – |

**PDF:** `word_forms.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 72.1 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 176.5 | tesseract | – | 4 | – |
| Hybrid | 5 | 4 / 4 | 100% | 59.3 | tesseract | – | – | – |


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

**🔗 LangChain** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Gebäude steht auf __ Berg.
__ Kinder spielen in __ Park.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Baum steht auf __ Anhöhe.
__ Vögel singen in __ Wald.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Schloss thront auf __ Anhöhe.  
__ Schüler lesen in __ Bibliothek.
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

Ich gehe zur Bibliothek. —  
Sie liest einen Artikel. —
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich fahre zum Bahnhof. —  
Sie schreibt einen Brief. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich laufe zum Bahnhof. —
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

heiß – warm – kalt – kühl
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink - geschwind - träge - hurtig
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
| LangChain | 4 | 2 / 3 | 67% | 52.2 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 215.7 | tesseract | – | 5 | – |
| Hybrid | 4 | 3 / 3 | 100% | 94.4 | tesseract | – | – | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 2 / 4 | 50% | 65.2 | tesseract | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 355.8 | tesseract | – | 6 | – |
| Hybrid | 5 | 4 / 4 | 100% | 124.1 | tesseract | – | – | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 1 / 4 | 25% | 82.8 | tesseract | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 216.2 | tesseract | – | 3 | – |
| Hybrid | 5 | 2 / 4 | 50% | 148.5 | tesseract | – | – | – |

**PDF:** `cost_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 3 / 4 | 75% | 68.9 | tesseract | – | – | – |
| LangGraph | 6 | 3 / 5 | 60% | 347.4 | tesseract | – | 5 | – |
| Hybrid | 6 | 4 / 5 | 80% | 159.8 | tesseract | – | – | – |

**PDF:** `market_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 3 / 5 | 60% | 84.2 | tesseract | – | – | – |
| LangGraph | 6 | 4 / 5 | 80% | 237.4 | tesseract | – | 3 | – |
| Hybrid | 6 | 3 / 5 | 60% | 184.7 | tesseract | – | – | – |


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
Unternehmen: NovaTech AG  
Bilanz zum 31.12.2024:

**AKTIVA**

- Anlagevermögen: 210.000 CHF  
- Umlaufvermögen: 108.000 CHF  

**Gesamt:** 318.000 CHF  

**PASSIVA**

- Eigenkapitalanteil: 165.000 CHF  
- Fremdkapitalquote: 153.000 CHF  

**Gesamt:** 318.000 CHF
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaTech AG  
Bilanz zum 31.12.2024:

**AKTIVA:**  

- Anlagevermögen: 215.000 CHF  
- Umlaufvermögen: 115.000 CHF  

Gesamt: 330.000 CHF  

**PASSIVA:**  

- Eigenkapitalanteil: 165.000 CHF  
- Fremdkapitalquote: 165.000 CHF  

Gesamt: 330.000 CHF
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaTech AG  
Bilanz zum 31.12.2024:

**AKTIVA:**  

- Anlagevermögen: 210.000 CHF  
- Umlaufvermögen: 108.000 CHF  

Gesamt: 318.000 CHF  

**PASSIVA:**  

- Eigenkapital: 160.000 CHF  
- Fremdkapital: 158.000 CHF  

Gesamt: 318.000 CHF
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
Die Beta AG weist ein Eigenkapital von 140 000 CHF und ein Gesamtkapital von 560 000 CHF aus. Ermitteln Sie den Eigenkapitalanteil am Gesamtvermögen.
```

> **Issues:** Länge weicht stark ab: 149 vs 42 Zeichen (Ratio: 3.55, erlaubt: 0.3–3.5)
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimme den Eigenkapitalanteil, wenn das Eigenkapital 140 000 CHF und das Gesamtkapital 350 000 CHF beträgt.
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimme den Eigenkapitalanteil der Beispiel GmbH, wenn das Eigenkapital 140 000 CHF und die Bilanzsumme 560 000 CHF beträgt.
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
Der Jahreserlös der AlpineTech AG betrug 770.000 CHF, die Betriebsausgaben lagen bei 610.000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Jahreserlös der AlpineTech GmbH betrug 680 000 CHF, die Betriebsausgaben beliefen sich auf 590 000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Der Umsatz betrug 650.000 € die Kosten 300.000 €
Wie hoch ist der Gewinn?
```
</details>



---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. Keine automatischen Beobachtungen generierbar (zu wenige erfolgreiche Runs oder unzureichende Datenbasis).

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **LangChain** / economics / Seg 3 / V1: Ratio 3.5×
- **LangChain** / economics / Seg 4 / V1: Ratio 5.5×
- **LangGraph** / economics / Seg 3 / V1: Ratio 3.0×
- **LangChain** / economics / Seg 3 / V1: Ratio 5.2×
- **LangChain** / economics / Seg 4 / V1: Ratio 4.0×
- **LangChain** / economics / Seg 5 / V1: Ratio 3.3×
- **LangGraph** / economics / Seg 3 / V1: Ratio 3.3×
- **LangGraph** / economics / Seg 5 / V1: Ratio 4.6×
- **Hybrid** / economics / Seg 3 / V1: Ratio 3.1×
- **Hybrid** / economics / Seg 4 / V1: Ratio 4.9×
