# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-04-20 16:36:44  |  **Varianten/Segment:** 1  |  **Frameworks:** 3  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 66.0 | 86% | – | – |
| LangGraph | Node → StateGraph → Node | 189.5 | 89% | 2.9 | – |
| Hybrid | LC → LangGraph → LC | 114.2 | 89% | – | – |


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
| LangChain | 5 | 4 / 4 | 100% | 56.2 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 193.8 | mistral | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 103.7 | mistral | – | – | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 68.3 | mistral | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 182.1 | mistral | – | 3 | – |
| Hybrid | 5 | 3 / 4 | 75% | 132.3 | mistral | – | – | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 4 / 4 | 100% | 67.0 | mistral | – | – | – |
| LangGraph | 4 | 4 / 4 | 100% | 70.4 | mistral | – | 0 | – |
| Hybrid | 4 | 4 / 4 | 100% | 57.8 | mistral | – | – | – |

**PDF:** `geometry_area.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 4 / 5 | 80% | 66.8 | mistral | – | – | – |
| LangGraph | 6 | 4 / 5 | 80% | 219.1 | mistral | – | 3 | – |
| Hybrid | 6 | 4 / 5 | 80% | 140.8 | mistral | – | – | – |

**PDF:** `percentage_ratio.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 77.6 | mistral | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 201.7 | mistral | – | 3 | – |
| Hybrid | 6 | 5 / 5 | 100% | 121.0 | mistral | – | – | – |


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
Aufgabe 1: Löse die Gleichung: $3a + 7 = 17$
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
Aufgabe 1: Löse die Gleichung: $3a + 8 = 20$
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
Aufgabe 2: Vereinfache: $4\bigl(x + 3\bigr) \;-\; 3\bigl(x - 2\bigr)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $4\bigl(x+3\bigr)\;-\;3\bigl(x-2\bigr)$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $4\bigl(x + 3\bigr) \;-\; 3\bigl(x - 2\bigr)$
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
d = 7 cm, e = 10 cm, f = 12 cm
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 7 cm, b = 10 cm, c = 12 cm
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 8 cm, b = 10 cm, c = 12 cm
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
Aufgabe 4: Ein Kapital von 1300 € wird zu 4 % Zinsen angelegt.
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1400 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1400 € wird zu 5% Zinsen angelegt.  
Wie hoch ist das Endkapital nach 8 Jahren?
```
</details>


---

## 3.2 Domäne: Sprachen (`languages`)

**PDFs:** `languages/grammar_exercise.pdf` | `languages/sentence_construction.pdf` | `languages/verb_conjugation.pdf` | `languages/text_transformation.pdf` | `languages/word_forms.pdf` | **Validator:** BERTScore


### Metriken

**PDF:** `grammar_exercise.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 3 / 3 | 100% | 34.9 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 76.3 | tesseract | – | 3 | – |
| Hybrid | 4 | 3 / 3 | 100% | 53.9 | tesseract | – | – | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 5 / 5 | 100% | 48.5 | tesseract | – | – | – |
| LangGraph | 6 | 5 / 5 | 100% | 133.9 | tesseract | – | 3 | – |
| Hybrid | 6 | 5 / 5 | 100% | 58.4 | tesseract | – | – | – |

**PDF:** `verb_conjugation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 70.3 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 228.2 | tesseract | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 114.3 | tesseract | – | – | – |

**PDF:** `text_transformation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 61.5 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 153.2 | tesseract | – | 3 | – |
| Hybrid | 5 | 4 / 4 | 100% | 104.1 | tesseract | – | – | – |

**PDF:** `word_forms.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 4 / 4 | 100% | 54.9 | tesseract | – | – | – |
| LangGraph | 4 | 4 / 4 | 100% | 59.6 | tesseract | – | 0 | – |
| Hybrid | 4 | 4 / 4 | 100% | 47.3 | tesseract | – | – | – |


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

__ Bauernhof steht auf __ Berg.
__ Schüler spielen in __ Park.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Bungalow steht auf __ Anhöhe.
__ Schüler spielen in __ Park.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Turm ragt über __ Anhöhe.  
__ Schüler laufen durch __ Park.
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

Ich schwimme im See. —
Sie malt ein Bild. —
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich fahre zur Arbeit. —
Sie kocht eine Suppe. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Wir wandern im Wald. —  
Sie malt ein Bild. —
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

flink – hurtig – träge – eilig
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink – hurtig – träge – geschwind
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink - geschwind - träge - hurtig
```
</details>


---

## 3.3 Domäne: Wirtschaft (`economics`)

**PDFs:** `economics/balance_sheet.pdf` | `economics/income_statement.pdf` | `economics/investment_calculation.pdf` | `economics/cost_analysis.pdf` | `economics/market_analysis.pdf` | **Validator:** ConsistencyCheck


### Metriken

**PDF:** `balance_sheet.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 2 / 3 | 67% | 57.5 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 187.4 | tesseract | – | 4 | – |
| Hybrid | – | – | – | – | – | – | – | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 73.2 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 262.8 | tesseract | – | 4 | – |
| Hybrid | – | – | – | – | – | – | – | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 1 / 4 | 25% | 84.7 | tesseract | – | – | – |
| LangGraph | 5 | 2 / 4 | 50% | 293.1 | tesseract | – | 4 | – |
| Hybrid | 5 | 2 / 4 | 50% | 163.7 | tesseract | – | – | – |

**PDF:** `cost_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 4 / 5 | 80% | 81.0 | tesseract | – | – | – |
| LangGraph | 6 | 4 / 5 | 80% | 300.8 | tesseract | – | 4 | – |
| Hybrid | 6 | 3 / 4 | 75% | 225.8 | tesseract | – | – | – |

**PDF:** `market_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 3 / 5 | 60% | 87.0 | tesseract | – | – | – |
| LangGraph | 6 | 4 / 5 | 80% | 280.7 | tesseract | – | 4 | – |
| Hybrid | 6 | 4 / 5 | 80% | 162.0 | tesseract | – | – | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `balance_sheet.pdf`_

#### Segment 1 — `title` — _Bilanzanalyse - Fallstudie_

**Original:**
```
Bilanzanalyse - Fallstudie
```

**🔗 LangChain** — Klassifiziert als `general / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `general / unknown` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🔀 Hybrid:** ❌ Pipeline fehlgeschlagen — `Preprocessing fehlgeschlagen: ['Klassifizierung fehlgeschlagen']`

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
Bilanz zum 31.12.2025:

**AKTIVA**

- Anlagevermögen: 210.000 CHF  
- Umlaufvermögen: 108.000 CHF  

Gesamt: 318.000 CHF  

**PASSIVA**

- Eigenkapital: 168.000 CHF  
- Fremdkapital: 150.000 CHF  

Gesamt: 318.000 CHF
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / theory` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: InnoTech AG  
Bilanz zum 31.12.2024:

**AKTIVA**

- Anlagevermögen: 210.000 CHF  
- Umlaufvermögen: 110.000 CHF  

**Gesamt:** 320.000 CHF  

**PASSIVA**

- Eigenkapital: 170.000 CHF  
- Fremdkapital: 150.000 CHF  

**Gesamt:** 320.000 CHF
```
</details>


**🔀 Hybrid:** ❌ Pipeline fehlgeschlagen — `Preprocessing fehlgeschlagen: ['Klassifizierung fehlgeschlagen']`

#### Segment 3 — `task` — _Aufgabe 1: Berechne die Eigenkapitalquote._

**Original:**
```
Aufgabe 1: Berechne die Eigenkapitalquote.
```

**🔗 LangChain** — Klassifiziert als `economics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 0/1 valide

<details>
<summary>Variante 1 — ❌ INVALID</summary>

```
Der Jahresabschluss der NovaTech AG zeigt ein Eigenkapital von 14 Millionen CHF bei einer Bilanzsumme von 35 Millionen CHF. Ermitteln Sie den Eigenkapitalanteil am Gesamtvermögen.
```

> **Issues:** Länge weicht stark ab: 179 vs 42 Zeichen (Ratio: 4.26, erlaubt: 0.3–3.5)
</details>


**🔀 Hybrid:** ❌ Pipeline fehlgeschlagen — `Preprocessing fehlgeschlagen: ['Klassifizierung fehlgeschlagen']`

#### Segment 4 — `task` — _Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 € Wie hoch ist der Gew…_

**Original:**
```
Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 €
Wie hoch ist der Gewinn?
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Der Umsatz betrug 680 000 € und die Kosten 610 000 €.  
Wie hoch ist der Gewinn?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Jahreserlös der NovaTech AG betrug 780.000 CHF, die Betriebsausgaben lagen bei 630.000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>


**🔀 Hybrid:** ❌ Pipeline fehlgeschlagen — `Preprocessing fehlgeschlagen: ['Klassifizierung fehlgeschlagen']`


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. Keine automatischen Beobachtungen generierbar (zu wenige erfolgreiche Runs oder unzureichende Datenbasis).

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **LangGraph** / economics / Seg 3 / V1: Ratio 4.3×
- **LangChain** / economics / Seg 3 / V1: Ratio 3.4×
- **LangGraph** / economics / Seg 4 / V1: Ratio 3.1×
- **LangGraph** / economics / Seg 3 / V1: Ratio 8.4×
- **LangGraph** / economics / Seg 4 / V1: Ratio 4.4×
- **Hybrid** / economics / Seg 3 / V1: Ratio 3.0×
