"""
Hybrid Rewriting Node – Phase 2a des LangGraph-Graphen

Liest classified_segments aus dem HybridWorkflowState und generiert
domänen-spezifische Varianten mit Diversity-Mechanismus.
Unterstützt Retry-Schleifen: beim erneuten Durchlauf werden nur
Segmente neu geschrieben, die bei der Validation gescheitert sind.
"""
import time
from typing import List

from common.constants import DOMAIN_LANGUAGES, NON_REWRITABLE_TYPES
from common.utils import calculate_similarity
from common.llm_handler import get_llm_handler
from common.logger import setup_logger
from hybrid_prototype.state.hybrid_state import HybridWorkflowState
from langchain_prototype.prompts.rewriting_prompts import (
    REWRITING_MATH_SYSTEM_PROMPT,
    REWRITING_LANGUAGES_SYSTEM_PROMPT,
    REWRITING_ECONOMICS_SYSTEM_PROMPT,
    REWRITING_GENERAL_SYSTEM_PROMPT,
    REWRITING_USER_PROMPT_TEMPLATE,
)

logger = setup_logger(__name__)

DOMAIN_PROMPTS = {
    "mathematics": REWRITING_MATH_SYSTEM_PROMPT,
    "languages": REWRITING_LANGUAGES_SYSTEM_PROMPT,
    "economics": REWRITING_ECONOMICS_SYSTEM_PROMPT,
    "general": REWRITING_GENERAL_SYSTEM_PROMPT,
}

MIN_SIMILARITY_THRESHOLD = 0.72
MAX_ATTEMPTS_PER_VARIANT = 3


def _too_similar(candidate: str, existing: List[str]) -> bool:
    return any(calculate_similarity(candidate, ex) >= MIN_SIMILARITY_THRESHOLD for ex in existing)


def _adaptive_temperature(base: float, attempt: int, domain: str = "") -> float:
    """
    Berechnet die Temperature domain-spezifisch.

    Temperature-Paradox: Für die Languages-Domain darf die Temperature
    bei Retries NICHT erhöht werden, da BERTScore semantische Nähe zum
    Original erfordert — höhere Temperature → grössere Abweichung →
    niedrigerer BERTScore → mehr Retries (Teufelskreis).
    """
    if domain == DOMAIN_LANGUAGES:
        return 0.7  # Konstant niedrig für BERT-Validierung
    return min(base + attempt * 0.1, 1.0)


def hybrid_rewriting_node(state: HybridWorkflowState) -> HybridWorkflowState:
    """
    LangGraph Node: Rewriting

    Input (State):
        - classified_segments  (aus LangChain Preprocessing)
        - segments_with_variants (optional, bei Retry-Iteration befüllt)
        - retry_counts

    Output (State Updates):
        - segments_with_variants
        - current_phase → 'rewriting_complete'
    """
    logger.info("🔗 [LangGraph] Hybrid Rewriting Node")

    start_time = time.time()

    try:
        classified_segments = state.get("classified_segments") or []
        existing_variants = state.get("segments_with_variants") or []
        retry_counts = state.get("retry_counts") or {}
        num_variants = state.get("num_variants", 3)

        llm = get_llm_handler()

        # Bestimme welche Segmente (neu) zu schreiben sind
        # Beim ersten Durchlauf → alle; beim Retry → nur gescheiterte
        is_retry = bool(existing_variants)
        segments_needing_rewrite: List[int] = []

        if is_retry:
            validation_stats = state.get("validation_stats") or {}
            segments_needing_rewrite = validation_stats.get("segments_needing_retry", [])
            logger.info(
                f"  Retry-Iteration: {len(segments_needing_rewrite)} Segmente "
                f"werden neu geschrieben"
            )
        else:
            segments_needing_rewrite = list(range(len(classified_segments)))
            existing_variants = []

        # Index existierender Varianten für schnellen Zugriff
        existing_map = {sv["segment_idx"]: sv for sv in existing_variants}

        result_segments = list(existing_variants)  # Kopie, wird ggf. aktualisiert

        for idx in segments_needing_rewrite:
            if idx >= len(classified_segments):
                continue

            classified = classified_segments[idx]
            segment = classified.get("segment", {})
            classification = classified.get("classification", {})
            original_text = segment.get("text", "")
            domain = classification.get("domain", "general")
            retry_count = retry_counts.get(idx, 0)

            # THESIS: Segmentfilter — Titel/Musterlösungen überspringen
            segment_type = segment.get("type", "unknown")
            if segment_type in NON_REWRITABLE_TYPES:
                logger.info(f"  Überspringe Segment {idx+1} (type='{segment_type}', nicht rewritable)")
                skipped_entry = {
                    "segment_idx": idx,
                    "segment": segment,
                    "classification": classification,
                    "variants": [],
                    "skipped": True,
                    "skip_reason": f"type={segment_type} is not rewritable",
                }
                replaced = False
                for i, sv in enumerate(result_segments):
                    if sv["segment_idx"] == idx:
                        result_segments[i] = skipped_entry
                        replaced = True
                        break
                if not replaced:
                    result_segments.append(skipped_entry)
                continue

            system_prompt = DOMAIN_PROMPTS.get(domain, REWRITING_GENERAL_SYSTEM_PROMPT)

            logger.debug(
                f"  Segment {idx + 1}/{len(classified_segments)} "
                f"[{domain}] Retry={retry_count}"
            )

            # Bestehende Varianten dieses Segments als Kontext übergeben
            prev_entry = existing_map.get(idx)
            prev_texts: List[str] = []
            if prev_entry:
                prev_texts = [v.get("text", "") for v in prev_entry.get("variants", [])]

            variants = []
            variant_texts: List[str] = list(prev_texts)  # für Diversitäts-Check

            for v_idx in range(num_variants):
                generated = False
                for attempt in range(MAX_ATTEMPTS_PER_VARIANT):
                    temperature = _adaptive_temperature(0.8, attempt + retry_count, domain)

                    prev_context = ""
                    if variant_texts:
                        samples = variant_texts[-3:]
                        prev_context = (
                            "\n\nBereits generierte Varianten (bitte deutlich verschieden):\n"
                            + "\n".join(f"- {t}" for t in samples)
                        )

                    user_prompt = (
                        REWRITING_USER_PROMPT_TEMPLATE.format(
                            text=original_text,
                            num_variants=1,
                        )
                        + prev_context
                    )

                    result = llm.generate(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                    )

                    if not result.get("success"):
                        logger.warning(f"    LLM-Fehler bei Variante {v_idx + 1}, Versuch {attempt + 1}")
                        continue

                    variant_text = result.get("text", "").strip()
                    if not variant_text or variant_text == original_text:
                        continue

                    if _too_similar(variant_text, [original_text] + variant_texts):
                        logger.debug(f"    Variante {v_idx + 1} zu ähnlich, Versuch {attempt + 1}")
                        continue

                    variant_texts.append(variant_text)
                    variants.append(
                        {
                            "variant_id": v_idx + 1,
                            "text": variant_text,
                            "attempts": attempt + 1,
                            "temperature_used": temperature,
                            "retry_iteration": retry_count,
                        }
                    )
                    generated = True
                    break

                if not generated:
                    logger.warning(f"    Konnte Variante {v_idx + 1} nach {MAX_ATTEMPTS_PER_VARIANT} Versuchen nicht generieren")

            new_entry = {
                "segment_idx": idx,
                "segment": segment,
                "classification": classification,
                "variants": variants,
            }

            # Ersetze oder füge hinzu
            replaced = False
            for i, sv in enumerate(result_segments):
                if sv["segment_idx"] == idx:
                    result_segments[i] = new_entry
                    replaced = True
                    break
            if not replaced:
                result_segments.append(new_entry)

        # Sortiere nach segment_idx für konsistente Reihenfolge
        result_segments.sort(key=lambda s: s["segment_idx"])

        state["segments_with_variants"] = result_segments
        state["current_phase"] = "rewriting_complete"
        state["total_processing_time"] += time.time() - start_time

        total_generated = sum(len(s["variants"]) for s in result_segments)
        logger.info(f"  ✓ Rewriting: {total_generated} Varianten generiert")

        return state

    except Exception as e:
        error_msg = f"Rewriting-Fehler: {str(e)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        state["current_phase"] = "error"
        return state
