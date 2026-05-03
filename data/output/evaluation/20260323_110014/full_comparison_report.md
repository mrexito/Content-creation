# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-03-23 11:00:14  |  **Varianten/Segment:** 1  |  **Frameworks:** 6  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 13.4 | 83% | – | – |
| LangGraph | Node → StateGraph → Node | 33.1 | 82% | – | – |
| Hybrid | LC → LangGraph → LC | 20.8 | 81% | – | – |
| Hybrid+Agent | LC → AgentExecutor → LC | 32.0 | 94% | 1.5 | 9.4 |
| Agent Orchestrator | Chain → AgentExecutor → Chain | 62.6 | 82% | 5.6 | 18.7 |
| Agent Multi-Step | Chain → 3× Agent → Chain | 39.7 | 85% | 3.8 | 12.9 |


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
| LangChain | 5 | 4 / 4 | 100% | 10.2 | mistral | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 29.9 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 14.7 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 27.3 | mistral | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 4 / 4 | 100% | 108.2 | mistral | 32 | 4 | – |
| Agent Multi-Step | 5 | 3 / 4 | 75% | 35.2 | mistral | 14 | 4 | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 3 / 4 | 75% | 11.3 | mistral | – | – | – |
| LangGraph | – | – | – | – | – | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 19.1 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 31.2 | mistral | 10 | 0 | 0 |
| Agent Orchestrator | 5 | 3 / 4 | 75% | 62.5 | mistral | 20 | 6 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 42.5 | mistral | 16 | 4 | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 12.4 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 21.5 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 13.6 | mistral | – | – | – |
| Hybrid+Agent | 5 | 3 / 4 | 75% | 33.4 | mistral | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 3 / 4 | 75% | 32.5 | mistral | 12 | 4 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 40.8 | mistral | 15 | 4 | – |


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


#### Segment 2 — `task` — _Aufgabe 1: Löse die Gleichung: $2x + 5 = 13$_

**Original:**
```
Aufgabe 1: Löse die Gleichung: $2x + 5 = 13$
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung: $5a + 2 = 17$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung: $3y - 7 = 16$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die folgende Gleichung: $4a + 10 = 26$
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die Gleichung $3a - 7 = 10$ lässt sich wie folgt lösen:
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung: $7a - 3 = 28$
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 3 — `task` — _Aufgabe 2: Vereinfache: $3(x + 2) - 2(x - 1)$_

**Original:**
```
Aufgabe 2: Vereinfache: $3(x + 2) - 2(x - 1)$
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: $5(z + 4) - 3(z - 2)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: $5(a + 7) - 3(b - 4)$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: 5a + 15 - 4b + 8
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache den Ausdruck: $5a + 15 - 4b + 8$
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache den Ausdruck: 3x - x + 2y + y
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
Berechne den Umfang eines Dreiecks, bei dem die Längen der Seiten gegeben sind: $p= 5$ m, $q= 7$ m und $r= 9$ m.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 0/1 valide

<details>
<summary>Variante 1 — ❌ INVALID</summary>

```
Berechne die Umfangs eines Dreiecks, dessen Seitenlängen gegeben sind als:

$a = 12 \text{ cm}$, $b = 15 \text{ cm}$ und $c = 18 \text{ cm}$.

Theorie:
Der Umfang eines Dreiecks ist die Summe der Längen seiner Seiten. Für ein Dreieck mit den Seitenlängen $a$, $b$ und $c$ gilt:
$$U = a + b + c$$

Gegeben sind die Seitenlängen $a$, $b$ und $c$ eines Dreiecks. Berechne den Umfang des Dreiecks.
```

> **Issues:** Länge weicht stark ab: 393 vs 90 Zeichen (Ratio: 4.37, erlaubt: 0.5-2.0)
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Umkreislinie eines Dreiecks, wenn dir die Seitenlängen gegeben sind: $p = 5$, $q = 7$ und $r = 9$.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Summe der Längen der Seiten eines Dreiecks, wenn die Seitenlängen wie folgt gegeben sind: p = 5 Meter, q = 7 Meter und r = 9 Meter.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge des Umfangs eines Dreiecks, dessen Seitenlängen gegeben sind: d = 12 Meter, e = 15 Meter und f = 18 Meter.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge des Umfangs eines Dreiecks, dessen Seitenlängen gegeben sind als: $x = 5$ m, $y = 7$ m und $z = 9$ m.
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
Aufgabe 4: Eine Investition von 850 Euro wird auf ein Konto mit einer jährlichen Verzinsung von 4,2% angelegt.  Berechne die Summe nach einem Anlagezeitraum von 6 Jahren.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Vorsorgeinvestition von 1250 € wird mit einer jährlichen Rendite von 4,5% verzinst. Berechne das Kapital nach 6 Jahren angespart.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Betrag von 1500 Euro wird auf eine Anlage mit einer jährlichen Verzinsung von 2,5 Prozent investiert. Berechnen Sie das Kapital nach sechs Jahren unter Berücksichtigung des Zinseszinses.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 Dollar wird zu einem Zinssatz von 2,5 % verzinst. Berechnen Sie das Ergebnis des Kapitals nach einem Zeitraum von sechs Jahren.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Betrag von 1250 € wird zu 6,5 Prozent Zinsen verwahrt. Berechne das Endkapital nach 3 Jahren.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Betrag von 1500 DM wird mit einem Zinssatz von 2,5 % projahr verzinst. Berechne das Kapital nach 8 Jahren.
```
</details>


---

## 3.2 Domäne: Sprachen (`languages`)

**PDFs:** `languages/grammar_exercise.pdf` | `languages/sentence_construction.pdf` | `languages/verb_conjugation.pdf` | **Validator:** BERTScore


### Metriken

**PDF:** `grammar_exercise.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 1 / 3 | 33% | 12.9 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 21.7 | tesseract | – | – | – |
| Hybrid | 4 | 3 / 3 | 100% | 17.7 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 3 / 3 | 100% | 31.4 | tesseract | 10 | 2 | 0 |
| Agent Orchestrator | 4 | 2 / 3 | 67% | 31.1 | tesseract | 6 | 2 | – |
| Agent Multi-Step | 4 | 1 / 3 | 33% | 28.9 | tesseract | 12 | 3 | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 2 / 5 | 40% | 17.1 | tesseract | – | – | – |
| LangGraph | 6 | 2 / 5 | 40% | 35.8 | tesseract | – | – | – |
| Hybrid | 6 | 4 / 4 | 100% | 26.1 | tesseract | – | – | – |
| Hybrid+Agent | 6 | 4 / 5 | 80% | 55.8 | tesseract | 17 | 8 | 0 |
| Agent Orchestrator | 6 | 5 / 5 | 100% | 97.0 | tesseract | 36 | 16 | – |
| Agent Multi-Step | 6 | 4 / 5 | 80% | 40.2 | tesseract | 15 | 5 | – |

**PDF:** `verb_conjugation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 27.4 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 60.9 | tesseract | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 38.7 | tesseract | – | – | – |
| Hybrid+Agent | – | – | – | – | – | – | – | – |
| Agent Orchestrator | 5 | 1 / 4 | 25% | 63.9 | tesseract | 8 | 3 | – |
| Agent Multi-Step | 5 | 3 / 4 | 75% | 67.5 | tesseract | 12 | 4 | – |


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

□ Die Villa thront auf □ Berg.
□ Die Schüler versammeln sich in □ Park.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:
□ Die Villa thront auf □ dem Berg.
□ Die Kinder verspielten sich in □ dem Garten.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Villa thront auf dem Berg.
Die Kleinkinder toben im Garten.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Auf der Anhöhe türmen sich zahlreiche Wohnhäuser auf.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Villa thront über dem Berg.
Die Jugendlichen vergnügen sich auf dem Feld.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `general / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Schreibe die passenden Artikel ein, um folgende Sätze zu vervollständigen:

__Das Haus__ thront auf __einem__ Berg.
__Die Kinder__ toben in __dem__ Garten.
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


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:
Der Schüler betritt die Universität. —
Die Studentin studiert ein Lehrbuch. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. – Er ging zu dem Unterricht.

Er liest ein Buch. – Er hat das Buch gerade durchgelesen.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Er verschlang die Seiten eines Buches. / Er taumelte umher, während er ein Buch las. / Die Geschichte zog ihn in ihren Bann, als er sie laut vorlas. / Der Band entfaltete sich vor seinen Augen, während er still und konzentriert las.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `general / task` — 0/0 valide

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
Aufgabe 3: Welche Wörter sind Synonyme?

Welche der genannten Begriffe weisen eine ähnliche Bedeutung auf?
Betrachten Sie die folgenden Optionen: schnell, rasch, langsam, zügig.
```

> **Issues:** Länge weicht stark ab: 177 vs 73 Zeichen (Ratio: 2.42, erlaubt: 0.6-1.5)
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

Welche der folgenden Wortgruppen bildet ein stimmiges Gefüge von gleichbedachten Begriffen?

Wähle aus: blitzschnell – gewaltig rasch – bedächtig langsam – flink zügig

Erläutere deine Antwort und begründe, warum die gewählten Wörter als Synonyme betrachtet werden können.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die korrekten Artikel ein:

schnell – rasch – langsam – zügig
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Begriffe bedeuten dasselbe? schnell – rasch – langsam – zügig
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
| LangChain | 3 | 2 / 2 | 100% | 6.5 | tesseract | – | – | – |
| LangGraph | 3 | 2 / 2 | 100% | 15.0 | tesseract | – | – | – |
| Hybrid | 4 | 1 / 3 | 33% | 21.9 | tesseract | – | – | – |
| Hybrid+Agent | 3 | 2 / 2 | 100% | 18.3 | tesseract | 6 | 1 | 0 |
| Agent Orchestrator | 3 | 2 / 2 | 100% | 21.4 | tesseract | 8 | 2 | – |
| Agent Multi-Step | 3 | 2 / 2 | 100% | 17.9 | tesseract | 6 | 2 | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 12.1 | tesseract | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 34.1 | tesseract | – | – | – |
| Hybrid | 5 | 3 / 4 | 75% | 16.4 | tesseract | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 30.1 | tesseract | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 4 / 4 | 100% | 74.2 | tesseract | 23 | 9 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 40.7 | tesseract | 13 | 4 | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 10.6 | tesseract | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 45.5 | tesseract | – | – | – |
| Hybrid | 5 | 1 / 4 | 25% | 18.5 | tesseract | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 28.7 | tesseract | 8 | 1 | 0 |
| Agent Orchestrator | 5 | 4 / 4 | 100% | 72.6 | tesseract | 23 | 4 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 43.9 | tesseract | 13 | 4 | – |


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


#### Segment 2 — `task` — _Aufgabe 1: Berechne die Eigenkapitalquote._

**Original:**
```
Aufgabe 1: Berechne die Eigenkapitalquote.
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Anteil des Eigenkapitals am Gesamtvermögen eines Unternehmens.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Anteil des Eigenkapitals am Gesamtvermögen eines Unternehmens.
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Wie hoch ist der Anteil des Eigenkapitals am gesamten Vermöten in Prozent?
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Gesamtvermögen der Firma Stahlhersteller AG.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Gesamtvermögen der "Stark & Stark GmbH".
```
</details>


#### Segment 3 — `task` — _Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 € Wie hoch ist der Gew…_

**Original:**
```
Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 € Wie hoch ist der Gewinn?
```

**🔗 LangChain** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma Bergstrom GmbH. Der Ertrag belief sich auf 600.000 SEK, die betrieblichen Ausgaben 525.000 NOK. Wie hoch ist der Gewinn?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma Stahlbau Schweiz. Der Ertrag belief sich auf 600'000 SEK, die Betriebskosten auf 520'000 NOK. Wie hoch ist der Gewinn?
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Anteil des Eigenkapitals am gesamten Vermötterniveau.

\documentclass{article}
\usepackage{amsmath}

Berechne die Eigenkapitalquote.

**Theoretische Grundlagen:**

Die Eigenkapitalquote ist ein wichtiger Kennwert, um die finanzielle Risikofähigkeit eines Unternehmens zu beurteilen. Sie zeigt, welcher Anteil des Eigenkapitals am gesamten Kapitalbestand vorhanden ist. Die Berechnung erfolgt wie folgt:

\[
E = \frac{E_k}{A_t}
\]

wobei:

\begin{itemize}
    \item  $E$ die Eigenkapitalquote in Prozent darstellt.
    \item $E_k$ das Eigenkapital des Unternehmens bezeichnet.
    \item $A_t$ die gesamte Kapitaldebent – wie in der Skizze rechts dargestellt – angibt.
\end{itemize}

Die Eigenkapitalquote gibt Auskunft darüber, wie stark das Unternehmen auf eigenes Kapital angewiesen ist. Eine hohe Eigenkapitalquote deutet auf eine geringe Abhängigkeit von Fremdkapital hin, was als positiv zu werten ist. Eine sehr niedrige Eigenkapitalquote hingegen kann ein Warnsignal sein, da das Unternehmen stark auf Fremdkapital angewiesen ist.

**Gegeben:**

\begin{align*}
E_k &= 125000 € \\
A_t &= 625000 €
\end{align*}

Berechne die Eigenkapitalquote und gib das Ergebnis in Prozent an.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle bitte den Jahresertrag der Firma Björn & Sohn AG für das vergangene Geschäftsjahr. Die Erträge beliefen sich auf 600’000 SEK, während die Betriebskosten bei 540’000 NOK lagen. Wie hoch war der daraus resultierende Gewinn?
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der "NovaTech GmbH". Der Erlös belief sich auf 600.000 SEK, die Betriebskosten auf 520.000 NOK.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma Stahlbaum GmbH. Die Erlöse beliefen sich auf 600.000 SEK, die Betriebskosten auf 540.000 NOK. Wie hoch war der Gewinn?
```
</details>


#### Segment 4 — `task` — _Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 € Wie hoch ist der Gew…_

**Original:**
```
Aufgabe 2: Der Umsatz betrug 500.000 € die Kosten 450.000 €
Wie hoch ist der Gewinn?
```

**🔗 LangChain:** _(kein Segment #4)_

**🕸️  LangGraph:** _(kein Segment #4)_

**🔀 Hybrid** — Klassifiziert als `economics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent:** _(kein Segment #4)_

**⚡ Agent Orchestrator:** _(kein Segment #4)_

**📋 Agent Multi-Step:** _(kein Segment #4)_

---

## 4. Agent-spezifische Analyse

_Diese Metriken sind nur für Frameworks mit AgentExecutor verfügbar._

### Tool-Call-Verteilung

| Framework | Domain | Tool-Calls | Retries | Halluziniert | Valid-Rate |
|-----------|--------|------------|---------|--------------|------------|
| Hybrid+Agent | math | 8 | 0 | 0 | 100% |
| Agent Orchestrator | math | 32 | 4 | None | 100% |
| Agent Multi-Step | math | 14 | 4 | None | 75% |
| Hybrid+Agent | math | 10 | 0 | 0 | 100% |
| Agent Orchestrator | math | 20 | 6 | None | 75% |
| Agent Multi-Step | math | 16 | 4 | None | 100% |
| Hybrid+Agent | math | 8 | 0 | 0 | 75% |
| Agent Orchestrator | math | 12 | 4 | None | 75% |
| Agent Multi-Step | math | 15 | 4 | None | 100% |
| Hybrid+Agent | languages | 10 | 2 | 0 | 100% |
| Agent Orchestrator | languages | 6 | 2 | None | 67% |
| Agent Multi-Step | languages | 12 | 3 | None | 33% |
| Hybrid+Agent | languages | 17 | 8 | 0 | 80% |
| Agent Orchestrator | languages | 36 | 16 | None | 100% |
| Agent Multi-Step | languages | 15 | 5 | None | 80% |
| Agent Orchestrator | languages | 8 | 3 | None | 25% |
| Agent Multi-Step | languages | 12 | 4 | None | 75% |
| Hybrid+Agent | economics | 6 | 1 | 0 | 100% |
| Agent Orchestrator | economics | 8 | 2 | None | 100% |
| Agent Multi-Step | economics | 6 | 2 | None | 100% |
| Hybrid+Agent | economics | 8 | 0 | 0 | 100% |
| Agent Orchestrator | economics | 23 | 9 | None | 100% |
| Agent Multi-Step | economics | 13 | 4 | None | 100% |
| Hybrid+Agent | economics | 8 | 1 | 0 | 100% |
| Agent Orchestrator | economics | 23 | 4 | None | 100% |
| Agent Multi-Step | economics | 13 | 4 | None | 100% |

**Halluzinations-Rate gesamt:** 0 / 359 Tool-Events = 0.0%

### Vergleich Retry-Effizienz: Agent vs. LangGraph

| Domain | LangGraph (Retries) | Hybrid+Agent (Retries) | Agent Orch. (Retries) |
|--------|---------------------|------------------------|----------------------|
| math | – | 0 | 4 |
| languages | – | 2 | 2 |
| economics | – | 1 | 2 |


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. **Agent Orchestrator** benötigte in Domain *math* Ø 964% mehr Zeit als **LangChain Pipeline** (108.2s vs. 10.2s).

2. **Hybrid+Agent vs. Hybrid** (math): Zeit +12.6s, Validation-Rate 0%. Identisches Pre/Postprocessing – Unterschied ausschliesslich Phase 2 (AgentExecutor vs. LangGraph StateGraph).

3. **Agent Multi-Step** erzielte mit Ø 85% Validation-Rate keine signifikant höhere Rate als **LangChain Pipeline** (83%, Differenz: +2%). Dies unterstützt die These, dass ein Agent mit einem einzigen Tool zur deterministischen Pipeline degeneriert.

4. **LangGraph** (Conditional Edges): Ø 0.0 Retries/Run — **Agent Orchestrator** (LLM-Scratchpad): Ø 5.6 Retries/Run. LangGraph-Retries sind explizit im Graphen definiert; Agent-Retries entstehen implizit durch LLM-Entscheidung.

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **LangGraph** / math / Seg 4 / V1: Ratio 4.4×
- **Hybrid** / math / Seg 3 / V1: Ratio 7.1×
- **Agent Orchestrator** / math / Seg 2 / V1: Ratio 12.4×
- **Agent Multi-Step** / math / Seg 2 / V1: Ratio 16.1×
- **Hybrid** / languages / Seg 4 / V1: Ratio 4.2×
- **LangGraph** / languages / Seg 5 / V1: Ratio 3.7×
- **Hybrid** / languages / Seg 5 / V1: Ratio 3.5×
- **Agent Orchestrator** / languages / Seg 5 / V1: Ratio 4.0×
- **Hybrid** / economics / Seg 3 / V1: Ratio 28.5×
- **LangGraph** / economics / Seg 2 / V1: Ratio 16.9×
- **Agent Multi-Step** / economics / Seg 2 / V1: Ratio 34.1×
