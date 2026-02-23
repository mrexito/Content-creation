"""
Edge Conditions für LangGraph Workflow
"""
from langgraph_prototype.state.workflow_state import WorkflowState
from common.logger import setup_logger

logger = setup_logger(__name__)


def should_retry_after_validation(state: WorkflowState) -> str:
    """
    Conditional Edge: Entscheidet ob nach Validation retry nötig
    
    Returns:
        'retry' wenn Segmente retry brauchen
        'assemble' wenn alle ok oder max retries erreicht
        'error' bei Fehler
    """
    if state['current_phase'] == 'error':
        return 'error'
    
    if state['current_phase'] != 'validation_complete':
        return 'error'
    
    # Prüfe ob Segmente Retry brauchen
    validation_stats = state.get('validation_stats', {})
    segments_needing_retry = validation_stats.get('segments_needing_retry', [])
    
    if segments_needing_retry:
        logger.info(f"🔄 {len(segments_needing_retry)} segments need retry")
        
        # Inkrementiere Retry-Counts
        if 'retry_counts' not in state:
            state['retry_counts'] = {}
        
        for seg_idx in segments_needing_retry:
            current = state['retry_counts'].get(seg_idx, 0)
            state['retry_counts'][seg_idx] = current + 1
        
        # Markiere als validation_failed für Rewriting-Node
        state['current_phase'] = 'validation_failed'
        
        return 'retry'
    else:
        logger.info("✓ All segments validated, proceeding to assembly")
        return 'assemble'