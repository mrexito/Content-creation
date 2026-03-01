"""
Edge Conditions für den Hybrid LangGraph-Graphen

Steuert die Retry-Schleife nach der Validation:
  → 'retry'    wenn Segmente noch Retry benötigen (und max_retries nicht erreicht)
  → 'done'     wenn alle Segmente ausreichend valide Varianten haben
  → 'error'    bei Fehler im Workflow
"""
from common.logger import setup_logger
from hybrid_prototype.state.hybrid_state import HybridWorkflowState

logger = setup_logger(__name__)


def should_retry_or_proceed(state: HybridWorkflowState) -> str:
    """
    Conditional Edge nach Validation Node.

    Returns:
        'retry'  → zurück zu Rewriting Node (Retry-Loop)
        'done'   → weiter (Postprocessing übernimmt)
        'error'  → Workflow abbrechen
    """
    if state.get("current_phase") == "error":
        logger.warning("  Edge: Fehler erkannt → 'error'")
        return "error"

    if state.get("current_phase") != "validation_complete":
        logger.warning("  Edge: Unerwarteter Phase-Zustand → 'error'")
        return "error"

    validation_stats = state.get("validation_stats") or {}
    segments_needing_retry = validation_stats.get("segments_needing_retry", [])

    if segments_needing_retry:
        # Erhöhe Retry-Counts für die betroffenen Segmente
        retry_counts = state.get("retry_counts") or {}
        for seg_idx in segments_needing_retry:
            retry_counts[seg_idx] = retry_counts.get(seg_idx, 0) + 1
        state["retry_counts"] = retry_counts

        # Setze Phase für Rewriting-Node zurück
        state["current_phase"] = "validation_failed"

        logger.info(
            f"  Edge: {len(segments_needing_retry)} Segmente benötigen Retry → 'retry'"
        )
        return "retry"

    logger.info("  Edge: Alle Segmente validiert → 'done'")
    return "done"
