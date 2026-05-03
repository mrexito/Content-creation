# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-03-22 20:53:16  |  **Varianten/Segment:** 1  |  **Frameworks:** 6  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 18.3 | 65% | – | – |
| LangGraph | Node → StateGraph → Node | 50.2 | 64% | – | – |
| Hybrid | LC → LangGraph → LC | 20.5 | 76% | – | – |
| Hybrid+Agent | LC → AgentExecutor → LC | 65.3 | 90% | 6.0 | 20.6 |
| Agent Orchestrator | Chain → AgentExecutor → Chain | 85.0 | 81% | 10.1 | 30.4 |
| Agent Multi-Step | Chain → 3× Agent → Chain | 55.7 | 74% | 6.0 | 21.1 |


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
| LangChain | 5 | 4 / 4 | 100% | 10.7 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 17.3 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 14.0 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 26.7 | mistral | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 2 / 4 | 50% | 29.8 | mistral | 6 | 2 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 35.8 | mistral | 13 | 4 | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 8 | 4 / 7 | 57% | 20.9 | mistral | – | – | – |
| LangGraph | 8 | 4 / 7 | 57% | 52.8 | mistral | – | – | – |
| Hybrid | 8 | 6 / 7 | 86% | 25.8 | mistral | – | – | – |
| Hybrid+Agent | 8 | 6 / 7 | 86% | 66.4 | mistral | 20 | 3 | 0 |
| Agent Orchestrator | 8 | 4 / 7 | 57% | 77.8 | mistral | 32 | 9 | – |
| Agent Multi-Step | 8 | 4 / 7 | 57% | 71.2 | mistral | 27 | 7 | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 10.6 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 20.1 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 14.6 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 30.8 | mistral | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 4 / 4 | 100% | 65.5 | mistral | 23 | 9 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 40.5 | mistral | 16 | 4 | – |


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
Löse die Gleichung $5a + 2 = 17$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Hebe die Gleichung $3y - 7 = 8$ an.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die Gleichung $4a + 9 = 25$ soll nach $a$ aufgelöst werden.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die Gleichung $3y - 7 = 20$ lässt sich wie folgt lösen:
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $4a + 10 = 26$
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $4a + 10 = 26$
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
Aufgabe 2: Vereinfache: $5(a + 4) - 3(b - 2)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: $5\left(a + 3\right) - 4\left(b - 2\right)$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: 5a + 20 - 3b + 6
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache den Ausdruck: $5a + 20 - 3b + 6$
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `general / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


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
Berechne die Perimeter eines Dreiecks, dessen Seitenlängen gegeben sind: $x = 5$ cm, $y = 7$ cm und $z = 9$ cm.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Begrenzung eines Dreiecks, wenn die Längen der Seiten $a = 8$ dm, $b = 12$ dm und $c = 15$ dm sind.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Umkreislinie eines Dreiecks, bei dem die Seitenlängen gegeben sind: 5 cm, 7 cm und 9 cm.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ein Dreieck hat die Seitenlängen $a = 8$ cm, $b = 10$ cm und $c = 12$ cm. Berechne den Umfang dieses Dreiecks.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `general / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Umfang eines Dreiecks, dessen Seitenlängen $P=5$, $Q=7$ und $R=9$ sind.
\
Theoretischer Hintergrund: Der Umfang eines Dreiecks ist die Summe aller seiner Seitenlängen.
\
Formel:  Der Umfang $U$ eines Dreiecks mit den Seitenlängen $a$, $b$ und $c$ ist definiert als $U = a + b + c$.
\
Lösung:
\
Gegeben sind die Seitenlängen eines Dreiecks: $a = 5$, $b = 7$ und $c = 9$.
\
Um den Umfang zu berechnen, addieren wir die Seitenlängen:
$$ U = a + b + c = 5 + 7 + 9 $$
$$ U = 21 $$
Die Seitenlängen sind also $a=5$ cm, $b=7$ cm und $c=9$ cm. Der Umfang des Dreiecks beträgt 21 cm.
\
Wie in der Skizze rechts dargestellt.
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
Aufgabe 4: Eine Investition von 1500 € wird mit einem Zinssatz von 2,5 % pro Jahr verzinst. Berechne das Kapital nach 8 Jahren unter Berücksichtigung des Zinseszinses.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 € wird auf eine jährliche Rendite von 2,5 % verzinst.  Berechnen Sie das Gesamtergebnis nach 6 Jahren.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Betrag von 1250 Euro wird auf ein Sparkonto angelegt, bei dem eine jährliche Verzinsung von 3,5 Prozent besteht. Berechnen Sie das Kapital nach sechs Jahren unter Berücksichtigung des Zinseszinses.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 DM wird mit einem Zinssatz von 2,5 Prozent pro Jahr verzinst. Berechnen Sie das Kapital nach acht Jahren unter Berücksichtigung eines einfachen Verzinsungssystems.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 DM wird mit einem Zinssatz von 2,5% p. a. verzinst. Bestimmen Sie das zu erwartende Endguthaben nach 7 Jahren.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 800 € wird auf ein Konto mit einer jährlichen Verzinsung von 2,5 % eingezahlt. Berechne das Kapital am Ende von 6 Jahren unter Berücksichtigung der jährlichen Zinsaufrechnung.
```
</details>


---

## 3.2 Domäne: Sprachen (`languages`)

**PDFs:** `languages/grammar_exercise.pdf` | `languages/sentence_construction.pdf` | `languages/verb_conjugation.pdf` | **Validator:** BERTScore


### Metriken

**PDF:** `grammar_exercise.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 1 / 3 | 33% | 12.6 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 22.2 | tesseract | – | – | – |
| Hybrid | 4 | 3 / 3 | 100% | 17.3 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 3 / 3 | 100% | 49.5 | tesseract | 16 | 9 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 58.0 | tesseract | 22 | 4 | – |
| Agent Multi-Step | 4 | 1 / 3 | 33% | 28.3 | tesseract | 12 | 3 | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 2 / 5 | 40% | 16.4 | tesseract | – | – | – |
| LangGraph | 6 | 2 / 5 | 40% | 35.7 | tesseract | – | – | – |
| Hybrid | 6 | 4 / 4 | 100% | 27.8 | tesseract | – | – | – |
| Hybrid+Agent | 6 | 3 / 5 | 60% | 52.0 | tesseract | 17 | 4 | 0 |
| Agent Orchestrator | 6 | 4 / 5 | 80% | 43.2 | tesseract | 17 | 6 | – |
| Agent Multi-Step | 6 | 3 / 5 | 60% | 45.4 | tesseract | 17 | 5 | – |

**PDF:** `verb_conjugation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 21 | 3 / 20 | 15% | 55.6 | tesseract | – | – | – |
| LangGraph | 22 | 3 / 21 | 14% | 195.5 | tesseract | – | – | – |
| Hybrid | 8 | 6 / 7 | 86% | 37.0 | tesseract | – | – | – |
| Hybrid+Agent | 21 | 12 / 20 | 60% | 275.3 | tesseract | 92 | 34 | 0 |
| Agent Orchestrator | 20 | 12 / 19 | 63% | 324.7 | tesseract | 108 | 35 | – |
| Agent Multi-Step | 22 | 8 / 21 | 38% | 174.8 | tesseract | 69 | 21 | – |


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

□ Baum wächst an □ Berg.
□ Schüler sitzen in □ Klasse.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

□ Schloss thront über □ Berg.
□ Jugendliche vergnügen sich auf □ Rasenfläche.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die korrekten Artikel ein:

Die Villa thront auf dem Berg.
Die Kinder vergnügen sich im Garten.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die korrekten Artikel ein: Formuliere die folgenden Sätze um, wobei du die passende Wortwahl sorgfältig abwägest und die Präzision erhöhst. Achte darauf, dass die Bedeutung erhalten bleibt – lediglich die Art und Weise der Formulierung wird verändert.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Villa thront auf __ Berg.
__ Jugendliche vergnügen sich in __ Park.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `general / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die Residenz thront auf der Zuspitzung eines Berges.
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
Aufgabe 2: Bilde die Parfait:

Der Postbote bringt die Briefe. —

Sie malt ein Bild. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. – Er hat eine Lektion besucht.

Er liest ein Buch. – Sie widmete sich der Lektüre.

Er ist nach Hause gegangen. – Sie kehrte zu ihren Eltern zurück.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Er taucht in die Seiten eines Buches ein. / Er verliert sich im Labyrinth der Wörter innerhalb eines Buches. / Die Buchstaben fließen ihm wie ein Strom zu, während er ein Buch liest. / Er vertieft sich in die Welt, die in einem Buch beschrieben ist.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:\nFormuliere die folgenden Sätze ins Deutsche Perfekt, wobei du dabei auf eine bedeutend veränderte Ausdrucksweise achtest.\n\nBeispiel:\nSie schreibt ein Brief. — Sie hat einen Brief geschrieben.\n\nErich kocht das Abendessen. — Er hat das Abendessen gekocht.\ndie Kinder spielen im Garten. — Sie haben im Garten gespielt.\ndas Mädchen singt ein Lied. — Sie hat ein Lied gesungen.
```
</details>


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

Welche der genannten Begriffe können als gleichbedeutend betrachtet werden, unter Berücksichtigung ihrer jeweiligen Konnotationen?

Betrachten wir die folgenden Wortgruppen: schnell – rasch – langsam – zügig.  Welche dieser Begriffe manifestieren eine ähnliche Bedeutung im Sinne von "mit hoher Geschwindigkeit voranzugehen" oder “effizient zu wirken”?  Erläutern Sie Ihre Antwort mit Bezug auf die Nuancen der Wortbedeutung.
```

> **Issues:** Länge weicht stark ab: 466 vs 74 Zeichen (Ratio: 6.30, erlaubt: 0.6-1.5)
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

Welche der folgenden Begriffe haben eine ähnliche oder nahezu identische Bedeutung? Vergleichen Sie die Bedeutungen sorgfältig und wählen Sie aus, welche Wörter innerhalb des gegebenen Wortfelds als gleichwertige Alternativen betrachtet werden können.

schnell – rasch – langsam – zügig
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Schnell, flink, geduldig und stetig.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `general / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:
schnell - rasch - langsam - zügig

Die flinke Maus bewegte sich _________ über den Teppich.  Ein schneller Zug fuhr _________ durch die Landschaft. Nach einer langen und _________ Reise erreichte das Schiff endlich seinen Zielort.  Die Arbeit verlief _________, ohne Unterbrechungen und mit großer Effizienz.
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
| LangChain | 4 | 3 / 3 | 100% | 9.6 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 26.2 | tesseract | – | – | – |
| Hybrid | 4 | 1 / 3 | 33% | 16.2 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 3 / 3 | 100% | 26.6 | tesseract | 6 | 0 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 32.6 | tesseract | 11 | 4 | – |
| Agent Multi-Step | 4 | 3 / 3 | 100% | 33.6 | tesseract | 10 | 3 | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 3 / 3 | 100% | 7.9 | tesseract | – | – | – |
| LangGraph | 4 | 1 / 3 | 33% | 22.9 | tesseract | – | – | – |
| Hybrid | 4 | 1 / 3 | 33% | 12.9 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 3 / 3 | 100% | 31.7 | tesseract | 9 | 3 | 0 |
| Agent Orchestrator | 5 | 4 / 4 | 100% | 34.1 | tesseract | 12 | 4 | – |
| Agent Multi-Step | 4 | 3 / 3 | 100% | 28.5 | tesseract | 13 | 3 | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 9 | 3 / 8 | 38% | 20.9 | tesseract | – | – | – |
| LangGraph | 9 | 5 / 8 | 62% | 58.5 | tesseract | – | – | – |
| Hybrid | 5 | 2 / 4 | 50% | 18.6 | tesseract | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 29.0 | tesseract | 9 | 1 | 0 |
| Agent Orchestrator | 9 | 6 / 8 | 75% | 99.1 | tesseract | 43 | 18 | – |
| Agent Multi-Step | 5 | 3 / 4 | 75% | 43.5 | tesseract | 13 | 4 | – |


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
BESTANDTEILE:

Verschuldete Vermögenswerte: 90.000 SEK
Liquide Mittel: 55.000 NOK

Gesamt: 145.000 SEK
SCHULDEN:

Eigenkapital: 85.000 DKK
Fremdkapital: 60.000 EUR

Gesamt: 145.000 DKK
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
Umlaufvermögen: 55.000 NOK

Gesamt: 145.000 SEK
PASSIVA:

Eigenkapital: 85.000 NOK
Fremdkapital: 60.000 SEK
Gesamt: 145.000 SEK
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaVision Solutions AG

Bilanz zum 31. Dezember 2025:

**Aktivitäten:**

*   Wesentlich Vermögen: 210.000 SEK
*   Umlaufvermögen: 95.000 NOK

**Gesamt:** 305.000 SEK

**Verbindlichkeiten:**

*   Eigenkapitalanteil: 185.000 NOK
*   Fremdkapital: 120.000 SEK

**Gesamt:** 305.000 SEK
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / data` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Gesamtvermögen der Firma Bern AG.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / data` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Betrieb: Innova Solutions AG
Jahresabschluss zum 31. Dezember 2025:
VERMÖGEN:
    Sachanlagen: 95.000 SEK	Liquide Mittel: 60.000 NOK
    Gesamt: 155.000 SEK
SCHULDEN:
    Stammkapital: 80.000 SEK	Zinsen und Kredite: 75.000 SEK
    Gesamt: 155.000 SEK

Berechne den Anteil des Eigenkapitals am Gesamtvermögen der Firma.
```
</details>


#### Segment 3 — `task` — _Aufgabe 1: Berechne die Eigenkapitalquote._

**Original:**
```
Aufgabe 1: Berechne die Eigenkapitalquote.
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Ermittle den Anteil des Eigenkapitals am Gesamtkapital.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Ermittle den Anteil des Eigenkapitals am Gesamtvermögen.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Berechne den Anteil des Eigenkapitals am gesamten Vermöten.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Berechne den Anteil des Eigenkapitals am gesamten Vermöten.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Gesamtvermögen der Beispielholding GmbH.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am gesamten Vermögen der Firma Stardust Solutions.
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
Ermittle den Jahresumsatzüberschuss der Firma Bergenhold GmbH. Der Ertrag belief sich auf 600.000 SEK, die betrieblichen Ausgaben 520.000 NOK. Wie hoch ist der Gewinn?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Erlöse der Firma Stahlwerk Nord GmbH summierten sich auf 600.000 SEK, die Betriebskosten beliefen sich auf 530.000 NOK. Wie hoch war der Jahresgewinn?
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Stahlwerk Bayern GmbH. Der jeweilige Erlös betrug 620.000 SEK, die betrieblichen Ausgaben 580.000 NOK. Wie hoch war das Endergebnis?
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma Baumwuchs GmbH. Die Erlöse beliefen sich auf 600.000 SEK, die Betriebskosten auf 520.000 NOK
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Bären GmbH bei einem Erlös von 600.000 SEK und Betriebskosten von 520.000 NOK.
```
</details>


---

## 4. Agent-spezifische Analyse

_Diese Metriken sind nur für Frameworks mit AgentExecutor verfügbar._

### Tool-Call-Verteilung

| Framework | Domain | Tool-Calls | Retries | Halluziniert | Valid-Rate |
|-----------|--------|------------|---------|--------------|------------|
| Hybrid+Agent | math | 8 | 0 | 0 | 100% |
| Agent Orchestrator | math | 6 | 2 | None | 50% |
| Agent Multi-Step | math | 13 | 4 | None | 100% |
| Hybrid+Agent | math | 20 | 3 | 0 | 86% |
| Agent Orchestrator | math | 32 | 9 | None | 57% |
| Agent Multi-Step | math | 27 | 7 | None | 57% |
| Hybrid+Agent | math | 8 | 0 | 0 | 100% |
| Agent Orchestrator | math | 23 | 9 | None | 100% |
| Agent Multi-Step | math | 16 | 4 | None | 100% |
| Hybrid+Agent | languages | 16 | 9 | 0 | 100% |
| Agent Orchestrator | languages | 22 | 4 | None | 100% |
| Agent Multi-Step | languages | 12 | 3 | None | 33% |
| Hybrid+Agent | languages | 17 | 4 | 0 | 60% |
| Agent Orchestrator | languages | 17 | 6 | None | 80% |
| Agent Multi-Step | languages | 17 | 5 | None | 60% |
| Hybrid+Agent | languages | 92 | 34 | 0 | 60% |
| Agent Orchestrator | languages | 108 | 35 | None | 63% |
| Agent Multi-Step | languages | 69 | 21 | None | 38% |
| Hybrid+Agent | economics | 6 | 0 | 0 | 100% |
| Agent Orchestrator | economics | 11 | 4 | None | 100% |
| Agent Multi-Step | economics | 10 | 3 | None | 100% |
| Hybrid+Agent | economics | 9 | 3 | 0 | 100% |
| Agent Orchestrator | economics | 12 | 4 | None | 100% |
| Agent Multi-Step | economics | 13 | 3 | None | 100% |
| Hybrid+Agent | economics | 9 | 1 | 0 | 100% |
| Agent Orchestrator | economics | 43 | 18 | None | 75% |
| Agent Multi-Step | economics | 13 | 4 | None | 75% |

**Halluzinations-Rate gesamt:** 0 / 649 Tool-Events = 0.0%

### Vergleich Retry-Effizienz: Agent vs. LangGraph

| Domain | LangGraph (Retries) | Hybrid+Agent (Retries) | Agent Orch. (Retries) |
|--------|---------------------|------------------------|----------------------|
| math | – | 0 | 2 |
| languages | – | 9 | 4 |
| economics | – | 0 | 4 |


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. **Agent Orchestrator** benötigte in Domain *math* Ø 179% mehr Zeit als **LangChain Pipeline** (29.8s vs. 10.7s).

2. **Hybrid+Agent vs. Hybrid** (math): Zeit +12.8s, Validation-Rate 0%. Identisches Pre/Postprocessing – Unterschied ausschliesslich Phase 2 (AgentExecutor vs. LangGraph StateGraph).

3. **LangGraph** (Conditional Edges): Ø 0.0 Retries/Run — **Agent Orchestrator** (LLM-Scratchpad): Ø 10.1 Retries/Run. LangGraph-Retries sind explizit im Graphen definiert; Agent-Retries entstehen implizit durch LLM-Entscheidung.

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Prompt-Leaks:**
- **LangGraph** / languages / V1: Prompt-Text im Output erkannt

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **Agent Multi-Step** / math / Seg 4 / V1: Ratio 7.0×
- **LangGraph** / math / Seg 3 / V1: Ratio 7.8×
- **LangGraph** / math / Seg 5 / V1: Ratio 5.7×
- **LangGraph** / math / Seg 7 / V1: Ratio 24.8×
- **Hybrid** / math / Seg 3 / V1: Ratio 5.6×
- **Hybrid** / math / Seg 7 / V1: Ratio 18.0×
- **Hybrid+Agent** / math / Seg 3 / V1: Ratio 7.6×
- **Hybrid+Agent** / math / Seg 7 / V1: Ratio 10.2×
- **Hybrid+Agent** / math / Seg 8 / V1: Ratio 14.9×
- **Agent Orchestrator** / math / Seg 3 / V1: Ratio 4.6×
- **Agent Multi-Step** / math / Seg 3 / V1: Ratio 12.2×
- **Agent Multi-Step** / math / Seg 8 / V1: Ratio 17.9×
- **LangGraph** / languages / Seg 4 / V1: Ratio 6.3×
- **Hybrid** / languages / Seg 4 / V1: Ratio 4.4×
- **Hybrid+Agent** / languages / Seg 3 / V1: Ratio 3.8×
- **Agent Orchestrator** / languages / Seg 3 / V1: Ratio 5.3×
- **Agent Orchestrator** / languages / Seg 4 / V1: Ratio 4.8×
- **LangGraph** / languages / Seg 5 / V1: Ratio 4.6×
- **Hybrid** / languages / Seg 5 / V1: Ratio 4.8×
- **Hybrid+Agent** / languages / Seg 5 / V1: Ratio 6.9×
  … und 38 weitere
