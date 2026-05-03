# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-03-16 15:33:09  |  **Varianten/Segment:** 1  |  **Frameworks:** 6  |  **Domains:** 3

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| LangChain | Chain → Chain → Chain | 12.2 | 67% | – | – |
| LangGraph | Node → StateGraph → Node | 26.3 | 78% | – | – |
| Hybrid | LC → LangGraph → LC | 15.5 | 78% | – | – |
| Hybrid+Agent | LC → AgentExecutor → LC | 25.7 | 89% | 0.7 | 6.7 |
| Agent Orchestrator | Chain → AgentExecutor → Chain | 39.1 | 81% | 4.7 | 16.0 |
| Agent Multi-Step | Chain → 3× Agent → Chain | 34.7 | 69% | 3.3 | 12.7 |


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
| LangChain | 5 | 4 / 4 | 100% | 10.6 | mistral | – | – | – |
| LangGraph | 5 | 4 / 4 | 100% | 18.4 | mistral | – | – | – |
| Hybrid | 5 | 4 / 4 | 100% | 12.8 | mistral | – | – | – |
| Hybrid+Agent | 5 | 4 / 4 | 100% | 26.1 | mistral | 8 | 0 | 0 |
| Agent Orchestrator | 5 | 3 / 4 | 75% | 43.9 | mistral | 21 | 9 | – |
| Agent Multi-Step | 5 | 3 / 4 | 75% | 36.0 | mistral | 15 | 4 | – |


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
Löse die Gleichung $3a + 2 = 11$
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $7a + 12 = 35$
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $4a + 10 = 26$.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $4y - 2 = 10$.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Berechne den Wert von *z*, wenn die Gleichung $7a - 3 = 26$ gilt.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Löse die Gleichung $5p - 3 = 17$
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
Aufgabe 2: Vereinfache: $5(a + 3) - 4(b - 2)$
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
Vereinfache: 5a + 20 - 3b + 6
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Vereinfache den Ausdruck: $5y + 30 - 3y + 6$
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
Berechne die Perimeter einer Dreiecksfläche, wenn ihre Seitenlängen gegeben sind als:  \(a = 8\) cm, \(b = 12\) cm und \(c = 15\) cm.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Umkreislinie eines Dreiecks, dessen Seitenlängen gegeben sind als: $s_1 = 5$ cm, $s_2 = 7$ cm und $s_3 = 9$ cm.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Umkreislinie eines Dreiecks, bei dem die Seitenlängen gegeben sind: $r_a = 5$, $r_b = 7$ und $r_c = 9$.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge des Umfangs eines Dreiecks, wenn die Längen seiner Seiten gegeben sind: $a = 12$ mm, $b = 15$ mm und $c = 18$ mm.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Bestimme die Länge der Umkreislinie eines Dreiecks, dessen Seitenlängen $p=8$ Meter, $q=12$ Meter und $r=15$ Meter sind.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechne die Länge der Umkreislinie eines Dreiecks, dessen Seitenlängen gegeben sind:  p = 5 Meter, q = 7 Meter, r = 9 Meter.
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
Aufgabe 4: Eine Einlage von 1500 € wird mit einem Zinssatz von 2,5 % pro Jahr verzinst. Berechnen Sie das Kapital nach 6 Jahren.
```
</details>


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1250 € wird mit einem Zinssatz von 3,5 % pro Jahr verzinst. Berechne den zukünftigen Wert der Investition nach 6 Jahren.
```
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Anlage von 1500 Dollar wird zu einem Zinssatz von 2,5 Prozent verzinst. Berechnen Sie den Kapitalbetrag, der nach sieben Jahren angespart wurde.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1250 Euro wird auf ein Konto angelegt, das eine jährliche Verzinsung von 4,5 Prozent bietet. Berechnen Sie nach sechs Jahren das zu erwartende Kapital.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1500 DM wird mit einem Zinssatz von 2,5 Prozent verzinst. Berechne das angesammelte Kapital am Ende eines Jahres.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 4: Eine Investition von 1250 Schweizer Franken wird mit einer jährlichen Verzinsung von 4,5% angelegt. Berechne das Resultat nach einer Anlageperiode von 8 Jahren.
```
</details>


---

## 3.2 Domäne: Sprachen (`languages`)

**PDF:** `languages/grammar_exercise.pdf` | **Validator:** BERTScore


### Metriken

| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR | Tool-Calls | Retries | Halluziniert |
|-----------|----------|----------------|------|----------|-----|------------|---------|--------------|
| LangChain | 4 | 1 / 3 | 33% | 15.4 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 20.8 | tesseract | – | – | – |
| Hybrid | 4 | 3 / 3 | 100% | 16.4 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 3 / 3 | 100% | 25.2 | tesseract | 8 | 2 | 0 |
| Agent Orchestrator | 4 | 3 / 3 | 100% | 23.7 | tesseract | 9 | 3 | – |
| Agent Multi-Step | 4 | 1 / 3 | 33% | 29.1 | tesseract | 13 | 3 | – |


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

□ Die Villa thronte auf □m Berg.
□ Jugendliche vergnügen sich im □ Garten.
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

Die Scheune thront auf dem Berg.
Die Schüler vergnügen sich im Park.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Ein Haus thront auf einem Berg.
Einige Jugendliche vergnügen sich im Vorgarten.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 1: Setze die richtigen Artikel ein:

Die Scheune thront auf dem Berg.
Jugendliche vergnügen sich im Garten.
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `general / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Die folgenden Sätze sollen mit den passenden Artikeln vervollständigt werden:

__ Das Haus thront auf __ Berg.
__ Die Kinder verspielten sich im __ Garten.
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

Die Schüler gehen zur Schule. —

Sie liest ein Buch. —
```
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Bilde das Perfekt:

Ich gehe in die Schule. – Er ging, wie er es tut.

Er liest ein Buch. – Sie liest, als ob ihre Gedanken sie leiten würden.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Er liest ein Buch vor sich.
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Forme die Perfekt-Form.
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

Welche Begriffe können als inhaltlich gleichwertig betrachtet werden?

flugartig – eilig – träge – ungestüm
```

> **Issues:** Länge weicht stark ab: 152 vs 63 Zeichen (Ratio: 2.41, erlaubt: 0.6-1.5)
</details>


**🔀 Hybrid** — Klassifiziert als `languages / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 3: Welche Wörter sind Synonyme?

Bitte wählen Sie aus den folgenden Begriffen diejenigen aus, die inhaltlich verwandt sind und eine ähnliche Bedeutung haben.

flink – eilfertig – geduldig – flott
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
Aufgabe 1: Setze die richtigen Artikel ein:

schnell - rasch - langsam - zügig

□ Die Nachricht erreichte uns innerhalb kürzester Zeit. / □ Der Zug fuhr mit einer unaufhaltsamen Geschwindigkeit voran. □ Die Arbeit wurde geduldig und bedächtig erledigt. / □ Er bewegte sich mit überaus hohem Tempo durch den Raum. □ Die Lösung des Problems erforderte eine sofortige und unüberlegte Reaktion. / □ Der Fluss plätscherte sanft und ruhig dahin.
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
| LangChain | 4 | 2 / 3 | 67% | 10.5 | tesseract | – | – | – |
| LangGraph | 4 | 2 / 3 | 67% | 39.7 | tesseract | – | – | – |
| Hybrid | 4 | 1 / 3 | 33% | 17.2 | tesseract | – | – | – |
| Hybrid+Agent | 4 | 2 / 3 | 67% | 25.7 | tesseract | 4 | 0 | 0 |
| Agent Orchestrator | 4 | 2 / 3 | 67% | 49.8 | tesseract | 18 | 2 | – |
| Agent Multi-Step | 4 | 3 / 3 | 100% | 38.9 | tesseract | 10 | 3 | – |


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
Unternehmen: NovaVision Solutions AG
Bilanz zum 31.08.2025:
BESTANDTEILE:

Wesentlich Vermögen: 210.000 SEK
Flüchtiges Vermögen: 95.000 NOK

Gesamt: 305.000 SEK
VERBINDLICHKEITEN:

Eigenkapital: 185.000 NOK
Fremdkapital: 120.000 SEK

Gesamt: 305.000 SEK
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaVision Solutions AG
Bilanz zum 31.12.2025:
VERMÖGENSPOSTEN:

Grundvermögen: 90.000 SEK
Umlaufmarge: 65.000 NOK

Gesamt: 155.000 SEK
SCHULDENVERBINDLICHEN:

Eigenkapitalanteil: 85.000 DKK
Verzinsungsposten: 70.000 ISRK

Gesamt: 155.000 DKK
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / example` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / example` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
NovaVision Solutions AG – Bilanz zum 31. Dezember 2025:

**VERMÖGENSPOSTEN:**

*   Fremdkapital: 105.000 SEK
*   Anlagevermögen: 210.000 NOK
*   Gesamt: 315.000 NOK

**SCHULDEN & FORDERUNGEN:**

*   Eigenkapital: 180.000 CHF
*   Fremdkapital: 135.000 DKK
*   Gesamt: 315.000 CHF
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / data` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaVision Solutions AG\nBilanz zum 31.12.2025:\nWERTE IN FRANKREICH (CHF):\n\nAnlagevermögen: 180.000 CHF\nUmlaufvermögen: 95.000 CHF\n\nGesamt: 275.000 CHF\nVERBINDLICHKEITEN:\n\nEigenkapital: 155.000 CHF\nFremdkapital: 120.000 CHF\nGesamt: 275.000 CHF
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / data` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Unternehmen: NovaFuture Solutions AG
Bilanz zum 31.12.2025:
VERMÖGENSSTÜCKE:

Fremdüberschlag: 90.000 SEK
Anlagevermögen: 180.000 NOK
Gesamt: 270.000 NOK
SCHULDEN UND FINANE:

Eigenkapital: 135.000 DKK
Fremdkapital: 135.000 CHF
Gesamt: 270.000 CHF

Berechne den Eigenkapitalanteil am Gesamtvermögen der StellarTech Holding.
```
</details>


#### Segment 3 — `task` — _Aufgabe 1: Berechne die Eigenkapitalquote._

**Original:**
```
Aufgabe 1: Berechne die Eigenkapitalquote.
```

**🔗 LangChain** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🕸️  LangGraph** — Klassifiziert als `mathematics / task` — 0/1 valide

<details>
<summary>Variante 1 — ❌ INVALID</summary>

```
Bestimme die Eigenkapitalquote.
\documentclass{article}
\usepackage{amsmath}

\begin{document}

Gegeben ein Unternehmen mit einem Gesamtkapital von 500.000 Euro und einer Schuldenlast von 300.000 Euro, berechne die Quote des Eigenkapitals im Verhältnis zum gesamten Kapitalwert.

\textbf{Theorie:}

Die Eigenkapitalquote wird berechnet, indem man den Wert des Eigenkapitals durch den Gesamtwert (Eigenkapital plus Schulden) teilt.
$$
\text{Eigenkapitalquote} = \frac{\text{Eigenkapital}}{\text{Gesamtkapital}}
$$

\textbf{Aufgabe:}

Berechne die Eigenkapitalquote für das oben genannte Unternehmen. Drücke das Ergebnis als Prozentsatz aus.
\end{document}
```

> **Issues:** Länge weicht stark ab: 654 vs 42 Zeichen (Ratio: 15.57, erlaubt: 0.5-2.0)
</details>


**🔀 Hybrid** — Klassifiziert als `mathematics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Berechnen Sie den Anteil des Eigenkapitals am Gesamtvermögen eines Unternehmens.

Theoretisch wird die Eigenkapitalquote ermittelt, indem Sie das Eigenkapital durch den Gesamtvermögenswert des Unternehmens teilen. Das Ergebnis wird anschließend als Dezimalzahl oder Prozentsatz angegeben.

Die Formel lautet: Eigenkapitalquote = Eigenkapital / Gesamtvermögen.

Beispiel: Wenn das Eigenkapital 50.000 € und das Gesamtvermögen 250.000 € beträgt, ergibt sich eine Eigenkapitalquote von 0,2 oder 20 %.

Aufgabe: Bestimmen Sie den Anteil des Eigenkapitals am Gesamtvermögen eines Unternehmens. Geben Sie das Ergebnis als Prozentsatz an, indem Sie die Werte für Eigenkapital und Gesamtvermögen entsprechend verändern.
```
</details>


**🤖 Hybrid+Agent** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**⚡ Agent Orchestrator** — Klassifiziert als `mathematics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Eigenkapitalanteil am Vermögen der Firma Heimtextilien AG.
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
Ermittle den Jahresüberschuss der Schmidt GmbH. Der Ertrag belief sich auf 600.000 SEK, die operativen Ausgaben auf 540.000 NOK. Wie hoch war der Gewinn?
```
</details>


**🕸️  LangGraph** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Der Jahreserlös von NovaTech AG belief sich auf 600.000 SEK, die Betriebskosten auf 540.000 NOK. Wie hoch ist der Jahresgewinn?
```
</details>


**🔀 Hybrid** — Klassifiziert als `economics / task` — 0/0 valide

_Keine Varianten generiert (Segment übersprungen)_


**🤖 Hybrid+Agent** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss von Helvetic Industries. Der Gesamtumsatz betrug 600’000 SEK, während die betrieblichen Ausgaben bei 530’000 NOK lagen. Wie hoch ist der Gewinn?
```
</details>


**⚡ Agent Orchestrator** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Ermittle den Jahresüberschuss der Firma Schneidwerk GmbH. Die Erlöse beliefen sich auf 620.000 SEK, die Betriebskosten auf 580.000 NOK
```
</details>


**📋 Agent Multi-Step** — Klassifiziert als `economics / task` — 1/1 valide

<details>
<summary>Variante 1 — ✅ VALIDE</summary>

```
Aufgabe 2: Die Erlöse der Firma NovaTech GmbH beliefen sich auf 600.000 SEK, die Betriebsausgaben auf 520.000 NOK. Wie gross ist der Gewinn?
```
</details>


---

## 4. Agent-spezifische Analyse

_Diese Metriken sind nur für Frameworks mit AgentExecutor verfügbar._

### Tool-Call-Verteilung

| Framework | Domain | Tool-Calls | Retries | Halluziniert | Valid-Rate |
|-----------|--------|------------|---------|--------------|------------|
| Hybrid+Agent | math | 8 | 0 | 0 | 100% |
| Agent Orchestrator | math | 21 | 9 | None | 75% |
| Agent Multi-Step | math | 15 | 4 | None | 75% |
| Hybrid+Agent | languages | 8 | 2 | 0 | 100% |
| Agent Orchestrator | languages | 9 | 3 | None | 100% |
| Agent Multi-Step | languages | 13 | 3 | None | 33% |
| Hybrid+Agent | economics | 4 | 0 | 0 | 67% |
| Agent Orchestrator | economics | 18 | 2 | None | 67% |
| Agent Multi-Step | economics | 10 | 3 | None | 100% |

**Halluzinations-Rate gesamt:** 0 / 106 Tool-Events = 0.0%

### Vergleich Retry-Effizienz: Agent vs. LangGraph

| Domain | LangGraph (Retries) | Hybrid+Agent (Retries) | Agent Orch. (Retries) |
|--------|---------------------|------------------------|----------------------|
| math | – | 0 | 9 |
| languages | – | 2 | 3 |
| economics | – | 0 | 2 |


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

1. **Agent Multi-Step** erzielte in der Domain *economics* die höchste Validation-Rate (100%).

2. **Agent Orchestrator** benötigte in Domain *math* Ø 315% mehr Zeit als **LangChain Pipeline** (43.9s vs. 10.6s).

3. **Hybrid+Agent vs. Hybrid** (math): Zeit +13.3s, Validation-Rate 0%. Identisches Pre/Postprocessing – Unterschied ausschliesslich Phase 2 (AgentExecutor vs. LangGraph StateGraph).

4. **Agent Multi-Step** erzielte mit Ø 69% Validation-Rate keine signifikant höhere Rate als **LangChain Pipeline** (67%, Differenz: +3%). Dies unterstützt die These, dass ein Agent mit einem einzigen Tool zur deterministischen Pipeline degeneriert.

5. **LangGraph** (Conditional Edges): Ø 0.0 Retries/Run — **Agent Orchestrator** (LLM-Scratchpad): Ø 4.7 Retries/Run. LangGraph-Retries sind explizit im Graphen definiert; Agent-Retries entstehen implizit durch LLM-Entscheidung.

---

## 6. Qualitäts-Auffälligkeiten

**⚠️ Extreme Längenabweichungen (> 3× Original):**
- **Agent Orchestrator** / languages / Seg 4 / V1: Ratio 5.9×
- **LangGraph** / economics / Seg 3 / V1: Ratio 15.6×
- **Hybrid** / economics / Seg 3 / V1: Ratio 16.9×
