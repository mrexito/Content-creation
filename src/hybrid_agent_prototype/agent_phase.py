"""
Hybrid Agent Phase – Phase 2 des Hybrid-Agent-Ansatzes

Ersetzt run_hybrid_graph() aus hybrid_prototype.
Verarbeitet classified_segments mit einem LangChain AgentExecutor
statt einem LangGraph StateGraph.

Ermöglicht isolierten Vergleich: LangGraph vs. Agent in Phase 2,
bei identischem Pre- und Postprocessing (Phase 1 und 3).
"""
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common.constants import NON_REWRITABLE_TYPES
from common.logger import setup_logger
from hybrid_prototype.state.hybrid_state import HybridWorkflowState
from langchain_prototype.lcel_llm import get_lcel_llm
from langchain_agent_prototype.tools.rewriting_tools import (
    rewrite_segment,
    validate_variant,
)

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# System-Prompt Template
# ---------------------------------------------------------------------------
# {max_retries} wird via .format() VOR ChatPromptTemplate eingesetzt.

_SYSTEM_PROMPT_TEMPLATE = """Du bist ein Rewriting-Agent für Bildungsmaterialien.
Du erhältst ein Textsegment mit bekannter Domain.

Dein Auftrag: Erstelle eine valide Variante.

Vorgehensweise:
1. Rufe rewrite_segment(text, domain) auf
2. Rufe validate_variant(original, variant, domain) auf
3. Wenn is_valid=false: Rufe rewrite_segment erneut auf mit
   hint=<Problembeschreibung aus den issues>
4. Maximal {max_retries} Rewriting-Versuche
5. Antworte am Ende mit:
   RESULT: <finale variante>
   VALID: true|false
"""


# ---------------------------------------------------------------------------
# Interne Hilfsfunktionen
# ---------------------------------------------------------------------------

def _create_segment_agent(max_retries: int) -> AgentExecutor:
    """Erstellt einen AgentExecutor für ein einzelnes Segment."""
    llm = get_lcel_llm(temperature=0.7)
    tools = [rewrite_segment, validate_variant]

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
        max_iterations=max_retries * 2 + 2,  # N*(rewrite+validate)
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    return executor


def _parse_tool_calls(intermediate_steps: List) -> List[Dict]:
    """Extrahiert kompakte Tool-Call-Sequenz für Thesis-Analyse."""
    calls = []
    for action, observation in intermediate_steps:
        tool_name = getattr(action, "tool", str(action))
        tool_input = getattr(action, "tool_input", {})

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


def _extract_result(output: str) -> Tuple[Optional[str], Optional[bool]]:
    """
    Extrahiert RESULT: <text> und VALID: true|false aus dem Agent-Output.
    Gibt (variant_text, is_valid) zurück.
    """
    variant = None
    is_valid = None

    result_match = re.search(r"RESULT:\s*(.+?)(?:\nVALID:|$)", output, re.DOTALL)
    if result_match:
        candidate = result_match.group(1).strip()
        if candidate:
            variant = candidate

    valid_match = re.search(r"VALID:\s*(true|false)", output, re.IGNORECASE)
    if valid_match:
        is_valid = valid_match.group(1).lower() == "true"

    return variant, is_valid


def _detect_hallucinated_calls(output: str, intermediate_steps: List) -> int:
    """
    Schätzt Anzahl halluzinierter Tool-Calls für Thesis-Analyse.

    Halluziniert = Tool-Name im Output-Text öfter erwähnt als
    tatsächlich in intermediate_steps vorhanden.
    """
    tool_names = ["rewrite_segment", "validate_variant"]
    actual_tools = [getattr(a, "tool", "") for a, _ in intermediate_steps]

    hallucinated = 0
    for tool in tool_names:
        mentions = len(re.findall(rf"\b{tool}\b", output))
        actual = actual_tools.count(tool)
        if mentions > actual:
            hallucinated += mentions - actual
    return hallucinated


# ---------------------------------------------------------------------------
# Haupt-Funktion
# ---------------------------------------------------------------------------

def run_hybrid_agent(
    state: HybridWorkflowState,
    max_retries: int = 3,
    progress_callback=None,
) -> HybridWorkflowState:
    """
    Phase 2 des Hybrid-Agent-Prototyps.

    Ersetzt run_hybrid_graph(). Verarbeitet jeden classified_segment mit
    einem eigenen LangChain AgentExecutor pro Segment.

    Befüllt nach Abschluss:
        state['segments_with_variants']  — Format kompatibel mit Postprocessing
        state['validation_stats']        — total_valid, total_invalid, validation_rate
        state['retry_counts']            — {segment_idx: retry_count}
        state['agent_stats']             — Thesis-Metriken
        state['current_phase'] = 'agent_complete'

    Args:
        state:             HybridWorkflowState nach abgeschlossenem Preprocessing
        max_retries:       Max. Rewriting-Versuche pro Segment
        progress_callback: Optionaler Callable[[str], None] für Fortschritt
    """
    logger.info("=" * 60)
    logger.info("HYBRID AGENT (Rewriting + Validation) – Start")
    logger.info("=" * 60)

    start_time = time.time()

    try:
        classified_segments = state.get("classified_segments") or []
        num_variants = state.get("num_variants", 1)

        segments_with_variants: List[Dict] = []
        retry_counts: Dict[int, int] = {}

        # Thesis-Tracking
        tool_calls_per_segment: List[int] = []
        total_tool_calls = 0
        total_retries = 0
        total_hallucinated = 0
        total_valid = 0
        total_invalid = 0

        for idx, classified in enumerate(classified_segments):
            segment = classified.get("segment", {})
            classification = classified.get("classification", {})
            original_text = segment.get("text", "")
            domain = classification.get("domain", "general")
            segment_type = segment.get("type", "unknown")

            # Überspringe nicht-rewritable Segmente
            if segment_type in NON_REWRITABLE_TYPES:
                logger.info(
                    f"  Überspringe Segment {idx + 1} "
                    f"(type='{segment_type}', nicht rewritable)"
                )
                segments_with_variants.append({
                    "segment_idx": idx,
                    "segment": segment,
                    "classification": classification,
                    "variants": [],
                    "skipped": True,
                    "skip_reason": f"type={segment_type} is not rewritable",
                })
                tool_calls_per_segment.append(0)
                continue

            logger.info(
                f"  Segment {idx + 1}/{len(classified_segments)} "
                f"[{domain}] – Agent startet"
            )

            all_variants = []
            seg_tool_calls = 0

            for v_idx in range(num_variants):
                segment_input = original_text
                if domain:
                    segment_input += f"\n\n[Domain: {domain}]"

                try:
                    executor = _create_segment_agent(max_retries=max_retries)
                    result = executor.invoke({"input": segment_input})
                except Exception as agent_err:
                    logger.error(f"  Agent-Fehler für Segment {idx + 1}: {agent_err}")
                    total_invalid += 1
                    continue

                raw_output: str = result.get("output", "")
                intermediate_steps: list = result.get("intermediate_steps", [])
                tool_calls = _parse_tool_calls(intermediate_steps)
                seg_tool_calls += len(tool_calls)

                # Retries = rewrite_segment-Aufrufe - 1 (erster ist kein Retry)
                rewrite_calls = sum(
                    1 for c in tool_calls if c["tool"] == "rewrite_segment"
                )
                retries = max(0, rewrite_calls - 1)
                retry_counts[idx] = retry_counts.get(idx, 0) + retries
                total_retries += retries

                # Halluzinations-Erkennung für Thesis
                hallucinated = _detect_hallucinated_calls(raw_output, intermediate_steps)
                total_hallucinated += hallucinated

                # Variante aus RESULT:-Marker extrahieren
                variant_text, is_valid_marker = _extract_result(raw_output)

                # Fallback: letzten rewrite_segment-Output verwenden
                if not variant_text:
                    for call_action, call_obs in reversed(intermediate_steps):
                        if getattr(call_action, "tool", "") == "rewrite_segment":
                            candidate = str(call_obs).strip()
                            if not (candidate.startswith("{") and "error" in candidate):
                                variant_text = candidate
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

                # RESULT/VALID-Marker aus Output als Tiebreaker
                if is_valid_marker is not None:
                    is_valid = is_valid_marker

                if is_valid:
                    total_valid += 1
                else:
                    total_invalid += 1

                if variant_text:
                    all_variants.append({
                        "variant_id": v_idx + 1,
                        "text": variant_text,
                        "attempts": rewrite_calls,
                        "validation": {
                            "is_valid": is_valid,
                            "issues": [],
                            "score": 1.0 if is_valid else 0.5,
                        },
                        "tool_calls": tool_calls,
                        "hallucinated_calls": hallucinated,
                    })

            total_tool_calls += seg_tool_calls
            tool_calls_per_segment.append(seg_tool_calls)

            segments_with_variants.append({
                "segment_idx": idx,
                "segment": segment,
                "classification": classification,
                "variants": all_variants,
            })

            if progress_callback:
                progress_callback("rewriting")

        # Sortiere nach segment_idx für konsistente Reihenfolge
        segments_with_variants.sort(key=lambda s: s["segment_idx"])

        total_processed = total_valid + total_invalid
        validation_rate = total_valid / max(total_processed, 1)
        elapsed = time.time() - start_time

        state["segments_with_variants"] = segments_with_variants
        state["retry_counts"] = retry_counts
        state["validation_stats"] = {
            "total_valid": total_valid,
            "total_invalid": total_invalid,
            "validation_rate": validation_rate,
        }
        state["agent_stats"] = {
            "total_tool_calls": total_tool_calls,
            "tool_calls_per_segment": tool_calls_per_segment,
            "total_retries": total_retries,
            "hallucinated_calls": total_hallucinated,
        }
        state["current_phase"] = "agent_complete"
        state["total_processing_time"] = (
            state.get("total_processing_time", 0.0) + elapsed
        )

        logger.info(
            f"✅ Hybrid Agent abgeschlossen – "
            f"{total_valid} valide, {total_invalid} invalide, "
            f"Rate: {validation_rate * 100:.1f}%, "
            f"Tool-Calls: {total_tool_calls}, Retries: {total_retries}"
        )

        if progress_callback:
            progress_callback("validation")

        return state

    except Exception as e:
        error_msg = f"Hybrid Agent Fehler: {str(e)}"
        logger.error(error_msg)
        errors = list(state.get("errors") or [])
        errors.append(error_msg)
        state["errors"] = errors
        state["current_phase"] = "error"
        return state
