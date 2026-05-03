# Framework-Vergleich: Alle Prototypen

**Datum:** 2026-03-16 10:18:16  |  **Varianten/Segment:** 1  |  **Frameworks:** 1  |  **Domains:** 1

---


## 1. Zusammenfassung

| Framework | Architektur | Ø Zeit (s) | Ø Validation-Rate | Ø Retries | Ø Tool-Calls |
|-----------|-------------|------------|--------------------|-----------|-------------|
| Agent Multi-Step | Chain → 3× Agent → Chain | – | – | – | – |


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
| Agent Multi-Step | – | – | – | – | – | – | – | – |


### Segment-Vergleich (Volltext)


---

## 5. Thesis-Erkenntnisse (auto-generiert)

_Diese Beobachtungen basieren auf den gemessenen Werten und können direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._

_Keine erfolgreichen Runs – keine Beobachtungen möglich._

---

## 6. Qualitäts-Auffälligkeiten

_Keine automatisch erkannten Auffälligkeiten._
