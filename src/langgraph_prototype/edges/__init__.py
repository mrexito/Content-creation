"""
Edge Conditions für LangGraph Workflow

WICHTIG: Edge-Funktionen in LangGraph persistieren keine State-Mutationen.
Diese Funktion ist daher rein lesend (pure function) — alle State-Updates
(retry_counts, current_phase) werden ausschliesslich in validation_node.py vorgenommen.
"""
from langgraph_prototype.state.workflow_state import WorkflowState
from common.logger import setup_logger

logger = setup_logger(__name__)


def should_retry_after_validation(state: WorkflowState) -> str:
    """
    Conditional Edge: Liest current_phase und entscheidet über Routing.

    State-Mutationen (retry_counts, current_phase) werden NICHT hier,
    sondern in validation_node.py vorgenommen.

    Returns:
        'retry'    – validation_node hat 'validation_failed' gesetzt
        'assemble' – validation_node hat 'validation_complete' gesetzt
        'error'    – unerwarteter Phase-Status oder Fehler
    """
    phase = state.get('current_phase', '')

    if phase == 'error':
        return 'error'

    if phase == 'validation_failed':
        n = len(state.get('validation_stats', {}).get('segments_needing_retry', []))
        logger.info(f"[RETRY] {n} Segment(e) benötigen Retry → zurück zu Rewriting")
        return 'retry'

    if phase == 'validation_complete':
        logger.info("[OK] Alle Segmente validiert → weiter zu Assembly")
        return 'assemble'

    logger.error(f"Unbekannte Phase nach Validation: '{phase}'")
    return 'error'