"""
Hybrid Validation Node – Phase 2b des LangGraph-Graphen

Validiert die generierten Varianten domain-spezifisch:
  - Mathematik  → SymPy-Check (algebraische Korrektheit)
  - Sprachen    → BERTScore (semantische Ähnlichkeit)
  - Wirtschaft  → Konsistenz-Check (numerische Konsistenz)

Markiert Segmente mit zu wenigen validen Varianten für Retry-Schleifen.
"""
import time

from common.validators import (
    get_sympy_validator,
    get_bert_validator,
    get_consistency_validator,
)
from common.utils import check_placeholder_preservation
from common.logger import setup_logger
from hybrid_prototype.state.hybrid_state import HybridWorkflowState

try:
    from langchain_prototype.chains.solution_chain import get_solution_chain as _get_solution_chain
    _solution_chain = _get_solution_chain()
except Exception:
    _solution_chain = None

logger = setup_logger(__name__)

# Mindestanzahl valider Varianten pro Segment bevor Retry
MIN_VALID_VARIANTS = 1


def hybrid_validation_node(state: HybridWorkflowState) -> HybridWorkflowState:
    """
    LangGraph Node: Validation mit Retry-Tracking

    Input (State):
        - segments_with_variants
        - domain (für Validator-Auswahl)

    Output (State Updates):
        - segments_with_variants (mit validation-Feldern)
        - validation_stats (inkl. segments_needing_retry)
        - current_phase → 'validation_complete'
    """
    logger.info("🔗 [LangGraph] Hybrid Validation Node")

    start_time = time.time()

    try:
        segments_with_variants = state.get("segments_with_variants") or []

        if not segments_with_variants:
            error_msg = "Keine Varianten zur Validierung vorhanden"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["current_phase"] = "error"
            return state

        sympy_validator = get_sympy_validator()
        bert_validator = get_bert_validator()
        consistency_validator = get_consistency_validator()

        total_valid = 0
        total_invalid = 0
        segments_needing_retry: list = []

        for seg_data in segments_with_variants:
            segment = seg_data.get("segment", {})
            classification = seg_data.get("classification", {})
            variants = seg_data.get("variants", [])
            seg_idx = seg_data.get("segment_idx", 0)

            original_text = segment.get("text", "")
            domain = classification.get("domain", "general")

            seg_valid_count = 0

            for variant in variants:
                variant_text = variant.get("text")

                if not variant_text:
                    variant["validation"] = {
                        "is_valid": False,
                        "issues": ["Leere Variante"],
                        "score": 0.0,
                    }
                    total_invalid += 1
                    continue

                issues = []
                score = 1.0
                placeholder_result = None

                # ── Domain-spezifische Validierung ───────────────────────────
                if domain == "mathematics":
                    math_result = sympy_validator.validate_text(variant_text)
                    text_issues = [
                        str(i.get("error", i)) for i in math_result.get("issues", [])
                    ]
                    if text_issues:
                        issues.extend(text_issues)
                        score = min(score, 0.5)

                elif domain == "languages":
                    bert_result = bert_validator.validate_paraphrase(
                        original=original_text,
                        paraphrased=variant_text,
                    )
                    if not bert_result.get("is_valid", True):
                        reason = bert_result.get("reason", "BERTScore zu niedrig")
                        issues.append(reason)
                        score = min(score, bert_result.get("score", 0.5))

                    # Placeholder-Check: Lücken dürfen nicht ausgefüllt werden
                    placeholder_result = check_placeholder_preservation(original_text, variant_text)
                    if not placeholder_result.get('skipped') and not placeholder_result['is_valid']:
                        issues.append(
                            f"Platzhalter nicht erhalten: "
                            f"{placeholder_result['variant_count']} von "
                            f"{placeholder_result['original_count']} Platzhaltern vorhanden "
                            f"(min. 80% erforderlich)"
                        )

                elif domain == "economics":
                    original_numbers = consistency_validator.extract_numbers(original_text)
                    econ_result = consistency_validator.check_number_consistency(
                        variant_text, original_numbers
                    )
                    if not econ_result.get("is_consistent", True):
                        missing = econ_result.get("missing_numbers", [])
                        issues.append(f"Fehlende Zahlen in Variante: {missing}")
                        score = min(score, 0.5)

                is_valid = len(issues) == 0
                variant["validation"] = {
                    "is_valid": is_valid,
                    "issues": issues,
                    "score": score,
                }
                if placeholder_result is not None:
                    variant["validation"]["placeholder"] = placeholder_result

                if is_valid:
                    total_valid += 1
                    seg_valid_count += 1
                    # Musterantwort für valide Variante generieren
                    if _solution_chain is not None:
                        try:
                            sol = _solution_chain.invoke({
                                'variant_text': variant_text,
                                'domain': domain,
                            })
                            variant['solution'] = sol.get('solution')
                        except Exception as _e:
                            logger.warning(f"Solution-Generierung fehlgeschlagen: {_e}")
                            variant['solution'] = None
                    else:
                        variant['solution'] = None
                else:
                    total_invalid += 1
                    variant['solution'] = None
                    logger.debug(
                        f"  Segment {seg_idx} Variante {variant.get('variant_id')}: "
                        f"ungültig – {issues}"
                    )

            # Segment für Retry vormerken wenn zu wenige valide Varianten
            max_retries = state.get("max_retries", 2)
            # Read retry_count BEFORE incrementing (edge function mutations don't persist)
            retry_count = (state.get("retry_counts") or {}).get(seg_idx, 0)

            if seg_valid_count < MIN_VALID_VARIANTS and retry_count < max_retries:
                segments_needing_retry.append(seg_idx)
                logger.info(
                    f"  Segment {seg_idx}: {seg_valid_count} valide Varianten "
                    f"→ Retry {retry_count + 1}/{max_retries}"
                )

        validation_rate = total_valid / max(total_valid + total_invalid, 1)

        # Increment retry_counts HERE (in node, not in edge function) so LangGraph persists it
        retry_counts = dict(state.get("retry_counts") or {})
        for seg_idx in segments_needing_retry:
            retry_counts[seg_idx] = retry_counts.get(seg_idx, 0) + 1
        state["retry_counts"] = retry_counts

        state["validation_stats"] = {
            "total_valid": total_valid,
            "total_invalid": total_invalid,
            "validation_rate": validation_rate,
            "segments_needing_retry": segments_needing_retry,
        }
        state["current_phase"] = "validation_complete"
        state["total_processing_time"] += time.time() - start_time

        logger.info(
            f"  ✓ Validation: {total_valid} valide, {total_invalid} ungültige Varianten "
            f"(Rate: {validation_rate * 100:.1f}%)"
        )
        if segments_needing_retry:
            logger.info(f"  ↩  {len(segments_needing_retry)} Segmente brauchen Retry")

        return state

    except Exception as e:
        error_msg = f"Validierungs-Fehler: {str(e)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        state["current_phase"] = "error"
        return state
