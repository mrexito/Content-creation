"""
Variante B: Multi-Agent Pipeline
Drei spezialisierte Einzelagenten hintereinander — je ein Tool pro Agent.

THESIS-HINWEIS (methodisch relevant):
  Ein Agent mit nur einem Tool kann keine echte autonome Entscheidung
  treffen: Er ruft immer dasselbe Tool aus. Diese Variante degeneriert
  strukturell zur sequenziellen Pipeline — identisch zu langchain_prototype.
  Der Vergleich mit Variante A zeigt empirisch: Der Mehrwert des
  Agenten-Patterns entsteht erst durch die Wahlmöglichkeit zwischen
  mehreren Tools (Autonomie, Retry-Logik, Beobachtung von Ergebnissen).

Architektur:
  ClassifierAgent → RewriterAgent → ValidatorAgent

  Kein übergeordneter Koordinator → bei invalider Variante kein Retry.
  Diese Einschränkung ist bewusst und dokumentiert den Unterschied zu
  Variante A (Orchestrierungsagent) und LangGraph (Retry-StateGraph).

LangChain-Komponenten:
  - 3x create_tool_calling_agent
  - 3x AgentExecutor
  - MessagesPlaceholder (Scratchpad pro Agent)
"""
import json
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
# Agent-Factories
# ---------------------------------------------------------------------------

def _create_classifier_agent() -> AgentExecutor:
    """
    Klassifizierungs-Agent mit genau einem Tool: classify_segment.

    Thesis-Anmerkung: Ein Agent mit einem Tool ist strukturell eine
    deterministische Funktion. Kein echtes Reasoning nötig.
    """
    llm = get_lcel_llm(temperature=0.1)
    tools = [classify_segment]
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Du bist ein Klassifizierungs-Spezialist für Bildungsmaterialien. "
            "Klassifiziere das gegebene Segment mit dem classify_segment-Tool. "
            "Rufe das Tool genau einmal auf und gib das Ergebnis unverändert aus.",
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent, tools=tools,
        max_iterations=2, verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


def _create_rewriter_agent() -> AgentExecutor:
    """
    Rewriting-Agent mit genau einem Tool: rewrite_segment.

    Erhält als Input: den Originaltext + die ermittelte Domain.
    Kein Retry — ruft rewrite_segment genau einmal auf.
    """
    llm = get_lcel_llm(temperature=0.9)
    tools = [rewrite_segment]
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Du bist ein Rewriting-Spezialist für Bildungsmaterialien. "
            "Dein Auftrag: Generiere eine Variante des gegebenen Segments "
            "mit rewrite_segment. Verwende die angegebene Domain. "
            "Für Mathematik: Ändere Zahlenwerte um mindestens 30%. "
            "Für Sprachen: Behalte die Bedeutung bei. "
            "Rufe das Tool genau einmal auf.",
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent, tools=tools,
        max_iterations=2, verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


def _create_validator_agent() -> AgentExecutor:
    """
    Validierungs-Agent mit genau einem Tool: validate_variant.

    Kein Retry-Koordinator vorhanden — gibt Validierungsergebnis zurück
    ohne erneutes Rewriting anzustossen.
    """
    llm = get_lcel_llm(temperature=0.1)
    tools = [validate_variant]
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Du bist ein Validierungs-Spezialist. "
            "Validiere die gegebene Variante mit validate_variant. "
            "Rufe das Tool genau einmal auf und gib das Ergebnis aus.",
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent, tools=tools,
        max_iterations=2, verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _extract_tool_output(intermediate_steps: list, tool_name: str) -> Optional[str]:
    """Gibt den Output des ersten Aufrufs von tool_name zurück."""
    for action, observation in intermediate_steps:
        if getattr(action, "tool", "") == tool_name:
            return str(observation)
    return None


def _build_tool_calls(steps_per_agent: Dict[str, list]) -> List[Dict]:
    """Kompakte Tool-Call-Sequenz aus allen drei Agenten für Thesis-Auswertung."""
    calls = []
    for agent_name, steps in steps_per_agent.items():
        for action, observation in steps:
            tool_name = getattr(action, "tool", str(action))
            tool_input = getattr(action, "tool_input", {})
            input_len = 0
            if isinstance(tool_input, dict):
                for v in tool_input.values():
                    if isinstance(v, str):
                        input_len = len(v)
                        break
            calls.append({
                "agent": agent_name,
                "tool": tool_name,
                "input_len": input_len,
                "output_preview": str(observation)[:80],
            })
    return calls


# ---------------------------------------------------------------------------
# Haupt-Ausführungsfunktion
# ---------------------------------------------------------------------------

def run_multi_agent_pipeline(
    segment: Dict,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    Führt die drei Agenten sequenziell für ein Segment aus.

    THESIS-HINWEIS:
    max_retries wird aus Kompatibilitätsgründen entgegengenommen,
    aber nicht genutzt — kein Retry-Koordinator vorhanden.
    Bei invalider Validierung wird das Ergebnis trotzdem zurückgegeben.
    Das ist die bewusste Einschränkung dieser Variante im Vergleich zu
    Variante A (Orchestrierungsagent) und LangGraph.

    Args:
        segment:     Dict mit 'text'.
        max_retries: Ignoriert (dokumentiert in ARCHITECTURE.md).

    Returns: Gleiches Format wie run_orchestrator() für direkten Vergleich.
    """
    text = segment.get("text", "")
    logger.info(f"MultiAgentPipeline: starte für Segment ({len(text)} Zeichen)")

    steps_per_agent: Dict[str, list] = {}
    domain = "general"
    variant = None
    is_valid = False
    issues = []
    validation_results = {}

    # ------------------------------------------------------------------
    # Schritt 1: Classifier-Agent
    # ------------------------------------------------------------------
    try:
        classifier = _create_classifier_agent()
        cls_result = classifier.invoke({"input": text})
        steps_per_agent["classifier"] = cls_result.get("intermediate_steps", [])

        cls_output = _extract_tool_output(
            steps_per_agent["classifier"], "classify_segment"
        )
        if cls_output:
            try:
                cls_data = json.loads(cls_output)
                domain = cls_data.get("domain", "general")
                logger.info(f"MultiAgent Classifier → domain={domain}")
            except json.JSONDecodeError:
                logger.warning("Classifier-Output kein valides JSON, nutze 'general'")

    except Exception as e:
        logger.exception(f"Classifier-Agent Fehler: {e}")
        steps_per_agent["classifier"] = []

    # ------------------------------------------------------------------
    # Schritt 2: Rewriter-Agent
    # ------------------------------------------------------------------
    try:
        rewriter = _create_rewriter_agent()
        rewrite_input = (
            f"Text: {text}\n"
            f"Domain: {domain}\n"
            f"Erstelle eine Variante mit rewrite_segment(text=..., domain='{domain}')."
        )
        rw_result = rewriter.invoke({"input": rewrite_input})
        steps_per_agent["rewriter"] = rw_result.get("intermediate_steps", [])

        variant_raw = _extract_tool_output(
            steps_per_agent["rewriter"], "rewrite_segment"
        )
        if variant_raw and not (
            variant_raw.strip().startswith("{") and "error" in variant_raw
        ):
            variant = variant_raw.strip()
            logger.info(f"MultiAgent Rewriter → {len(variant)} Zeichen")
        else:
            logger.warning(f"Rewriter: kein valider Output ({variant_raw!r})")

    except Exception as e:
        logger.exception(f"Rewriter-Agent Fehler: {e}")
        steps_per_agent["rewriter"] = []

    # ------------------------------------------------------------------
    # Schritt 3: Validator-Agent
    # ------------------------------------------------------------------
    if variant:
        try:
            validator = _create_validator_agent()
            val_input = (
                f"Original: {text}\n"
                f"Variante: {variant}\n"
                f"Domain: {domain}\n"
                f"Validiere mit validate_variant("
                f"original=..., variant=..., domain='{domain}')."
            )
            val_result = validator.invoke({"input": val_input})
            steps_per_agent["validator"] = val_result.get("intermediate_steps", [])

            val_output = _extract_tool_output(
                steps_per_agent["validator"], "validate_variant"
            )
            if val_output:
                try:
                    val_data = json.loads(val_output)
                    is_valid = val_data.get("is_valid", False)
                    issues = val_data.get("issues", [])
                    validation_results = val_data.get("details", {})
                    logger.info(
                        f"MultiAgent Validator → valid={is_valid}, "
                        f"issues={issues}"
                    )
                except json.JSONDecodeError:
                    logger.warning("Validator-Output kein valides JSON")

        except Exception as e:
            logger.exception(f"Validator-Agent Fehler: {e}")
            steps_per_agent["validator"] = []
    else:
        steps_per_agent["validator"] = []
        logger.warning("MultiAgent: kein Variant → Validator übersprungen")

    tool_calls = _build_tool_calls(steps_per_agent)

    logger.info(
        f"MultiAgentPipeline abgeschlossen: "
        f"variant={'ja' if variant else 'nein'}, valid={is_valid}, "
        f"tool_calls={len(tool_calls)}"
    )

    return {
        "original": text,
        "variant": variant,
        "domain": domain,
        "is_valid": is_valid,
        "tool_calls": tool_calls,
        "attempts": 1,  # Immer genau 1 Rewriting-Versuch (kein Retry)
        "success": variant is not None,
        "issues": issues,
        "validation_results": validation_results,
    }
