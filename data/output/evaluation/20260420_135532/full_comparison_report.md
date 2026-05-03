# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-04-20 13:55:32  |  **Varianten/Segment:** 3  |  **Frameworks:** 3  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 146.9 | 95% | – | – |
| LangGraph | Node → StateGraph → Node | 412.1 | 100% | 2.2 | – |
| Hybrid | LC → LangGraph → LC | 239.5 | 96% | – | – |


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
| LangChain | 5 | 12 / 12 | 100% | 194.8 | mistral | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 263.3 | mistral | – | – | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 10 / 12 | 83% | 141.0 | mistral | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | 5 | 3 / 4 | 75% | 311.0 | mistral | – | – | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 12 / 12 | 100% | 130.6 | mistral | – | – | – |
| LangGraph | 4 | 12 / 12 | 100% | 242.1 | mistral | – | 0 | – |
| Hybrid | 4 | 4 / 4 | 100% | 169.9 | mistral | – | – | – |

**PDF:** `geometry_area.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 12 / 15 | 80% | 174.3 | mistral | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | 6 | 4 / 5 | 80% | 329.3 | mistral | – | – | – |

**PDF:** `percentage_ratio.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 14 / 15 | 93% | 183.1 | mistral | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | 6 | 5 / 5 | 100% | 276.6 | mistral | – | – | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `equations_simple.pdf`_

#### Segment 1 — `title` — _# Mathematik-Übungen_

**Original:**
```
# Mathematik-Übungen
```

**🔗 LangChain** — Klassifiziert als `general / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph:** ❌ Pipeline fehlgeschlagen — `Timeout nach 600s überschritten`

**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 2 — `task` — _Aufgabe 1: Löse die Gleichung: $2x + 5 = 13$_

**Original:**
```
Aufgabe 1: Löse die Gleichung: $2x + 5 = 13$
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 17$
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 17$
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 1: Löse die Gleichung: $3a + 7 = 17$
```
</details>


**🕸️  LangGraph:** ❌ Pipeline fehlgeschlagen — `Timeout nach 600s überschritten`

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

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $5\bigl(x + 4\bigr) \;-\; 3\bigl(x - 2\bigr)$
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $5(x + 3) - 3(x - 2)$
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $4(x + 3) - 3(x - 2)$
```
</details>


**🕸️  LangGraph:** ❌ Pipeline fehlgeschlagen — `Timeout nach 600s überschritten`

**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $5\bigl(x + 4\bigr)\;-\;6\bigl(x - 3\bigr)$
```
</details>


#### Segment 4 — `task` — _Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten: a = 5 cm, b = 7 cm…_

**Original:**
```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 5 cm, b = 7 cm, c = 9 cm
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 8 cm, b = 10 cm, c = 13 cm
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 8 cm, b = 10 cm, c = 12 cm
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
a = 8 cm, b = 10 cm, c = 13 cm
```
</details>


**🕸️  LangGraph:** ❌ Pipeline fehlgeschlagen — `Timeout nach 600s überschritten`

**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:
p = 8 cm, q = 10 cm, r = 13 cm
```
</details>


#### Segment 5 — `task` — _Aufgabe 4: Ein Kapital von 1000 € wird zu 3% Zinsen angelegt. Wie hoch ist das E…_

**Original:**
```
Aufgabe 4: Ein Kapital von 1000 € wird zu 3% Zinsen angelegt.
Wie hoch ist das Endkapital nach 5 Jahren?
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1500 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1300 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1400 € wird zu 4 % Zinsen angelegt.  
Wie hoch ist das Endkapital nach 7 Jahren?
```
</details>


**🕸️  LangGraph:** ❌ Pipeline fehlgeschlagen — `Timeout nach 600s überschritten`

**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1500 € wird zu 4 % Zinsen angelegt.  
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
| LangChain | 4 | 9 / 9 | 100% | 70.2 | tesseract | – | – | – |
| LangGraph | 4 | 9 / 9 | 100% | 302.6 | tesseract | – | 3 | – |
| Hybrid | 4 | 6 / 6 | 100% | 106.3 | tesseract | – | – | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 15 / 15 | 100% | 118.5 | tesseract | – | – | – |
| LangGraph | 6 | 15 / 15 | 100% | 574.7 | tesseract | – | 3 | – |
| Hybrid | 6 | 7 / 7 | 100% | 179.4 | tesseract | – | – | – |

**PDF:** `verb_conjugation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 12 / 12 | 100% | 184.1 | tesseract | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | 5 | 12 / 12 | 100% | 314.1 | tesseract | – | – | – |

**PDF:** `text_transformation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 12 / 12 | 100% | 135.9 | tesseract | – | – | – |
| LangGraph | 5 | 12 / 12 | 100% | 529.2 | tesseract | – | 3 | – |
| Hybrid | 5 | 10 / 10 | 100% | 222.7 | tesseract | – | – | – |

**PDF:** `word_forms.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 11 / 12 | 92% | 136.6 | tesseract | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | 5 | 9 / 9 | 100% | 222.0 | tesseract | – | – | – |


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

**🔗 LangChain** — Klassifiziert als `languages / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Schloss thront auf __ Anhöhe.
__ Studenten lernen in __ Bibliothek.
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Schloss thront über __ Berg.
__ Schüler laufen durch __ Park.
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Schloss thront auf __ Anhöhe.
__ Jugendliche laufen im __ Park.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Gebäude steht auf __ Berg.  
__ Kinder spielen in __ Park.
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Schloss liegt auf __ Anhöhe.  
__ Schüler sitzen in __ Aula.
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Turm ragt aus __ Ebene.  
__ Touristen wandern durch __ Wald.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 2/2 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Gebäude steht auf __ Berg.
__ Kinder spielen in __ Garten.
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

__ Turm ragt über __ Tal.
__ Jugendliche treffen sich in __ Park.
```
</details>


#### Segment 3 — `task` — _Aufgabe 2: Bilde das Perfekt:  Ich gehe in die Schule. — Er liest ein Buch. —_

**Original:**
```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. —
Er liest ein Buch. —
```

**🔗 LangChain** — Klassifiziert als `languages / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Sie fährt zum Markt. —  
Wir schreiben einen Brief. —
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Wir laufen zum Park. —  
Sie kocht eine Suppe. —
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich laufe zur Schule. —
Er blättert durch ein Buch. —
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich fahre zum Bahnhof. —
Sie malt ein Bild. —
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich kaufe im Supermarkt ein. —  
Der Hund jagt die Katze. —
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich besuche meine Großeltern. —  
Der Lehrer erklärt die Grammatik. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich fahre zum Bahnhof. —  
Sie malt ein Bild. —
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich kaufe im Supermarkt ein. —  
Du schreibst einen Brief. —
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich bestelle im Café einen Kaffee. —  
Wir planen den Urlaub. —
```
</details>


#### Segment 4 — `task` — _Aufgabe 3: Welche Wörter sind Synonyme?  schnell - rasch - langsam - zügig_

**Original:**
```
Aufgabe 3: Welche Wörter sind Synonyme?

schnell - rasch - langsam - zügig
```

**🔗 LangChain** — Klassifiziert als `languages / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink - geschwind - träge - hurtig
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink – hurtig – träge – geschwind
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink – hurtig – träge – eilig
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 3/3 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink – zügig – träge – schnell
```
</details>

<details>
<summary>Variante 2 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

flink – hurtig – träge – geschwind
```
</details>

<details>
<summary>Variante 3 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

eilig – flott – lahm – hurtig
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
| LangChain | – | – | – | – | – | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | – | – | – | – | – | – | – | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | – | – | – | – | – | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | – | – | – | – | – | – | – | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | – | – | – | – | – | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | – | – | – | – | – | – | – | – |

**PDF:** `cost_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | – | – | – | – | – | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | – | – | – | – | – | – | – | – |

**PDF:** `market_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | – | – | – | – | – | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | – | – | – | – | – | – | – | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `balance_sheet.pdf`_


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. Keine automatischen Beobachtungen generierbar (zu wenige erfolgreiche Runs oder unzureichende Datenbasis).

---

## 6. Qualitäts-Auffälligkeiten

_Keine automatisch erkannten Auffälligkeiten._
