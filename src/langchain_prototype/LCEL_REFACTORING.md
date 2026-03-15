# LCEL-Refactoring: LangChain-Prototyp

Dieses Dokument beschreibt die Umstellung der LangChain-Chains auf echtes
**LangChain Expression Language (LCEL)** und dient als Grundlage für
Kapitel 5.1 der Masterthesis.

---

## Ausgangslage

Die ursprünglichen Chains in `src/langchain_prototype/chains/` implementierten
eine `.invoke()`-Methode und nutzten intern den gemeinsamen `LLMHandler` aus
`common/llm_handler.py` (direkter OpenAI-SDK-Aufruf).  Sie importierten nichts
aus dem `langchain`-Package und waren damit **keine echten LangChain-
Komponenten**, obwohl sie das Interface imitierten.

---

## LCEL-Pattern

LCEL basiert auf dem `|`-Operator zur Komposition von Runnables:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    ("human", "{user_prompt}"),
])
llm = get_lcel_llm(temperature=0.7)   # Factory aus lcel_llm.py
parser = StrOutputParser()

chain = prompt | llm | parser          # LCEL-Komposition

result = chain.invoke({
    "system_prompt": SYSTEM_PROMPT,
    "user_prompt": user_prompt,
})
```

Jedes Element (`ChatPromptTemplate`, `ChatOpenAI`, `StrOutputParser`) ist ein
`Runnable`.  Der `|`-Operator verbindet sie zu einer sequenziellen Pipeline,
die lazy evaluiert wird.

---

## Umgestellte Komponenten

### 1. `lcel_llm.py` (neu)

Zentrale Factory-Datei für alle LCEL-Chains:

- **`get_lcel_llm(temperature, max_tokens)`** — gibt `ChatOpenAI` zurück,
  konfiguriert für OpenAI oder BFH (OpenAI-kompatibler Endpoint).  Der
  aktive Provider wird aus `Config.LLM_PROVIDER` gelesen; bei `'auto'` wird
  anhand vorhandener API-Keys entschieden.
- **`_extract_json(text)`** — extrahiert JSON aus LLM-Output: entfernt
  Markdown-Fences (` ```json `), korrigiert unescapte Backslashes (LaTeX)
  und fällt notfalls auf `ast.literal_eval` zurück.  Entspricht der
  Logik aus `common/llm_handler.py::generate_structured()`.

### 2. `chains/segmentation_chain.py`

| Vorher | Nachher |
|--------|---------|
| `LLMHandler.generate_structured()` | `ChatPromptTemplate \| ChatOpenAI \| StrOutputParser` |

Temperature `0.3` (deterministische Segmentierung).  JSON-Parsing via
`_extract_json()`.

### 3. `chains/classification_chain.py`

| Vorher | Nachher |
|--------|---------|
| `LLMHandler.generate_structured()` | `ChatPromptTemplate \| ChatOpenAI \| StrOutputParser` |

Temperature `0.1` (sehr deterministisch für Klassifizierung).

### 4. `chains/rewriting_chain.py`

Komplexeste Umstellung wegen Diversity-Mechanismus und Temperature-Paradox:

- Schleifenlogik (Varianten-Generierung, Similarity-Check, Retry) bleibt
  vollständig erhalten.
- Für jeden Versuch wird via `_build_rewriting_chain(temperature)` eine neue
  LCEL-Chain aufgebaut: `prompt | ChatOpenAI(temperature=t) | StrOutputParser`.
- **Temperature-Paradox** (unverändert beibehalten):
  - Domain `languages`: konstant `temperature=0.7` — BERTScore erfordert
    semantische Nähe zwischen Original und Variante; zu hohe Kreativität
    führt zu Validierungsfehlern.
  - Andere Domains: `temperature = 0.9 + (attempt × 0.05)` — steigt bei
    Wiederholungen, um mehr Diversität zu erzwingen.

---

## Unveränderte Komponenten (RunnableLambda-Wrapper)

Diese Chains machen **keinen LLM-Aufruf** und werden daher nicht auf
`ChatPromptTemplate | ChatOpenAI` umgestellt.  Um sie formal LCEL-kompatibel
zu machen, erhält jede Klasse ein `self._runnable = RunnableLambda(self.invoke)`
Attribut.

### 5. `chains/parsing_chain.py`

OCR (Tesseract / Mistral) ist kein LLM-Schritt.  Der `OCRHandler` aus
`common/ocr_handler.py` wird unverändert verwendet.

### 6. `chains/assembly_chain.py`

Dokument-Aggregation ohne LLM.  Baut das finale Varianten-Dokument aus den
validierten Segmenten zusammen.

### 7. `chains/validation_chain.py`

Validierung durch Fachbibliotheken:
- **SymPy** (Domain `mathematics`): prüft Gleichungsstruktur
- **BERTScore** (Domain `languages`): semantische Ähnlichkeit
- **ConsistencyValidator** (Domain `economics`): Zahlenkonsistenz

Kein LLM-Aufruf.  Der Prompt-Leak-Check (`_has_prompt_leak()`) ist ein
einfacher String-Vergleich.

---

## Interface-Kompatibilität

`pipeline.py` wurde **nicht verändert**.  Alle Chains behalten die Signatur:

```python
chain.invoke(input_dict: Dict) -> Dict
```

Die Rückgabe-Dicts sind identisch zur ursprünglichen Implementierung, sodass
der LangChain-Prototyp ohne Anpassungen an der Pipeline-Logik läuft.

---

## Neue Abhängigkeit

`langchain-openai>=0.2.0` wurde zu `requirements.txt` hinzugefügt.
Dieses Package stellt `ChatOpenAI` bereit, das in der LCEL-Komposition als
LLM-Runnable fungiert.

---

## Methodische Einordnung (Thesis)

Durch das Refactoring verwendet der LangChain-Prototyp jetzt echte
LangChain-Primitive:

- `ChatPromptTemplate` — deklarative Prompt-Verwaltung
- `ChatOpenAI` — LangChain-gekapseltes LLM
- `StrOutputParser` — standardisierter Output-Parser
- `RunnableLambda` — LCEL-Adapter für Nicht-LLM-Schritte
- `|`-Operator — LCEL-Kompositionsoperator

Damit ist der methodische Vergleich *LangChain (LCEL) vs. LangGraph
(StateGraph)* korrekt abgebildet: Beide Prototypen nutzen ihre jeweiligen
Kern-Abstraktionen des LangChain-Ökosystems.
