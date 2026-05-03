# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-04-21 20:28:53  |  **Varianten/Segment:** 1  |  **Frameworks:** 2  |  **Domains:** 1

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 70.1 | 61% | – | – |
| Hybrid | LC → LangGraph → LC | 143.3 | 77% | – | – |


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

## 3.3 Domäne: Wirtschaft (`economics`)

**PDFs:** `economics/balance_sheet.pdf` | `economics/income_statement.pdf` | `economics/investment_calculation.pdf` | `economics/cost_analysis.pdf` | `economics/market_analysis.pdf` | **Validator:** ConsistencyCheck


### Metriken

**PDF:** `balance_sheet.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 2 / 3 | 67% | 47.5 | tesseract | – | – | – |
| Hybrid | 4 | 2 / 3 | 67% | 93.5 | tesseract | – | – | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 63.1 | tesseract | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 133.2 | tesseract | – | – | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 1 / 4 | 25% | 72.6 | tesseract | – | – | – |
| Hybrid | – | – | – | – | – | – | – | – |

**PDF:** `cost_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 3 / 5 | 60% | 82.9 | tesseract | – | – | – |
| Hybrid | 6 | 3 / 5 | 60% | 193.7 | tesseract | – | – | – |

**PDF:** `market_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 4 / 5 | 80% | 84.5 | tesseract | – | – | – |
| Hybrid | 6 | 4 / 5 | 80% | 152.9 | tesseract | – | – | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `balance_sheet.pdf`_

#### Segment 1 — `title` — _Bilanzanalyse - Fallstudie_

**Original:**
```
Bilanzanalyse - Fallstudie
```

**🔗 LangChain** — Klassifiziert als `general / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🔀 Hybrid** — Klassifiziert als `economics / task` — 0/0 valide

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
Unternehmen: NovaTech AG  
Bilanz zum 31.12.2025:

**AKTIVA**

- Anlagevermögen: 210.000 CHF  
- Umlaufvermögen: 115.000 CHF  

Gesamt: 325.000 CHF  

**PASSIVA**

- Eigenkapital: 175.000 CHF  
- Fremdkapital: 150.000 CHF  

Gesamt: 325.000 CHF
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 0/1 valide

<details>
<summary>Variante 1 — ❌ INVALID</summary>

```
**Unternehmen:** NovaTech AG  
**Bilanz zum 31.03.2025**

**AKTIVA**  

- Anlagevermögen: 210 000 CHF  
- Umlaufvermögen: 120 000 CHF  

Gesamt: 330 000 CHF  

**PASSIVA**  

- Eigenkapitalanteil: 170 000 CHF  
- Fremdkapital: 160 000 CHF  

Gesamt: 330 000 CHF
```

> **Issues:** Anzahl Zahlen stark unterschiedlich: 7 vs 13
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
Die XYZ AG weist ein Eigenkapital von 12 Mio CHF und ein Gesamtkapital von 28 Mio CHF aus. Bestimme den Eigenkapitalanteil am Gesamtvermögen.
```

> **Issues:** Semantische Ähnlichkeit zu gering (Wirtschaft): BERTScore 0.715 < 0.72
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil, wenn das Eigenkapital 140 000 CHF und das Gesamtkapital 560 000 CHF beträgt.
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
Der Jahreserlös der NovaTech AG betrug 730.000 CHF, die Betriebsausgaben beliefen sich auf 610.000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Der Jahreserlös der AlpenTech GmbH beträgt 780 000 CHF, die Betriebsausgaben belaufen sich auf 630 000 CHF. Wie hoch ist der Jahresüberschuss?
```
</details>



---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. **Hybrid** erzielte in der Domain *economics* die höchste Validation-Rate (100%).

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **LangChain** / economics / Seg 3 / V1: Ratio 3.4×
- **LangChain** / economics / Seg 3 / V1: Ratio 3.2×
- **LangChain** / economics / Seg 4 / V1: Ratio 3.4×
- **LangChain** / economics / Seg 3 / V1: Ratio 3.9×
- **LangChain** / economics / Seg 4 / V1: Ratio 6.6×
