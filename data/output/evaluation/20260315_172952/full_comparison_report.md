# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-03-15 17:29:52  |  **Varianten/Segment:** 1  |  **Frameworks:** 6  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 12.4 | 89% | – | – |
| LangGraph | Node → StateGraph → Node | 21.0 | 89% | – | – |
| Hybrid | LC → LangGraph → LC | 14.7 | 78% | – | – |
| Hybrid+Agent | LC → AgentExecutor → LC | 34.2 | 67% | 3.3 | 9.0 |
| Agent Orchestrator | Chain → AgentExecutor → Chain | 62.8 | 92% | 4.7 | 16.0 |
| Agent Multi-Step | Chain → 3× Agent → Chain | 34.2 | 58% | 3.3 | 12.7 |


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

**PDF:** `math/equations_simple.pdf` | **Validator:** SymPy


### Metriken

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 5 | 4 / 4 | 100% | 10.3 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 20.6 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 12.6 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 30.3 | mistral | 9 | 1 | 0 |
| Agent Orchestrator | 5 | 3 / 4 | 75% | 34.7 | mistral | 13 | 5 | – |
| Agent Multi-Step | 5 | 3 / 4 | 75% | 39.0 | mistral | 15 | 4 | – |


### Segment-Vergleich (Volltext)

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
Löse die Gleichung $3y - 7 = 16$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $7y - 3 = 26$.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die Gleichung $3a + 7 = 20$ kann wie folgt gelöst werden:

Zuerst subtrahiere ich von beiden Seiten 7:
$3a = 13$

Dann teile ich beide Seiten durch 3:
$a = \frac{13}{3}$
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $4y - 7 = 15$
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $3a + 7 = 20$
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
Vereinfache: $5(a + 3) - 4(b - 2)$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache: $5(a + 3) - 4(b - 2)$
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
Das Ergebnis ist 3m - 9n + 81.
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
Aufgabe 3: Bestimme den Umfang eines Dreiecks, dessen Seitenlängen gegeben sind: $u = 5$, $v = 7$ und $w = 9$.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Gegeben sind die Längen der Seiten eines Dreiecks:  s = 5 m, t = 7 m und u = 9 m. Berechne den Umfang des Dreiecks.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Umfang eines Dreiecks, dessen Seitenlängen wie folgt gegeben sind: $s_1 = 8$ m, $s_2 = 10$ m und $s_3 = 12$ m.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Umfang der geometrischen Figur, die durch die Seitenlängen $a = 8$ dm, $b = 12$ dm und $c = 15$ dm gegeben ist.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Perimeter eines Dreiecks, wenn die Längen der Kanten jeweils $a=8$ cm, $b=12$ cm und $c=15$ cm betragen.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Begrenzung eines dreiseitigen Polygons, wenn die Längen der Seiten gegeben sind: p = 15 m, q = 20 m, r = 25 m
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
Aufgabe 4: Eine Investition von 2500 DM wird mit einem Zinssatz von 4,5 Prozent verzinst. Berechne das Kapital nach 6 Jahren.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Anlage von 1500 Dollar wird mit einer jährlichen Verzinsung von 4,5 Prozent angelegt. Berechne das angesammelte Kapital nach 6 Jahren.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Ein Betrag von 1250 Euro wird auf ein Sparkonto angelegt, dessen jährliche Verzinsung bei 4,5 Prozent liegt. Berechnen Sie das Kapital nach sechs Jahren unter Berücksichtigung des Säumniszinses.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 Euro wird auf ein Darlehen mit einer jährlichen Verzinsung von 4,5 Prozent angelegt. Wie hoch ist das Kapital nach sechs Jahren?
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 DM wird mit einer jährlichen Verzinsung von 2,75% angelegt. Ermitteln Sie das Kapital nach einer Anlageperiode von dreizehn Monaten.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Anlagemenge von 1500 Dollar wird zu 6,5 Prozent Zinsen investiert. Ermitteln Sie das resultierende Kapital nach 8 Jahren.
```
</details>


---

## 3.2 Domäne: Sprachen (`languages`)

**PDF:** `languages/grammar_exercise.pdf` | **Validator:** BERTScore


### Metriken

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 2 / 3 | 67% | 18.0 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 20.6 | tesseract | – | – | – |
| Hybrid | 4 | 3 / 3 | 100% | 16.1 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 1 / 3 | 33% | 32.0 | tesseract | 10 | 7 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 31.5 | tesseract | 12 | 4 | – |
| Agent Multi-Step | 4 | 1 / 3 | 33% | 34.3 | tesseract | 14 | 3 | – |


### Segment-Vergleich (Volltext)

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

Das Haus befindet sich auf einem Hügel.
Die Kinder verspielten sich im Garten.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Setze die richtigen Artikel ein:

□ Schloss thront auf □ Berg.
□ Jugendliche toben in □ Park.
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Villa thront auf einem Berg.
Die Kleinkinder toben im Garten.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Villa thront auf dem Berg.
Die Jugendliche vergnügen sich im Park.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `general / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ausführung:

Das Heim thront auf einem Berg. Die Ernte liegt in der Wiese.
Die Kleinen versöhnen sich im Garten.
```
</details>


#### Segment 3 — `task` — _Aufgabe 2: Bilde das Perfekt:  Ich gehe in die Schule. —  er liest ein Buch. —_

**Original:**
```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. —

er liest ein Buch. —
```

**🔗 LangChain** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich besuche die Schule. —

Er liest ein Buch. —
```
</details>


**🕸️  LangGraph** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bilde das Perfekt:

Er geht zur Schule. —

Sie liest ein Buch. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. – Er ist in die Schule gegangen.

Er liest ein Buch. – Sie versinkt in dem Buch.

Liest er das Buch? – Hat er das Buch bereits vollständig gelesen?
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bewerte die Vollendetemporalform der genannten Verben in die jeweils korrekte Form des Passé Composé um. Berücksichtige dabei die Konjugation und die korrekten Hilfsverben.[TOOL_RESULT]
[END_TOOL_RESULT]
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

schnell – rasch – langsam – zügig

Formuliere eine inhaltlich exakt gleich bleibende, jedoch deutlicher veränderte Version.
```

> **Issues:** Länge weicht stark ab: 198 vs 63 Zeichen (Ratio: 3.14, erlaubt: 0.6-1.5)
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

Welche der genannten Begriffe weist die größte semantische Ähnlichkeit auf? Berücksichtigen Sie dabei die unterschiedlichen Konnotationen und Nuancen der Wörter.

schnell – rasch – langsam – zügig
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

Nennen Sie bitte Synonyme für die folgenden Begriffe:

schnell – rasch – langsam – zügig
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `general / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
schnell - rasch - langsam - zügig.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `languages / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


---

## 3.3 Domäne: Wirtschaft (`economics`)

**PDF:** `economics/balance_sheet.pdf` | **Validator:** ConsistencyCheck


### Metriken

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 3 / 3 | 100% | 8.9 | tesseract | – | – | – |
| LangGraph | 4 | 3 / 3 | 100% | 21.8 | tesseract | – | – | – |
| Hybrid | 4 | 1 / 3 | 33% | 15.4 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 2 / 3 | 67% | 40.5 | tesseract | 8 | 2 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 122.1 | tesseract | 23 | 5 | – |
| Agent Multi-Step | 4 | 2 / 3 | 67% | 29.4 | tesseract | 9 | 3 | – |


### Segment-Vergleich (Volltext)

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
Unternehmen: InnovaVision Solutions AG
Bilanz zum 31.08.2025:
AKTIVA:

Anlagevermögen: 175.000 SEK
Umlaufvermögen: 95.000 NOK

Gesamt: 270.000 NOK
PASSIVA:

Eigenkapital: 155.000 SEK
Fremdkapital: 115.000 NOK

Gesamt: 270.000 SEK
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaTech Solutions AG
Bilanz zum 31.08.2025:
WERTE:
Investitionsvermögen: 175.000 SEK
Liquiden Mittel: 65.000 NOK
Gesamt: 240.000 SEK
VERBINDLICHKEITEN:
Stammkapital: 135.000 SEK
Kredite: 105.000 SEK
Gesamt: 240.000 SEK

Ermittle den Eigenkapitalanteil am Gesamtvermögen.
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
Unternehmen: VisionTech International GmbH
Bilanz zum 31.08.2026:
Vermögen:

Festvermögen: 195.000 DKK
Bargeldreserven: 70.000 PLN

Gesamt: 265.000 DKK
Forderungen:

Eigenkapital: 170.000 PLN
Anleihen: 120.000 DKK
Gesamt: 290.000 DKK
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / data` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


#### Segment 3 — `task` — _Aufgabe 1: Berechne die Eigenkapitalquote._

**Original:**
```
Aufgabe 1: Berechne die Eigenkapitalquote.
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Ermittle den Anteil des Eigenkapitals am gesamten Vermögen.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne den Anteil des Eigenkapitals an den gesamten Aktiengewinnen.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Berechne den Anteil des Eigenkapitals am Gesamtvermögen eines Unternehmens.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Berechnen Sie den Anteil des Kurswerts an der Gesamtkapitalisierung einer Aktiengesellschaft, wobei der Kurswert 120.000 € und das Gesamtvermögen 600.000 € beträgt.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Bestimme den Prozentsatz des Eigenkapitals im Vermögen eines Unternehmens. Berechne den Kapitalanteil nach der Formel: Kapitalanteil = (Eigencapital / Gesamtsystemvermögen) * 100.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Gesamtvermögen der Firma StahlKraft AG.
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
Ermittle den Jahresüberschuss der Firma Stark GmbH. Der Erlös belief sich auf 600'000 SEK, die laufenden Ausgaben auf 520'000 NOK. Wie hoch war der Gewinn?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Erlöse der Schmidt GmbH beliefen sich auf 800.000 SEK, die Kalkulationskosten auf 720.000 NOK. Wie hoch ist der Gewinnbetrag?
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma Berg & Sohn. Im vergangenen Geschäftsjahr lag dieser bei 620.000 SEK, während die Betriebskosten mit 580.000 NOK zu Buche gingen. Wie hoch war der Gewinn?
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der "NovaTech Solutions Ltd.". Der Ertrag belief sich auf 600.000 SEK, die Betriebskosten auf 540.000 NOK.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Erlöse der Firma Berg & Sohn GmbH summierten sich auf 600.000 SEK, die Betriebskosten beliefen sich auf 520.000 NOK. Wie hoch war der Gewinn?
```
</details>


---

## 4. Agent-spezifische Analyse

_Diese Metriken sind nur für Frameworks mit AgentExecutor verfügbar._

### Tool-Call-Verteilung

| Framework | Domain | Tool-Calls | Retries | Halluziniert | Valid-Rate |
|-----------|--------|------------|---------|--------------|------------|
| Hybrid+Agent | math | 9 | 1 | 0 | 100% |
| Agent Orchestrator | math | 13 | 5 | None | 75% |
| Agent Multi-Step | math | 15 | 4 | None | 75% |
| Hybrid+Agent | languages | 10 | 7 | 0 | 33% |
| Agent Orchestrator | languages | 12 | 4 | None | 100% |
| Agent Multi-Step | languages | 14 | 3 | None | 33% |
| Hybrid+Agent | economics | 8 | 2 | 0 | 67% |
| Agent Orchestrator | economics | 23 | 5 | None | 100% |
| Agent Multi-Step | economics | 9 | 3 | None | 67% |

**Halluzinations-Rate gesamt:** 0 / 113 Tool-Events = 0.0%

### Vergleich Retry-Effizienz: Agent vs. LangGraph

| Domain | LangGraph (Retries) | Hybrid+Agent (Retries) | Agent Orch. (Retries) |
|--------|---------------------|------------------------|----------------------|
| math | – | 1 | 5 |
| languages | – | 7 | 4 |
| economics | – | 2 | 5 |


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. **Agent Orchestrator** benötigte in Domain *math* Ø 237% mehr Zeit als **LangChain Pipeline** (34.7s vs. 10.3s).

2. **Hybrid+Agent vs. Hybrid** (math): Zeit +17.7s, Validation-Rate 0%. Identisches Pre/Postprocessing – Unterschied ausschliesslich Phase 2 (AgentExecutor vs. LangGraph StateGraph).

3. **LangGraph** (Conditional Edges): Ø 0.0 Retries/Run — **Agent Orchestrator** (LLM-Scratchpad): Ø 4.7 Retries/Run. LangGraph-Retries sind explizit im Graphen definiert; Agent-Retries entstehen implizit durch LLM-Entscheidung.

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **Hybrid+Agent** / math / Seg 2 / V1: Ratio 3.9×
- **LangGraph** / languages / Seg 4 / V1: Ratio 3.1×
- **Hybrid** / languages / Seg 4 / V1: Ratio 3.2×
- **Hybrid+Agent** / economics / Seg 3 / V1: Ratio 4.2×
- **Agent Orchestrator** / economics / Seg 3 / V1: Ratio 4.3×
