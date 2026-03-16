"""
Variante A: Orchestrierungsagent
Ein einzelner Agent mit Zugriff auf alle drei Tools.

Das LLM entscheidet autonom:
  1. Welches Tool es wann aufruft
  2. Wie es auf Tool-Resultate reagiert (Retry bei Validierungsfehler)
  3. Wann es mit einer finalen Variante antwortet

LangChain-Komponenten:
  - create_tool_calling_agent  (ReAct-Pattern via function calling)
  - AgentExecutor              (Ausführungs-Loop mit Tool-Dispatch)
  - MessagesPlaceholder        (Scratchpad für intermediate steps)
"""
import json
import re
from typing import Any, Dict, List, Optional

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common.logger import setup_logger
from langchain_prototype.lcel_llm import get_lcel_llm
from langchain_agent_prototype.tools.rewriting_tools import (
    classify_segment,
    rewrite_segment,
    validate_variant,
)

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# System-Prompt Template
# ---------------------------------------------------------------------------
# WICHTIG: {max_retries} wird VOR ChatPromptTemplate.from_messages() via
# .format() eingesetzt, da der Template-Mechanismus sonst versucht, es
# aus den invoke()-Inputs zu befüllen.

_SYSTEM_PROMPT_TEMPLATE = """Du bist ein Rewriting-Agent für Bildungsmaterialien.

Dein Auftrag: Erstelle eine valide Variante des gegebenen Textsegments.

Vorgehensweise:
1. Klassifiziere das Segment mit classify_segment um die Domain zu bestimmen.
2. Generiere eine Variante mit rewrite_segment (verwende die ermittelte Domain).
3. Validiere die Variante mit validate_variant.
4. Falls die Validierung fehlschlägt: Rufe rewrite_segment erneut auf.
   Setze dabei den hint-Parameter mit einer kurzen Beschreibung des Problems.
   Maximal {max_retries} Rewriting-Versuche insgesamt.
5. Am Ende antworte mit dem Marker:
   FINALE_VARIANTE: <text der besten Variante>

Falls keine Validierung erfolgreich war, gib trotzdem die beste verfügbare
Variante aus.
"""


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_orchestrator_agent(max_retries: int = 3) -> AgentExecutor:
    """
    Erstellt AgentExecutor für den Orchestrierungsagenten.

    Args:
        max_retries: Max. Anzahl Rewriting-Versuche pro Segment.

    Returns:
        AgentExecutor mit allen drei Tools.
    """
    llm = get_lcel_llm(temperature=0.7)
    tools = [classify_segment, rewrite_segment, validate_variant]

    system_content = _SYSTEM_PROMPT_TEMPLATE.format(max_retries=max_retries)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_content),
        ("human", "Segment: {input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=max_retries * 3 + 3,  # classify + N*(rewrite+validate)
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    logger.info(
        f"OrchestratorAgent erstellt (max_retries={max_retries}, "
        f"max_iterations={max_retries * 3 + 3})"
    )
    return executor


# ---------------------------------------------------------------------------
# Hilfsfunktionen für Output-Parsing
# ---------------------------------------------------------------------------

def _extract_final_variant(output: str) -> Optional[str]:
    """
    Extrahiert den Varianten-Text nach dem FINALE_VARIANTE:-Marker.
    Gibt None zurück falls kein Marker gefunden.
    """
    match = re.search(r"FINALE_VARIANTE:\s*(.+)", output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _parse_tool_calls(intermediate_steps: List) -> List[Dict]:
    """
    Extrahiert eine kompakte Tool-Call-Sequenz aus den intermediate_steps.

    Gibt eine Liste zurück wie:
      [{"tool": "classify_segment", "input_len": 43, "output_preview": "..."},
       {"tool": "rewrite_segment", ...}, ...]

    Nützlich für die Thesis-Auswertung (wie viele Iterationen, welche Reihenfolge).
    """
    calls = []
    for action, observation in intermediate_steps:
        tool_name = getattr(action, "tool", str(action))
        tool_input = getattr(action, "tool_input", {})

        # Bestimme Input-Länge (erste String-Wert im Dict)
        input_len = 0
        if isinstance(tool_input, dict):
            for v in tool_input.values():
                if isinstance(v, str):
                    input_len = len(v)
                    break
        elif isinstance(tool_input, str):
            input_len = len(tool_input)

        calls.append({
            "tool": tool_name,
            "input_len": input_len,
            "output_preview": str(observation)[:80],
        })
    return calls


# ---------------------------------------------------------------------------
# Haupt-Ausführungsfunktion
# ---------------------------------------------------------------------------

def run_orchestrator(
    segment: Dict,
    domain_hint: Optional[str] = None,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    Führt den Orchestrierungsagenten für ein einzelnes Segment aus.

    Der Agent entscheidet autonom über die Tool-Reihenfolge und Retries.

    Args:
        segment:     Dict mit 'text' (und optional 'type').
        domain_hint: Optionaler Domain-Hinweis (wird dem Segment-Text angehängt).
        max_retries: Max. Rewriting-Versuche.

    Returns:
        {
          'original':   str,   — Original-Text
          'variant':    str,   — Beste gefundene Variante
          'domain':     str,   — Ermittelte Domain
          'is_valid':   bool,  — Ob Variante die Validierung bestanden hat
          'tool_calls': [...], — Für Thesis: Tool-Sequenz mit Details
          'attempts':   int,   — Anzahl Rewriting-Versuche
          'success':    bool,  — True wenn Variante vorhanden
        }
    """
    text = segment.get("text", "")
    segment_input = text
    if domain_hint:
        segment_input += f"\n\n[Domain-Hinweis: {domain_hint}]"

    logger.info(f"OrchestratorAgent: starte für Segment ({len(text)} Zeichen)")

    try:
        executor = create_orchestrator_agent(max_retries=max_retries)
        result = executor.invoke({"input": segment_input})
    except Exception as e:
        logger.error(f"OrchestratorAgent Fehler: {e}")
        return {
            "original": text,
            "variant": None,
            "domain": "general",
            "is_valid": False,
            "tool_calls": [],
            "attempts": 0,
            "success": False,
            "error": str(e),
        }

    # --- Output parsen ---
    raw_output: str = result.get("output", "")
    intermediate_steps: list = result.get("intermediate_steps", [])

    tool_calls = _parse_tool_calls(intermediate_steps)
    attempts = sum(1 for c in tool_calls if c["tool"] == "rewrite_segment")

    # Finale Variante aus FINALE_VARIANTE:-Marker extrahieren
    variant = _extract_final_variant(raw_output)

    # Fallback: letzten rewrite_segment-Output verwenden
    if not variant:
        for call_action, call_obs in reversed(intermediate_steps):
            if getattr(call_action, "tool", "") == "rewrite_segment":
                variant = str(call_obs).strip()
                if variant.startswith("{") and "error" in variant:
                    variant = None
                else:
                    break

    # Domain aus letztem classify_segment-Ergebnis lesen
    domain = domain_hint or "general"
    for call_action, call_obs in intermediate_steps:
        if getattr(call_action, "tool", "") == "classify_segment":
            try:
                cls_result = json.loads(str(call_obs))
                domain = cls_result.get("domain", domain)
            except (json.JSONDecodeError, TypeError):
                pass
            break

    # Validierungsstatus aus letztem validate_variant-Ergebnis
    is_valid = False
    for call_action, call_obs in reversed(intermediate_steps):
        if getattr(call_action, "tool", "") == "validate_variant":
            try:
                val_result = json.loads(str(call_obs))
                is_valid = val_result.get("is_valid", False)
            except (json.JSONDecodeError, TypeError):
                pass
            break

    logger.info(
        f"OrchestratorAgent abgeschlossen: "
        f"variant={'ja' if variant else 'nein'}, valid={is_valid}, "
        f"attempts={attempts}, tool_calls={len(tool_calls)}"
    )

    return {
        "original": text,
        "variant": variant,
        "domain": domain,
        "is_valid": is_valid,
        "tool_calls": tool_calls,
        "attempts": attempts,
        "success": variant is not None,
    }
