# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-03-22 19:25:25  |  **Varianten/Segment:** 1  |  **Frameworks:** 6  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 12.8 | 70% | – | – |
| LangGraph | Node → StateGraph → Node | 28.9 | 73% | – | – |
| Hybrid | LC → LangGraph → LC | 19.3 | 77% | – | – |
| Hybrid+Agent | LC → AgentExecutor → LC | 42.3 | 80% | 4.0 | 12.9 |
| Agent Orchestrator | Chain → AgentExecutor → Chain | 64.5 | 86% | 9.9 | 23.5 |
| Agent Multi-Step | Chain → 3× Agent → Chain | 40.1 | 81% | 4.1 | 14.4 |


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

**PDFs:** `math/equations_simple.pdf` | `math/equations_advanced.pdf` | `math/word_problems.pdf` | **Validator:** SymPy


### Metriken

**PDF:** `equations_simple.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 10.4 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 19.2 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 13.4 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 25.6 | mistral | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 4 / 4 | 100% | 33.3 | mistral | 14 | 5 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 34.7 | mistral | 13 | 4 | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 7 | 3 / 6 | 50% | 15.8 | mistral | – | – | – |
| LangGraph | 8 | 4 / 7 | 57% | 45.6 | mistral | – | – | – |
| Hybrid | 7 | 6 / 6 | 100% | 21.6 | mistral | – | – | – |
| Hybrid+Agent | 8 | 5 / 7 | 71% | 94.0 | mistral | 31 | 12 | 0 |
| Agent Orchestrator | 8 | 4 / 7 | 57% | 79.4 | mistral | 34 | 14 | – |
| Agent Multi-Step | 8 | 4 / 7 | 57% | 76.1 | mistral | 27 | 7 | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 11.3 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 25.2 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 14.2 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 29.8 | mistral | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 4 / 4 | 100% | 32.4 | mistral | 12 | 4 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 40.9 | mistral | 13 | 4 | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `equations_simple.pdf`_

#### Segment 1 — `title` — _Mathematik-Übungen_

**Original:**
```
Mathematik-Übungen
```

**🔗 LangChain** — Klassifiziert als `general / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `math / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**📋 Agent Multi-Step** — Klassifiziert als `math / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 2 — `task` — _Aufgabe 1: Löse die Gleichung $2x + 5 = 13$_

**Original:**
```
Aufgabe 1: Löse die Gleichung $2x + 5 = 13$
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $4p + 15 = 37$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $5a + 2 = 17$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $5z - 12 = -4$ nach $z$.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die Gleichung lautet: $\frac{3}{2}w - 2 = 8$.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $x + 3y = 14$ für $x$ in Abhängigkeit von $y$.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $7a + 12 = 35$
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
Aufgabe 2: Vereinfache: $5(z + 4) - 3(z - 2)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: $5(a + 6) - 3(b - 4)$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: $5a + 20 - 3b + 6$
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache den Ausdruck: $5a + 15 - 4b + 8$.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache den Ausdruck: $7(x + 6) - 4(y - 3)$
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: $5(a + 4) - 3(b - 2)$
```
</details>


#### Segment 4 — `task` — _Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten: a = 5 cm, b = 7 cm…_

**Original:**
```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten: a = 5 cm, b = 7 cm, c = 9 cm
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Berechne die Umkreiszahl eines Dreiecks, dessen Seitenlängen wie folgt gegeben sind: $x = 5$ cm, $y = 7$ cm, $z = 9$ cm
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Umfang eines Dreiecks, bei dem die Seitenlängen gegeben sind: $p = 5$, $q = 7$ und $r = 9$.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Umfang eines Dreiecks mit Seitenlängen von $a = 12$ m, $b = 15$ m und $c = 18$ m.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge des Umfangs eines Dreiecks, dessen Seitenlängen 5 Meter, 7 Meter und 9 Meter betragen.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Umkreislinie eines Dreiecks, dessen Seitenlängen gleich 12, 15 und 18 Meter sind.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Umkreislinie eines Dreiecks, dessen Seitenlängen gegeben sind:  p = 12 m, q = 15 m, r = 18 m.
```
</details>


#### Segment 5 — `task` — _Aufgabe 4: Ein Kapital von 1000 € wird zu 3% Zinsen angelegt. Wie hoch ist das E…_

**Original:**
```
Aufgabe 4: Ein Kapital von 1000 € wird zu 3% Zinsen angelegt. Wie hoch ist das Endkapital nach 5 Jahren?
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Betrag von 1250 € wird auf ein Konto mit einer jährlichen Verzinsung von 4,5% angelegt. Berechne das Kapital nach 6 Jahren unter Berücksichtigung dieser Zinsen.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 Schweizer Franken wird mit einem Zinssatz von 2,5 % pro Jahr verzinst. Berechne das Kapital nach 8 Jahren.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 Schweizer Franken wird jährlich mit einem Zinssatz von 2,8% verzinst. Berechnen Sie das Endguthaben nach sechs Jahren.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Kapital von 1500 Euro wird mit einem Zinssatz von 2,5 Prozent pro Jahr angelegt. Berechnen Sie das Kapital nach acht Jahren.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Sparinvestition von 1250 Euro wird zu einem Zinssatz von 4,5% pro Jahr verzinst. Berechne das Kapital nach einer Anlageperiode von 7 Jahren.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 2500 € wird zu 6,8% Zinsen für 3 Jahre verzinst. Berechne das Kapital, welches am Ende der Laufzeit verfügbar ist.
```
</details>


---

## 3.2 Domäne: Sprachen (`languages`)

**PDFs:** `languages/grammar_exercise.pdf` | `languages/sentence_construction.pdf` | `languages/verb_conjugation.pdf` | **Validator:** BERTScore


### Metriken

**PDF:** `grammar_exercise.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 1 / 3 | 33% | 18.6 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 22.4 | tesseract | – | – | – |
| Hybrid | 4 | 3 / 3 | 100% | 17.1 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 1 / 3 | 33% | 35.6 | tesseract | 11 | 8 | 0 |
| Agent Orchestrator | 4 | 2 / 3 | 67% | 69.5 | tesseract | 20 | 9 | – |
| Agent Multi-Step | 4 | 1 / 3 | 33% | 30.9 | tesseract | 12 | 3 | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 2 / 5 | 40% | 16.0 | tesseract | – | – | – |
| LangGraph | 6 | 2 / 5 | 40% | 36.6 | tesseract | – | – | – |
| Hybrid | 6 | 4 / 4 | 100% | 28.1 | tesseract | – | – | – |
| Hybrid+Agent | 6 | 5 / 5 | 100% | 48.0 | tesseract | 13 | 2 | 0 |
| Agent Orchestrator | 6 | 4 / 5 | 80% | 64.6 | tesseract | 26 | 11 | – |
| Agent Multi-Step | 6 | 4 / 5 | 80% | 38.7 | tesseract | 15 | 5 | – |

**PDF:** `verb_conjugation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | – | – | – | – | – | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | – | – | – | – | – | – | – | – |
| Hybrid+Agent | – | – | – | – | – | – | – | – |
| Agent Orchestrator | – | – | – | – | – | – | – | – |
| Agent Multi-Step | – | – | – | – | – | – | – | – |


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


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `languages / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**📋 Agent Multi-Step** — Klassifiziert als `languages / title` — 0/0 valide

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

□ Die Scheune thront auf □ einem Berg.
□ Die Jugendlichen toben in □ dem Park.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Setze die richtigen Artikel ein:

□ Burg thront auf □ Berg.
□ Jugendliche lachen in □ Park.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Villa thront auf einem Berg.
Jugendliche verspielten sich in einem Park.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Villa thront über dem Berg. Die Jugendlichen vergnügen sich auf dem Gelände.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `general / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die Aufgabe erfordert die präzise Einarbeitung der passenden Artikel in den folgenden Sätzen:

__ Die Häuser verteilen sich auf __ Berges.
__ Die jungen Jungen vergnügen sich in __ Scheune.
```
</details>


#### Segment 3 — `task` — _Aufgabe 2: Bilde das Perfekt:  Ich gehe in die Schule. —  er liest ein Buch. —_

**Original:**
```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. —

er liest ein Buch. —
```

**🔗 LangChain** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bilde das Perfekt:

Die Schüler gehen ins Klassenzimmer. —

Sie liest die Geschichte. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. – Er ging in die Schule.

Er liest ein Buch. – Er hat das Buch zu Ende gelesen.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**📋 Agent Multi-Step** — Klassifiziert als `general / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 4 — `task` — _Aufgabe 3: Welche Wörter sind Synonyme?  schnell - rasch - langsam - zügig_

**Original:**
```
Aufgabe 3: Welche Wörter sind Synonyme?

schnell - rasch - langsam - zügig
```

**🔗 LangChain** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 0/1 valide

<details>
<summary>Variante 1 — ❌ INVALID</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Welche Wörter sind Synonyme?

schnell – rasch – langsam – zügig

Erstelle eine inhaltlich äquivalente, aber DEUTLICH anders formulierte Variante.
```

> **Issues:** Länge weicht stark ab: 190 vs 63 Zeichen (Ratio: 3.02, erlaubt: 0.6-1.5)
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

Welche der folgenden Wortgruppen bildet eine Gruppe von Wörtern, die in ihrer Bedeutung nahe beieinanderliegen?
Bitte betrachten Sie die Begriffe: schnell – rasch – langsam – zügig.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
True.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme? schnell - rasch - langsam – zügig
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


---

## 3.3 Domäne: Wirtschaft (`economics`)

**PDFs:** `economics/balance_sheet.pdf` | `economics/income_statement.pdf` | `economics/investment_calculation.pdf` | **Validator:** ConsistencyCheck


### Metriken

**PDF:** `balance_sheet.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 2 / 3 | 67% | 11.7 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 21.9 | tesseract | – | – | – |
| Hybrid | 4 | 1 / 3 | 33% | 17.0 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 1 / 3 | 33% | 56.0 | tesseract | 18 | 10 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 44.5 | tesseract | 13 | 3 | – |
| Agent Multi-Step | 4 | 3 / 3 | 100% | 32.5 | tesseract | 9 | 3 | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 2 / 3 | 67% | 8.0 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 23.2 | tesseract | – | – | – |
| Hybrid | 4 | 1 / 3 | 33% | 12.5 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 3 / 3 | 100% | 21.8 | tesseract | 6 | 0 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 27.3 | tesseract | 11 | 3 | – |
| Agent Multi-Step | 4 | 3 / 3 | 100% | 28.4 | tesseract | 13 | 3 | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 10.4 | tesseract | – | – | – |
| LangGraph | 5 | 2 / 4 | 50% | 37.5 | tesseract | – | – | – |
| Hybrid | 9 | 4 / 8 | 50% | 30.2 | tesseract | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 27.7 | tesseract | 8 | 0 | 0 |
| Agent Orchestrator | 9 | 7 / 8 | 88% | 165.3 | tesseract | 58 | 30 | – |
| Agent Multi-Step | 5 | 3 / 4 | 75% | 39.1 | tesseract | 13 | 4 | – |


### Segment-Vergleich (Volltext)

_Segmentvergleich für erstes PDF: `balance_sheet.pdf`_

#### Segment 1 — `title` — _Bilanzanalyse - Fallstudie_

**Original:**
```
Bilanzanalyse - Fallstudie
```

**🔗 LangChain** — Klassifiziert als `general / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🔀 Hybrid** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `economics / title` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**📋 Agent Multi-Step** — Klassifiziert als `economics / title` — 0/0 valide

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
Unternehmen: NovaVision Solutions AG
Bilanz zum 31.08.2025:
VERMÖGEN:

Warenbestand: 90.000 SEK
Finanzanlagen: 65.000 NOK

Gesamt: 155.000 SEK
SCHULDEN:

Eigenkapital: 80.000 DKK
Kreditlinien: 70.000 EUR

Gesamt: 150.000 EUR
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaVision Solutions AG
Bilanz zum 31.12.2025:
AKTIVA:

Anlagevermögen: 90.000 SEK
Umlaufvermögen: 65.000 NOK

Gesamt: 155.000 SEK
PASSIVA:

Eigenkapital: 85.000 NOK
Fremdkapital: 70.000 SEK
Gesamt: 155.000 SEK
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `economics / data` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaVision Solutions AG\nBilanz zum 31.12.2025:\nAKTIVA:\n\nAnlagevermögen: 200.000 SEK\nUmlaufvermögen: 120.000 NOK\n\nGesamt: 320.000 SEK\nPASSIVA:\n\nEigenkapital: 240.000 NOK\nFremdkapital: 180.000 SEK\nGesamt: 420.000 SEK
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / data` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmensstammrechnung der NovaVision Solutions AG zum 31.12.2026:
VERMÖGEN:
Sachwerte: 95.000 SEK
Liquiditätsanlagen: 60.000 NOK
Gesamt: 155.000 SEK
SCHULDEN:
Eigenkapital: 85.000 SEK
Fremdkapital: 70.000 SEK
Gesamt: 155.000 SEK
```
</details>


#### Segment 3 — `task` — _Aufgabe 1: Berechne die Eigenkapitalquote._

**Original:**
```
Aufgabe 1: Berechne die Eigenkapitalquote.
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Anteil des Eigenkapitals am Gesamtvermögen eines Unternehmens.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Anteil des Eigenkapitals am gesamten Vermögen eines Unternehmens.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Ermittle den Anteil des Eigenkapitals am Gesamtvermögen.
\documentclass{article}

\begin{document}

Berechne den Anteil des Eigenkapitals am Gesamtvermögen.

Theoretischer Hintergrund:
Der Eigenkapitalanteil ist ein wichtiger Indikator für die Risikobereitschaft und die Kapitalstruktur eines Unternehmens. Er drückt das Verhältnis zwischen dem Eigenkapital und dem Gesamtvermögen aus. Dieses Verhältnis gibt Auskunft über den Grad der Selbstfinanzierung des Unternehmens und dessen Abhängigkeit von Fremdkapital. Die Berechnung erfolgt wie folgt:

$$ E_a = \frac{E}{T} $$

wobei:

*   $E_a$ der Eigenkapitalanteil ist (Ausgedruckt als Dezimalzahl zwischen 0 und 1 oder Prozentzahl)
*   $E$ das Eigenkapital ist (monetärer Wert)
*   $T$ das Gesamtvermögen ist (monetärer Wert)

Beispiel:
Ein Unternehmen besitzt ein Eigenkapital von 120.000€ und ein Gesamtvermögen von 600.000€.  Berechne den Eigenkapitalanteil.

Lösung:
$E_a = \frac{120.000}{600.000} = 0,2  = 20\%$

\end{document}
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Gesamtvermögen von Unternehmen "NovaTech Solutions".
```
</details>


#### Segment 4 — `task` — _Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 € Wie hoch ist der Gew…_

**Original:**
```
Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 € Wie hoch ist der Gewinn?
```

**🔗 LangChain** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma Stahlberg GmbH. Der Gesamtumsatz für das Geschäftsjahr lag bei 800.000 SEK, die Betriebskosten beliefen sich auf 720.000 NOK. Wie hoch war der Gewinn?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Erlöse der Stork GmbH summierten sich auf 800.000 SEK, die betrieblichen Ausgaben belaufenen sich auf 720.000 NOK. Wie hoch war der Jahresgewinn?
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Firma Stern GmbH erzielte Erlöse in Höhe von 600.000 SEK, während die Betriebskosten bei 530.000 NOK lagen. Wie hoch war der Jahresgewinn?
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Erlöse der Firma Svensson GmbH summierten sich zu 600.000 SEK, die Betriebskosten beliefen sich auf 520.000 SEK. Ermittle den Jahresgewinn.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma "Nordwind Solutions". Die Erlöse beliefen sich auf 600.000 SEK, die Betriebskosten auf 540.000 NOK. Wie hoch ist der Gewinn?
```
</details>


---

## 4. Agent-spezifische Analyse

_Diese Metriken sind nur für Frameworks mit AgentExecutor verfügbar._

### Tool-Call-Verteilung

| Framework | Domain | Tool-Calls | Retries | Halluziniert | Valid-Rate |
|-----------|--------|------------|---------|--------------|------------|
| Hybrid+Agent | math | 8 | 0 | 0 | 100% |
| Agent Orchestrator | math | 14 | 5 | None | 100% |
| Agent Multi-Step | math | 13 | 4 | None | 100% |
| Hybrid+Agent | math | 31 | 12 | 0 | 71% |
| Agent Orchestrator | math | 34 | 14 | None | 57% |
| Agent Multi-Step | math | 27 | 7 | None | 57% |
| Hybrid+Agent | math | 8 | 0 | 0 | 100% |
| Agent Orchestrator | math | 12 | 4 | None | 100% |
| Agent Multi-Step | math | 13 | 4 | None | 100% |
| Hybrid+Agent | languages | 11 | 8 | 0 | 33% |
| Agent Orchestrator | languages | 20 | 9 | None | 67% |
| Agent Multi-Step | languages | 12 | 3 | None | 33% |
| Hybrid+Agent | languages | 13 | 2 | 0 | 100% |
| Agent Orchestrator | languages | 26 | 11 | None | 80% |
| Agent Multi-Step | languages | 15 | 5 | None | 80% |
| Hybrid+Agent | economics | 18 | 10 | 0 | 33% |
| Agent Orchestrator | economics | 13 | 3 | None | 100% |
| Agent Multi-Step | economics | 9 | 3 | None | 100% |
| Hybrid+Agent | economics | 6 | 0 | 0 | 100% |
| Agent Orchestrator | economics | 11 | 3 | None | 100% |
| Agent Multi-Step | economics | 13 | 3 | None | 100% |
| Hybrid+Agent | economics | 8 | 0 | 0 | 100% |
| Agent Orchestrator | economics | 58 | 30 | None | 88% |
| Agent Multi-Step | economics | 13 | 4 | None | 75% |

**Halluzinations-Rate gesamt:** 0 / 406 Tool-Events = 0.0%

### Vergleich Retry-Effizienz: Agent vs. LangGraph

| Domain | LangGraph (Retries) | Hybrid+Agent (Retries) | Agent Orch. (Retries) |
|--------|---------------------|------------------------|----------------------|
| math | – | 0 | 5 |
| languages | – | 8 | 9 |
| economics | – | 10 | 3 |


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. **Agent Orchestrator** benötigte in Domain *math* Ø 221% mehr Zeit als **LangChain Pipeline** (33.3s vs. 10.4s).

2. **Hybrid+Agent vs. Hybrid** (math): Zeit +12.2s, Validation-Rate 0%. Identisches Pre/Postprocessing – Unterschied ausschliesslich Phase 2 (AgentExecutor vs. LangGraph StateGraph).

3. **LangGraph** (Conditional Edges): Ø 0.0 Retries/Run — **Agent Orchestrator** (LLM-Scratchpad): Ø 9.9 Retries/Run. LangGraph-Retries sind explizit im Graphen definiert; Agent-Retries entstehen implizit durch LLM-Entscheidung.

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Prompt-Leaks:**
- **LangGraph** / languages / V1: Prompt-Text im Output erkannt

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **LangGraph** / math / Seg 3 / V1: Ratio 31.2×
- **LangGraph** / math / Seg 7 / V1: Ratio 17.5×
- **Hybrid** / math / Seg 2 / V1: Ratio 6.9×
- **Hybrid** / math / Seg 3 / V1: Ratio 9.0×
- **Hybrid** / math / Seg 7 / V1: Ratio 19.8×
- **Hybrid+Agent** / math / Seg 3 / V1: Ratio 4.3×
- **Agent Multi-Step** / math / Seg 3 / V1: Ratio 13.8×
- **Agent Multi-Step** / math / Seg 7 / V1: Ratio 17.4×
- **LangGraph** / languages / Seg 4 / V1: Ratio 3.0×
- **LangGraph** / languages / Seg 3 / V1: Ratio 3.1×
- **LangGraph** / languages / Seg 5 / V1: Ratio 4.1×
- **LangGraph** / languages / Seg 6 / V1: Ratio 4.1×
- **Hybrid** / languages / Seg 3 / V1: Ratio 3.8×
- **Hybrid** / languages / Seg 5 / V1: Ratio 3.1×
- **Hybrid+Agent** / languages / Seg 5 / V1: Ratio 17.7×
- **Agent Orchestrator** / economics / Seg 3 / V1: Ratio 23.7×
- **LangGraph** / economics / Seg 2 / V1: Ratio 8.7×
- **Hybrid+Agent** / economics / Seg 3 / V1: Ratio 3.2×
- **Agent Orchestrator** / economics / Seg 3 / V1: Ratio 4.3×
- **Agent Multi-Step** / economics / Seg 3 / V1: Ratio 4.4×
  … und 8 weitere
