"""
State-Schema für LangGraph Workflow
Definiert die Datenstruktur, die durch den Graph fließt
"""
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated


class WorkflowState(TypedDict):
    """
    Zentraler State für den gesamten Workflow
    
    Dieser State wird durch alle Nodes weitergereicht und
    kann von jedem Node gelesen und geschrieben werden.
    """
    
    # Input
    pdf_path: str
    domain: Optional[str]  # 'math', 'languages', 'economics', None
    
    # Phase 1: Parsing
    raw_text: Optional[str]
    ocr_metadata: Optional[Dict[str, Any]]
    
    # Phase 2: Segmentation
    segments: Optional[List[Dict[str, Any]]]
    
    # Phase 3: Classification & Rewriting
    classified_segments: Optional[List[Dict[str, Any]]]
    
    # Phase 4: Validation (mit Retry-Logik)
    segments_with_variants: Optional[List[Dict[str, Any]]]
    retry_counts: Optional[Dict[int, int]]  # segment_idx -> retry_count
    max_retries: int
    
    # Phase 5: Assembly
    final_document: Optional[Dict[str, Any]]
    
    # Metadata & Control
    current_phase: str  # 'parsing', 'segmentation', 'classification', etc.
    errors: List[str]
    total_processing_time: float
    
    # Config
    num_variants: int
    similarity_threshold: float


# Helper: Initialisiere leeren State
def create_initial_state(
    pdf_path: str,
    domain: str = None,
    num_variants: int = 2,
    max_retries: int = 3,
    similarity_threshold: float = 0.7
) -> WorkflowState:
    """
    Erstellt einen initialen State für den Workflow
    
    Args:
        pdf_path: Pfad zum Input-PDF
        domain: Optional domain hint
        num_variants: Anzahl Varianten pro Segment
        max_retries: Max Rewriting-Versuche bei Validation-Failures
        similarity_threshold: Threshold für Diversity-Check
    
    Returns:
        Initialisierter WorkflowState
    """
    return WorkflowState(
        # Input
        pdf_path=pdf_path,
        domain=domain,
        
        # Phases (alle None am Anfang)
        raw_text=None,
        ocr_metadata=None,
        segments=None,
        classified_segments=None,
        segments_with_variants=None,
        retry_counts={},
        max_retries=max_retries,
        final_document=None,
        
        # Metadata
        current_phase='initialized',
        errors=[],
        total_processing_time=0.0,
        
        # Config
        num_variants=num_variants,
        similarity_threshold=similarity_threshold
    )
# ... (bestehender Code bleibt) ...

def increment_retry_count(state: WorkflowState, segment_idx: int) -> WorkflowState:
    """
    Inkrementiert Retry-Count für ein Segment
    
    Args:
        state: Current state
        segment_idx: Index des Segments
    
    Returns:
        Updated state
    """
    if 'retry_counts' not in state or state['retry_counts'] is None:
        state['retry_counts'] = {}
    
    current_count = state['retry_counts'].get(segment_idx, 0)
    state['retry_counts'][segment_idx] = current_count + 1
    
    return state


def get_retry_count(state: WorkflowState, segment_idx: int) -> int:
    """
    Holt Retry-Count für ein Segment
    
    Args:
        state: Current state
        segment_idx: Index des Segments
    
    Returns:
        Anzahl Retries
    """
    if 'retry_counts' not in state or state['retry_counts'] is None:
        return 0
    
    return state['retry_counts'].get(segment_idx, 0)


def should_retry_segment(state: WorkflowState, segment_idx: int) -> bool:
    """
    Entscheidet ob Segment retry braucht
    
    Args:
        state: Current state
        segment_idx: Index des Segments
    
    Returns:
        True wenn retry nötig und erlaubt
    """
    retry_count = get_retry_count(state, segment_idx)
    max_retries = state.get('max_retries', 3)
    
    return retry_count < max_retries