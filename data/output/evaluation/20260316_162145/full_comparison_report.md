# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-03-16 16:21:45  |  **Varianten/Segment:** 1  |  **Frameworks:** 6  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 12.0 | 66% | – | – |
| LangGraph | Node → StateGraph → Node | 29.4 | 75% | – | – |
| Hybrid | LC → LangGraph → LC | 19.9 | 80% | – | – |
| Hybrid+Agent | LC → AgentExecutor → LC | 47.1 | 79% | 4.3 | 14.9 |
| Agent Orchestrator | Chain → AgentExecutor → Chain | 50.2 | 88% | 8.6 | 20.0 |
| Agent Multi-Step | Chain → 3× Agent → Chain | 40.6 | 66% | 4.0 | 14.9 |


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
| LangChain | 5 | 4 / 4 | 100% | 10.3 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 18.6 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 13.2 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 35.6 | mistral | 12 | 2 | 0 |
| Agent Orchestrator | 5 | 3 / 4 | 75% | 41.9 | mistral | 18 | 7 | – |
| Agent Multi-Step | 5 | 3 / 4 | 75% | 55.8 | mistral | 16 | 4 | – |

**PDF:** `equations_advanced.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 8 | 4 / 7 | 57% | 15.1 | mistral | – | – | – |
| LangGraph | 8 | 4 / 7 | 57% | 58.8 | mistral | – | – | – |
| Hybrid | 8 | 7 / 7 | 100% | 24.1 | mistral | – | – | – |
| Hybrid+Agent | 8 | 3 / 7 | 43% | 100.4 | mistral | 31 | 10 | 0 |
| Agent Orchestrator | 8 | 5 / 7 | 71% | 71.9 | mistral | 28 | 11 | – |
| Agent Multi-Step | 8 | 3 / 7 | 43% | 65.3 | mistral | 25 | 7 | – |

**PDF:** `word_problems.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 11.0 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 20.8 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 14.6 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 30.2 | mistral | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 4 / 4 | 100% | 61.2 | mistral | 23 | 15 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 44.1 | mistral | 16 | 4 | – |


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
Löse die Gleichung $3a + 7 = 20$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimme den Wert von $x$ in der Gleichung $3y - 7 = 10$.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $7y - 12 = 4$.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die Gleichung $3y - 7 = 16$ lässt sich wie folgt lösen:
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $5a + 2 = 17$
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $4y - 12 = -8$
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
Vereinfache den Ausdruck: $5(a + 3) - 4(b - 2)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Vereinfache: $5(a + 4) - 3(b - 2)$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache den Ausdruck: $5(a + 7) - 3(b - 4)$.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache den Ausdruck: $5a + 15 - 4b + 8$
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 4 — `task` — _Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten: a = 5 cm, b = 7 cm…_

**Original:**
```
Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten: a = 5 cm, b = 7 cm, c = 9 cm
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge des Umfangs eines Dreiecks, dessen Seitenlängen  $p = 5$, $q = 7$ und $r = 9$ Meter sind.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimmen Sie die Umfangs eines Dreiecks, dessen Seitenlängen gegeben sind: $r_1 = 5 \text{ m}$, $r_2 = 7 \text{ m}$ und $r_3 = 9 \text{ m}$.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Umfang eines Dreiecks, dessen Seitenlängen 5 cm, 7 cm und 9 cm betragen.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge des Kreisumfangs eines Kreises mit einem Radius von 8 Metern. Runde das Ergebnis auf zwei Nachkommastellen.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Bestimme die Länge des Umfangs eines Dreiecks, dessen Seitenlängen $P = 12$ m, $Q = 15$ m und $R = 18$ m sind.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Umfang eines Dreiecks, bei dem die Längen der Seiten gegeben sind als: $l_1 = 5$ cm, $l_2 = 7$ cm und $l_3 = 9$ cm.
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
Aufgabe 4: Eine Investition von 1500 Dollar wird mit einem Zinssatz von 2,5 % pro Jahr verzinst. Berechne das angesammelte Kapital nach einer Laufzeit von 6 Jahren.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition in Höhe von 1250 € wird auf einen Zinssatz von 4,5% verzinst. Berechne das Kapital nach 3 Jahren unter Berücksichtigung dieser Verzinsung.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Einlage von 2500 Euro wird mit einer jährlichen Verzinsung von 4,5 Prozent angelegt. Berechnen Sie das Kapital nach acht Jahren.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Eine Investition von 1500 DM wird mit einem Zinssatz von 4,25 % jährlich effektiv verzinst. Berechnen Sie das Kapital nach sechs Jahren.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1250 € wird fällig, wenn es 6,75 % Zinsen pro Jahr bringt. Berechne das Gesamtergebnis nach 8 Jahren.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1250 Euro wird mit einem Zinssatz von 6,5% verzinst. Berechne das angesammelte Kapital nach einem Zeitraum von 8 Jahren.
```
</details>


---

## 3.2 Domäne: Sprachen (`languages`)

**PDFs:** `languages/grammar_exercise.pdf` | `languages/sentence_construction.pdf` | `languages/text_analysis.pdf` | **Validator:** BERTScore


### Metriken

**PDF:** `grammar_exercise.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 1 / 3 | 33% | 11.7 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 24.4 | tesseract | – | – | – |
| Hybrid | 4 | 3 / 3 | 100% | 15.4 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 2 / 3 | 67% | 28.1 | tesseract | 8 | 2 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 26.5 | tesseract | 11 | 4 | – |
| Agent Multi-Step | 4 | 1 / 3 | 33% | 28.3 | tesseract | 12 | 3 | – |

**PDF:** `sentence_construction.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 6 | 2 / 5 | 40% | 15.6 | tesseract | – | – | – |
| LangGraph | 6 | 2 / 5 | 40% | 33.5 | tesseract | – | – | – |
| Hybrid | 6 | 4 / 4 | 100% | 26.6 | tesseract | – | – | – |
| Hybrid+Agent | 6 | 3 / 5 | 60% | 69.6 | tesseract | 20 | 6 | 0 |
| Agent Orchestrator | 6 | 3 / 5 | 60% | 63.0 | tesseract | 26 | 11 | – |
| Agent Multi-Step | 6 | 2 / 5 | 40% | 45.7 | tesseract | 19 | 5 | – |

**PDF:** `text_analysis.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 1 / 3 | 33% | 10.6 | tesseract | – | – | – |
| LangGraph | 4 | 1 / 3 | 33% | 26.1 | tesseract | – | – | – |
| Hybrid | 4 | 3 / 3 | 100% | 15.1 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 2 / 3 | 67% | 33.4 | tesseract | 12 | 7 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 22.4 | tesseract | 9 | 3 | – |
| Agent Multi-Step | 4 | 0 / 3 | 0% | 27.0 | tesseract | 11 | 3 | – |


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
□ Die Kleinkinder vergnügen sich in □ Feld.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Setze die richtigen Artikel ein:

□ Die Villa thront über □ Berg.
□ Jugendliche vergnügen sich im □ Park.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Villa thront über dem Berg.
Jugendliche vergnügen sich im Park.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Setze die passenden Artikel ein: Das Schloss befindet sich auf dem Berg. Jugendliche vergnügen sich im Park.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

□ Die Villa thront auf □ Berg.
□ Jugendliche vergnügen sich in □ Park.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `general / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


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

Die Schüler gehen zur Schule. —

Sie liest ein Buch. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. – Er ist bereits zur Schule gegangen.

Er liest ein Buch. – Sie ist bereits intensiv in das Lesen eines Buches vertieft.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `general / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Er liest ________ Buch. / Er geht ________ Kino.
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
Aufgabe 1: Setze die richtigen Artikel ein:

Welche Wörter sind Synonyme?

schnell - rasch - langsam – zügig
```

> **Issues:** Länge weicht stark ab: 108 vs 63 Zeichen (Ratio: 1.71, erlaubt: 0.6-1.5)
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

Bitte wählen Sie aus den folgenden Begriffen diejenigen aus, die inhaltlich nahezu identische Bedeutungen aufweisen.

schnell – eilig – träge – expedit
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

schnell – rasch – langsam – zügig

Die Bewegung verlief **schnell**, während der Gegner auf **eine** Reaktion hoffte. Es war **ein** Prozess, der jedoch **erfolgreich** abgeschlossen wurde. Die Nachricht erreichte uns **umgehend**, und wir reagierten **prompt**. Die Arbeit war **anstrengend**, um sie rechtzeitig zu erledigen. Manchmal ist es **schwierig**, Dinge zu beschleunigen, während andere Situationen **eine** geduldige Vorgehensweise erfordern. Die Maschine arbeitete **effizient**, um die Aufgabe zu bewältigen.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter beschreiben ähnliche Bedeutungen? flink – eilig – geduldig – ungeschwind
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

Formuliere die folgenden Wortpaare so um, dass sie inhaltlich gleichen Sinn ergeben, jedoch eine andere Ausdrucksweise verwenden. Achte dabei auf unterschiedliche Wortwahl und Satzstruktur.

□ Vogel fliegt □ Baum. / □ Blume blüht □ Feld.
```
</details>


---

## 3.3 Domäne: Wirtschaft (`economics`)

**PDFs:** `economics/balance_sheet.pdf` | `economics/income_statement.pdf` | `economics/investment_calculation.pdf` | **Validator:** ConsistencyCheck


### Metriken

**PDF:** `balance_sheet.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 3 / 3 | 100% | 9.2 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 21.9 | tesseract | – | – | – |
| Hybrid | 4 | 1 / 3 | 33% | 23.1 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 3 / 3 | 100% | 25.0 | tesseract | 6 | 0 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 39.3 | tesseract | 12 | 4 | – |
| Agent Multi-Step | 4 | 3 / 3 | 100% | 32.9 | tesseract | 10 | 3 | – |

**PDF:** `income_statement.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 2 / 3 | 67% | 7.9 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 25.6 | tesseract | – | – | – |
| Hybrid | 5 | 1 / 4 | 25% | 21.7 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 3 / 3 | 100% | 25.6 | tesseract | 8 | 1 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 50.5 | tesseract | 20 | 9 | – |
| Agent Multi-Step | 4 | 3 / 3 | 100% | 26.9 | tesseract | 12 | 3 | – |

**PDF:** `investment_calculation.pdf`

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 9 | 5 / 8 | 62% | 16.6 | tesseract | – | – | – |
| LangGraph | 5 | 3 / 4 | 75% | 35.1 | tesseract | – | – | – |
| Hybrid | 9 | 5 / 8 | 62% | 25.1 | tesseract | – | – | – |
| Hybrid+Agent | 9 | 6 / 8 | 75% | 75.6 | tesseract | 29 | 11 | 0 |
| Agent Orchestrator | 9 | 7 / 8 | 88% | 75.5 | tesseract | 33 | 13 | – |
| Agent Multi-Step | 5 | 4 / 4 | 100% | 39.1 | tesseract | 13 | 4 | – |


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
Bilanz zum 31.12.2025:
VERMÖGENSPOSTEN:

Grundst{\"a\"tte und Immobilien: 85.000 SEK
Umlaufvermögen: 60.000 NOK

Gesamt: 145.000 SEK
SCHULDEN UND FIINANZIERUNGEN:

Eigenkapitalanteil: 90.000 NOK
Fremdkapital: 55.000 SEK
Gesamt: 145.000 SEK
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaVision Solutions AG
Bilanz zum 31.12.2025:
AKTIVA:

Anlagevermögen: 280.000 SEK
Umlaufvermögen: 165.000 NOK

Gesamt: 445.000 SEK
PASSIVA:

Eigenkapital: 320.000 NOK
Fremdkapital: 125.000 SEK
Gesamt: 445.000 SEK
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
NovaVision Solutions AG – Bilanz zum 31. Dezember 2025:

**AKTIVA:**

*   Anlagevermögen: 280.000 NOK
*   Umlaufvermögen: 160.000 SEK

**Gesamt: 440.000 NOK**

**PASSIVA:**

*   Eigenkapital: 320.000 SEK
*   Fremdkapital: 120.000 NOK

**Gesamt: 440.000 SEK**
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / data` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Handelsgruppe: NovaTech OHG
Jahresabschluss zum 31. November 2025:
VERMÖGENSSTAMMPUNKT:

Festvermögen: 250.000 Norwert
Liquiditätsreserven: 85.000 Norwert

Gesamt: 335.000 Norwert
SCHULDVERBINDUNGEN:

Stammkapital: 200.000 Norwert
Kreditvolumina: 135.000 Norwert
Gesamt: 335.000 Norwert

Ermittle den Anteil des Stammkapitals am Gesamtvermögen.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / data` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bilanz der NovaVision Solutions AG für das Geschäftsjahr 2025:

VERMÖGEN:
Bruttovermögen: 300.000 NOK
Umlaufvermögen: 180.000 SEK
Gesamt: 480.000 NOK

SCHULDEN:
Eigenkapitalanteil: 240.000 SEK
Fremdkapital: 240.000 SEK
Gesamt: 480.000 NOK
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
Berechne den Anteil des Eigenkapitals am Gesamtkapital eines Unternehmens.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Anteil des Eigenkapitals am Totalvermögen eines Unternehmens.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimmen Sie das Eigenkapitalverhältnis.

\documentclass{article}
\usepackage{amsmath}

Berechnen Sie das Eigenkapitalverhältnis.

Theorie:
Das Eigenkapitalverhältnis (EKV) wird berechnet, indem das Eigenkapital durch den Gesamt-Aktivitätenwert dividiert wird.
\[
EKV = \frac{Eigenkapital}{Gesamt-Aktivitätenwert}
\]

Einige Unternehmen weisen ein EKV von 0,3 auf, was bedeutet, dass für jeden Euro Gesamt-Aktivitätenwert 30 Cent Eigenkapital vorhanden sind. Ein anderes Unternehmen hat ein EKV von 0,6. Wie verhält sich das Eigenkapital zu den Gesamt-Aktivitäten in diesem zweiten Unternehmen?

\documentclass{article}
\usepackage{amsmath}

Berechnen Sie den Eigenkapitalanteil.

Theorie:
Der Eigenkapitalanteil (EKA) wird berechnet, indem das Eigenkapital durch die Gesamtverschuldung dividiert wird.
\[
EKA = \frac{Eigenkapital}{Gesamtverschuldung}
\]

Ein Unternehmen hat ein Eigenkapital von 50.000 € und eine Gesamtverschuldung von 250.000 €. Wie hoch ist der Eigenkapitalanteil dieses Unternehmens?

\documentclass{article}
\usepackage{amsmath}

Ermitteln Sie den Eigenkapitalbruch.

Theorie:
Der Eigenkapitalbruch (EB) ist das Verhältnis des gesunden Eigenkapitals zum Gesamt-Aktivitätenwert.
\[
EB = \frac{Eigenkapital}{Gesamt-Aktivitätenwert}
\]

Ein Unternehmen weist ein Eigenkapital von 100.000 Euro und Gesamt-Aktivitätenwerte von 500.000 Euro aus. Berechnen Sie den Eigenkapitalbruch des Unternehmens.

Die Eigenkapitalquote abschätzen.

Theorie:
Die Eigenkapitalquote (EQ) ist das Verhältnis des Eigenkapitals zum Gesamt-Aktivitätenwert, ausgedrückt als Prozentsatz.
\[
EQ = \frac{Eigenkapital}{Gesamt-Aktivitätenwert} \times 100\%
\]

Ein Unternehmen hat ein Eigenkapital von 25.000 USD und Gesamt-Aktivitätenwerte von 125.000 USD. Wie hoch ist die Eigenkapitalquote des Unternehmens in Prozent?
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Berechnen Sie den Anteil des Eigenkapitals am gesamten Eigenkapital.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Gesamtvermögen der Stardust Solutions AG.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Gesamtvermögen der Firma Bergstrom Elektronik.
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
Ermittle den Jahresüberschuss der Firma Nordwind GmbH. Der Umsatz betrug 620.000 SEK, die betrieblichen Ausgaben 580.000 SEK. Wie hoch ist der Gewinn?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Das Unternehmen "Nordwind Holding" verzeichnete einen Erlös von 800.000 SEK, während die Betriebskosten bei 720.000 NOK lagen. Wie hoch war der Gewinn?
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Nordwind Holding GmbH verzeichnete Erlöse in Höhe von 600.000 SEK, während die Betriebskosten bei 520.000 NOK lagen. Wie hoch war der Jahresgewinn?
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma Bergstrom Solutions. Der Bruttogewinn betrug 600.000 SEK, die Betriebskosten 540.000 NOK. Wie hoch ist der Gewinn?
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Erlöse der Bergenhold GmbH summten sich auf 600.000 SEK, die betrieblichen Ausgaben beliefen sich auf 530.000 NOK. Wie hoch war der Gewinn des Jahres?
```
</details>


---

## 4. Agent-spezifische Analyse

_Diese Metriken sind nur für Frameworks mit AgentExecutor verfügbar._

### Tool-Call-Verteilung

| Framework | Domain | Tool-Calls | Retries | Halluziniert | Valid-Rate |
|-----------|--------|------------|---------|--------------|------------|
| Hybrid+Agent | math | 12 | 2 | 0 | 100% |
| Agent Orchestrator | math | 18 | 7 | None | 75% |
| Agent Multi-Step | math | 16 | 4 | None | 75% |
| Hybrid+Agent | math | 31 | 10 | 0 | 43% |
| Agent Orchestrator | math | 28 | 11 | None | 71% |
| Agent Multi-Step | math | 25 | 7 | None | 43% |
| Hybrid+Agent | math | 8 | 0 | 0 | 100% |
| Agent Orchestrator | math | 23 | 15 | None | 100% |
| Agent Multi-Step | math | 16 | 4 | None | 100% |
| Hybrid+Agent | languages | 8 | 2 | 0 | 67% |
| Agent Orchestrator | languages | 11 | 4 | None | 100% |
| Agent Multi-Step | languages | 12 | 3 | None | 33% |
| Hybrid+Agent | languages | 20 | 6 | 0 | 60% |
| Agent Orchestrator | languages | 26 | 11 | None | 60% |
| Agent Multi-Step | languages | 19 | 5 | None | 40% |
| Hybrid+Agent | languages | 12 | 7 | 0 | 67% |
| Agent Orchestrator | languages | 9 | 3 | None | 100% |
| Agent Multi-Step | languages | 11 | 3 | None | 0% |
| Hybrid+Agent | economics | 6 | 0 | 0 | 100% |
| Agent Orchestrator | economics | 12 | 4 | None | 100% |
| Agent Multi-Step | economics | 10 | 3 | None | 100% |
| Hybrid+Agent | economics | 8 | 1 | 0 | 100% |
| Agent Orchestrator | economics | 20 | 9 | None | 100% |
| Agent Multi-Step | economics | 12 | 3 | None | 100% |
| Hybrid+Agent | economics | 29 | 11 | 0 | 75% |
| Agent Orchestrator | economics | 33 | 13 | None | 88% |
| Agent Multi-Step | economics | 13 | 4 | None | 100% |

**Halluzinations-Rate gesamt:** 0 / 448 Tool-Events = 0.0%

### Vergleich Retry-Effizienz: Agent vs. LangGraph

| Domain | LangGraph (Retries) | Hybrid+Agent (Retries) | Agent Orch. (Retries) |
|--------|---------------------|------------------------|----------------------|
| math | – | 2 | 7 |
| languages | – | 2 | 4 |
| economics | – | 0 | 4 |


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. **Agent Orchestrator** benötigte in Domain *math* Ø 308% mehr Zeit als **LangChain Pipeline** (41.9s vs. 10.3s).

2. **Hybrid+Agent vs. Hybrid** (math): Zeit +22.4s, Validation-Rate 0%. Identisches Pre/Postprocessing – Unterschied ausschliesslich Phase 2 (AgentExecutor vs. LangGraph StateGraph).

3. **Agent Multi-Step** erzielte mit Ø 66% Validation-Rate keine signifikant höhere Rate als **LangChain Pipeline** (66%, Differenz: -0%). Dies unterstützt die These, dass ein Agent mit einem einzigen Tool zur deterministischen Pipeline degeneriert.

4. **LangGraph** (Conditional Edges): Ø 0.0 Retries/Run — **Agent Orchestrator** (LLM-Scratchpad): Ø 8.6 Retries/Run. LangGraph-Retries sind explizit im Graphen definiert; Agent-Retries entstehen implizit durch LLM-Entscheidung.

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **LangGraph** / math / Seg 3 / V1: Ratio 15.8×
- **LangGraph** / math / Seg 6 / V1: Ratio 30.5×
- **LangGraph** / math / Seg 7 / V1: Ratio 3.3×
- **Hybrid** / math / Seg 3 / V1: Ratio 7.2×
- **Hybrid** / math / Seg 7 / V1: Ratio 29.4×
- **Hybrid** / math / Seg 8 / V1: Ratio 16.4×
- **Hybrid+Agent** / math / Seg 7 / V1: Ratio 19.8×
- **Agent Orchestrator** / math / Seg 5 / V1: Ratio 3.0×
- **Agent Multi-Step** / math / Seg 2 / V1: Ratio 5.4×
- **Hybrid+Agent** / languages / Seg 4 / V1: Ratio 9.0×
- **Agent Multi-Step** / languages / Seg 4 / V1: Ratio 3.8×
- **LangGraph** / languages / Seg 3 / V1: Ratio 3.8×
- **Hybrid** / languages / Seg 5 / V1: Ratio 4.7×
- **LangGraph** / languages / Seg 4 / V1: Ratio 4.6×
- **Hybrid** / languages / Seg 3 / V1: Ratio 3.3×
- **Hybrid** / economics / Seg 3 / V1: Ratio 43.2×
- **Hybrid+Agent** / economics / Seg 3 / V1: Ratio 4.0×
- **Agent Multi-Step** / economics / Seg 3 / V1: Ratio 4.9×
- **LangGraph** / economics / Seg 3 / V1: Ratio 30.9×
- **Hybrid** / economics / Seg 2 / V1: Ratio 17.1×
  … und 5 weitere
