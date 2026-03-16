# LangChain Agent Prototype — Architektur

## Überblick

Dieser Prototyp implementiert denselben Content-Rewriting-Workflow wie
`langchain_prototype` und `langgraph_prototype`, aber nutzt das
**LangChain Agenten-Pattern** (`create_tool_calling_agent` + `AgentExecutor`).

Zwei Varianten werden verglichen:
- **Variante A** — Orchestrierungsagent (ein Agent, alle Tools)
- **Variante B** — Multi-Agent-Pipeline (drei Agenten, je ein Tool)

---

## Gemeinsame Tools (`tools/rewriting_tools.py`)

Beide Varianten teilen dieselben `@tool`-dekorierten Funktionen:

| Tool | Beschreibung | Intern | Return |
|------|-------------|--------|--------|
| `classify_segment(text)` | Domain/Typ-Klassifizierung | LCEL-Chain (ChatOpenAI) | JSON-String |
| `rewrite_segment(text, domain, hint)` | Varianten-Generierung | LCEL-Chain (ChatOpenAI) | Varianten-Text |
| `validate_variant(original, variant, domain)` | Validierung | SymPy / BERTScore / Konsistenz | JSON-String |

Tools geben immer `str` zurück — Voraussetzung von `AgentExecutor`.

---

## Variante A: Orchestrierungsagent (`orchestrator/agent.py`)

### Pattern: ReAct (Reason → Act → Observe → Repeat)

```
Eingabe: "Segment: <text>"
    ↓
AgentExecutor (LangChain)
    ↓ Tool-Call
classify_segment → {"domain": "mathematics", ...}
    ↓ Tool-Call
rewrite_segment  → "Aufgabe 1: Löse 3y - 7 = 11"
    ↓ Tool-Call
validate_variant → {"is_valid": true, ...}
    ↓ (falls is_valid=false)
rewrite_segment  → "..." (erneut, mit hint)
    ↓ Tool-Call
validate_variant → ...
    ↓
Ausgabe: "FINALE_VARIANTE: <beste Variante>"
```

### LangChain-Komponenten

- `create_tool_calling_agent` — verbindet LLM, Prompt und Tools zu einem Agenten
- `AgentExecutor` — Ausführungs-Loop: ruft Tool-Calls aus, beobachtet Outputs,
  entscheidet über Fortsetzung oder Abschluss
- `MessagesPlaceholder(variable_name="agent_scratchpad")` — intermediate steps
  als Kontext für das LLM sichtbar (Basis des ReAct-Patterns)

### Kontrollfluss

Das LLM entscheidet autonom:
1. Welches Tool es aufruft
2. Wie es auf Tool-Outputs reagiert
3. Wann es mit einer finalen Antwort abbricht

Retry-Logik ist **implizit**: Falls Validierung fehlschlägt, erkennt das LLM
das Problem im Scratchpad und ruft `rewrite_segment` mit einem `hint` erneut auf.
`max_iterations` begrenzt die Gesamtanzahl der Schritte.

### Thesis-Relevanz

Variante A zeigt das echte Agenten-Pattern: Das LLM hat Handlungsspielraum,
kann die Reihenfolge der Tool-Aufrufe anpassen und aus Beobachtungen lernen.
`return_intermediate_steps=True` liefert die vollständige Tool-Call-Sequenz
für Thesis-Auswertung (Anzahl Iterationen, welche Tools wie oft).

---

## Variante B: Multi-Agent Pipeline (`multi_agent/pipeline.py`)

### Pattern: Spezialisierte Einzelagenten hintereinander

```
ClassifierAgent (1 Tool: classify_segment)
    ↓ domain
RewriterAgent   (1 Tool: rewrite_segment)
    ↓ variant
ValidatorAgent  (1 Tool: validate_variant)
    ↓
Ergebnis (kein Retry)
```

### LangChain-Komponenten

- 3× `create_tool_calling_agent` — je ein spezialisierter Agent
- 3× `AgentExecutor` — je `max_iterations=2` (exakt 1 Tool-Call pro Agent)

### WICHTIGE EINSCHRÄNKUNG (methodisch relevant für Thesis)

> **Ein Agent mit nur einem Tool kann keine echte autonome Entscheidung treffen.**
> Er ruft immer dasselbe Tool aus — das ist strukturell identisch zu einem
> direkten Funktionsaufruf.

Konsequenzen:
- **Keine Retry-Logik**: Kein übergeordneter Koordinator → bei invalider
  Variante wird das Ergebnis trotzdem zurückgegeben.
- **Degeneriert zur Pipeline**: Sequenz aus drei deterministischen Schritten,
  nicht von drei Agenten mit autonomer Entscheidungsfähigkeit.
- **Overhead ohne Mehrwert**: Der Agenten-Mechanismus (LLM-basiertes Routing)
  fügt Latenz und Kosten hinzu ohne den Workflow zu verbessern.

### Thesis-Relevanz

Variante B dient als empirischer Beweis:
Der Mehrwert des Agenten-Patterns entsteht erst durch die **Wahlmöglichkeit
zwischen mehreren Tools** (Variante A) — nicht durch die blosse Verwendung
des `AgentExecutor`-Mechanismus.

Der Vergleich A vs. B macht messbar, was Autonomie in LangChain-Agenten bedeutet.

---

## Pipeline-Wrapper (`pipeline.py`)

```
Phase 1 (Preprocessing):  Parsing → Segmentierung → Klassifizierung
                           → LangChain-Chains aus langchain_prototype
Phase 2 (Agenten):         Pro Segment: run_orchestrator() oder
                                         run_multi_agent_pipeline()
Phase 3 (Assembly):        AssemblyChain aus langchain_prototype
```

Output: Kompatibel mit langchain_prototype und langgraph_prototype.
Zusätzlich: `_agent_stats.json` mit Tool-Call-Sequenzen für Thesis-Auswertung.

---

## Vergleich der vier Prototypen

| Eigenschaft | LangChain | LangGraph | Agent A | Agent B |
|------------|-----------|-----------|---------|---------|
| Kontrollfluss | Explizit sequenziell | StateGraph (deklarativ) | LLM-autonom | LLM-pseudoautonom |
| Retry-Logik | RewritingChain-intern | Conditional Edge | Agent-Scratchpad | Keine |
| Tool-Wahlfreiheit | Nein | Nein | Ja | Nein (1 Tool pro Agent) |
| Determinismus | Hoch | Hoch | Niedrig | Mittel |
| Interpretierbarkeit | Hoch | Hoch | Niedrig | Mittel |
| Overhead | Niedrig | Mittel | Hoch | Hoch |

---

## Laufzeit-Analyse

### Vergleich Test-Script vs. Produktiv-Run

| Kontext         | Segmente | LLM-Calls | Laufzeit      |
|-----------------|----------|-----------|---------------|
| Test-Script     | 1        | ~4        | ~15s          |
| Frontend-Run    | ~12      | ~61       | ~5–7 Min      |

Das Test-Script (`test_agent_orchestrator.py`) verarbeitet ein einzelnes
hardcodiertes Segment und überspringt OCR, Segmentierung und Klassifizierung.
Der Unterschied ist strukturell, kein Bug: Beide Wege nutzen dieselbe
`run_orchestrator()`-Funktion — aber der Frontend-Run ruft sie ~12× auf.

### LLM-Call-Aufschlüsselung (Orchestrator, 12 Segmente)

| Phase                           | Calls |
|---------------------------------|-------|
| Segmentation                    | 1     |
| Classification (via Agent-Tool) | 12    |
| Agent: rewrite_segment          | 12    |
| Agent: validate_variant         | 12    |
| AgentExecutor-Reasoning         | ~24   |
| **Total**                       | **~61** |

Hinweis: Die explizite Classification-Chain (Phase 1c) wurde aus
`run_agent_pipeline.py` entfernt — der Agent klassifiziert via
`classify_segment`-Tool selbst. Spart ~12 redundante LLM-Calls.

### Thesis-Relevanz

Die Laufzeit ist kein Implementierungsfehler, sondern ein messbarer
Kostenfaktor der Agenten-Architektur. Im Vergleich: Die deterministische
LangChain-Pipeline benötigt für dasselbe Dokument ~12s (~14 LLM-Calls).

**Faktor: ~30× mehr Zeit bei ~3% höherer Validation-Rate.**

Das ist das zentrale Ergebnis des Architekturvergleichs: Das Agenten-Pattern
bietet Flexibilität (autonome Tool-Wahl, implizite Retry-Logik) auf Kosten
von Latenz und Vorhersagbarkeit.

---

## Dateistruktur

```
src/langchain_agent_prototype/
├── pipeline.py                    ← End-to-End Pipeline (beide Varianten)
├── ARCHITECTURE.md                ← Dieses Dokument
├── tools/
│   └── rewriting_tools.py         ← @tool Definitionen (gemeinsam)
├── orchestrator/
│   └── agent.py                   ← Variante A: Orchestrierungsagent
└── multi_agent/
    └── pipeline.py                ← Variante B: 3 Agenten, je 1 Tool
```
