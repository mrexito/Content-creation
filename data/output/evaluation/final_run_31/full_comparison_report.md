# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-04-22 18:33:33  |  **Varianten/Segment:** 1  |  **Frameworks:** 3  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 64.6 | 89% | – | – |
| LangGraph | Node → StateGraph → Node | 203.9 | 91% | 3.3 | – |
| Hybrid | LC → LangGraph → LC | 113.2 | 84% | – | – |


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
| LangChain | 5 | 4 / 4 | 100% | 56.5 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 171.9 | mistral | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 113.6 | mistral | – | – | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 69.8 | mistral | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 180.4 | mistral | – | 3 | – |
| Hybrid | 5 | 3 / 4 | 75% | 145.2 | mistral | – | – | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 4 / 4 | 100% | 63.1 | mistral | – | – | – |
| LangGraph | 4 | 4 / 4 | 100% | 59.4 | mistral | – | 0 | – |
| Hybrid | 4 | 4 / 4 | 100% | 51.2 | mistral | – | – | – |

**PDF:** `geometry_area.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 4 / 5 | 80% | 66.3 | mistral | – | – | – |
| LangGraph | 6 | 4 / 5 | 80% | 220.8 | mistral | – | 3 | – |
| Hybrid | 6 | 4 / 5 | 80% | 141.8 | mistral | – | – | – |

**PDF:** `percentage_ratio.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 65.9 | mistral | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 201.0 | mistral | – | 3 | – |
| Hybrid | 6 | 5 / 5 | 100% | 120.6 | mistral | – | – | – |


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
Aufgabe 1: Löse die Gleichung: $3a + 8 = 18$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 17$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 17$
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
Aufgabe 2: Vereinfache: $5(a + 3) - 3(a - 2)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $4\bigl(x+3\bigr)-3\bigl(x-2\bigr)$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $4(x + 3) - 3(x - 2)$
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
a = 7 cm, b = 10 cm, c = 13 cm
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 8 cm, b = 10 cm, c = 12 cm
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 7 cm, b = 10 cm, c = 13 cm
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
Aufgabe 4: Ein Kapital von 1500 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1400 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1300 € wird zu 4 % Zinsen angelegt.  
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
| LangChain | 4 | 3 / 3 | 100% | 37.2 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 87.9 | tesseract | – | 3 | – |
| Hybrid | 4 | 3 / 3 | 100% | 47.4 | tesseract | – | – | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 45.5 | tesseract | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 144.6 | tesseract | – | 3 | – |
| Hybrid | 6 | 5 / 5 | 100% | 69.4 | tesseract | – | – | – |

**PDF:** `verb_conjugation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 74.7 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 223.7 | tesseract | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 117.1 | tesseract | – | – | – |

**PDF:** `text_transformation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 60.5 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 162.6 | tesseract | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 81.3 | tesseract | – | – | – |

**PDF:** `word_forms.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 61.3 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 217.1 | tesseract | – | 5 | – |
| Hybrid | 5 | 3 / 4 | 75% | 77.8 | tesseract | – | – | – |


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

__ Schloss thront auf __ Berg.
__ Schüler laufen in __ Spielplatz.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Schloss thront auf __ Anhöhe.  
__ Schüler lernen in __ Bibliothek.
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

Ich laufe zum Supermarkt. —  
Er schreibt einen Brief. —
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich laufe zum Gymnasium. —
Sie malt ein Bild. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich fahre zum Bahnhof. —  
Sie kauft im Markt ein. —
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

flink – hurtig – träge – geschwind
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

gigantisch – gewaltig – klein – enorm
```
</details>


---

## 3.3 Domäne: Wirtschaft (`economics`)

**PDFs:** `economics/balance_sheet.pdf` | `economics/income_statement.pdf` | `economics/investment_calculation.pdf` | `economics/cost_analysis.pdf` | `economics/market_analysis.pdf` | **Validator:** ConsistencyCheck


### Metriken

**PDF:** `balance_sheet.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 3 / 3 | 100% | 51.1 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 194.1 | tesseract | – | 4 | – |
| Hybrid | 4 | 3 / 3 | 100% | 95.8 | tesseract | – | – | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 78.0 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 262.2 | tesseract | – | 4 | – |
| Hybrid | 5 | 4 / 4 | 100% | 99.2 | tesseract | – | – | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 2 / 4 | 50% | 79.2 | tesseract | – | – | – |
| LangGraph | 5 | 2 / 4 | 50% | 287.0 | tesseract | – | 4 | – |
| Hybrid | 5 | 1 / 4 | 25% | 154.8 | tesseract | – | – | – |

**PDF:** `cost_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 4 / 5 | 80% | 81.0 | tesseract | – | – | – |
| LangGraph | 6 | 3 / 5 | 60% | 421.2 | tesseract | – | 6 | – |
| Hybrid | 6 | 1 / 4 | 25% | 213.3 | tesseract | – | – | – |

**PDF:** `market_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 3 / 4 | 75% | 79.1 | tesseract | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 225.2 | tesseract | – | 3 | – |
| Hybrid | 6 | 4 / 5 | 80% | 169.0 | tesseract | – | – | – |


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

*Gesamt:* 318.000 CHF  

**PASSIVA**

- Eigenkapital: 160.000 CHF  
- Fremdkapital: 158.000 CHF  

*Gesamt:* 318.000 CHF
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: InnovaTech AG  
Bilanz zum 31.12.2025:

**AKTIVA**

- Anlagevermögen: 210.000 CHF  
- Umlaufvermögen: 108.000 CHF  

**Gesamt:** 318.000 CHF  

**PASSIVA**

- Eigenkapital: 170.000 CHF  
- Fremdkapital: 148.000 CHF  

**Gesamt:** 318.000 CHF
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaTech AG  
Bilanz zum 31.12.2024:

**AKTIVA:**  

Anlagevermögen: 210.000 CHF  
Umlaufvermögen: 110.000 CHF  

Gesamt: 320.000 CHF  

**PASSIVA:**  

Eigenkapital: 160.000 CHF  
Fremdkapital: 160.000 CHF  

Gesamt: 320.000 CHF
```
</details>


#### Segment 3 — `task` — _Aufgabe 1: Berechne die Eigenkapitalquote._

**Original:**
```
Aufgabe 1: Berechne die Eigenkapitalquote.
```

**🔗 LangChain** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil, wenn das Unternehmen einen Bilanzwert von 1 200 000 CHF und ein Eigenkapital von 420 000 CHF ausweist.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimme den Eigenkapitalanteil, wenn das Eigenkapital 13 Millionen CHF und das Gesamtkapital 38 Millionen CHF beträgt.
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimme den Eigenkapitalanteil, wenn das Eigenkapital 210 000 CHF und das Gesamtkapital 560 000 CHF beträgt.
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
Der Jahreserlös der Nordwind GmbH betrug 780.000 CHF, die Betriebsausgaben lagen bei 640.000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Jahreserlös der Nordsee GmbH betrug 720.000 CHF, die Betriebsausgaben lagen bei 300.000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Jahreserlös der AlpineTech GmbH betrug 730 000 CHF, die Betriebsausgaben lagen bei 640 000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>



---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. Keine automatischen Beobachtungen generierbar (zu wenige erfolgreiche Runs oder unzureichende Datenbasis).

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **LangChain** / economics / Seg 3 / V1: Ratio 3.2×
- **LangGraph** / economics / Seg 4 / V1: Ratio 3.1×
- **Hybrid** / economics / Seg 2 / V1: Ratio 3.2×
- **Hybrid** / economics / Seg 3 / V1: Ratio 3.1×
- **LangChain** / economics / Seg 3 / V1: Ratio 3.1×
- **LangChain** / economics / Seg 4 / V1: Ratio 5.7×
- **LangGraph** / economics / Seg 3 / V1: Ratio 3.4×
- **LangGraph** / economics / Seg 5 / V1: Ratio 3.1×
- **Hybrid** / economics / Seg 3 / V1: Ratio 3.8×
- **Hybrid** / economics / Seg 4 / V1: Ratio 4.4×
- **Hybrid** / economics / Seg 5 / V1: Ratio 3.7×
