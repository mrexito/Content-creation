"""
HybridWorkflowState: Verbindet LangChain Preprocessing mit LangGraph StateGraph

Der State wird nach dem Preprocessing durch LangChain befüllt und dann
durch den LangGraph-Graphen weitergereicht. Nach dem Graph-Durchlauf
wird er an das LangChain Postprocessing übergeben.
"""
from typing import TypedDict, List, Dict, Any, Optional


class HybridWorkflowState(TypedDict):
    """
    Zentraler State für den Hybrid-Workflow.

    Phase 1 (LangChain Preprocessing) → befüllt: raw_text, segments, classified_segments
    Phase 2 (LangGraph)               → befüllt: segments_with_variants, validation_stats
    Phase 3 (LangChain Postprocessing)→ befüllt: final_document
    """

    # ── Input ─────────────────────────────────────────────────────────────────
    pdf_path: str
    domain: Optional[str]          # 'math', 'languages', 'economics', None (→ auto)
    num_variants: int
    max_retries: int

    # ── Phase 1: LangChain Preprocessing ──────────────────────────────────────
    raw_text: Optional[str]
    ocr_metadata: Optional[Dict[str, Any]]
    segments: Optional[List[Dict[str, Any]]]
    classified_segments: Optional[List[Dict[str, Any]]]

    # ── Phase 2: LangGraph Rewriting + Validation ─────────────────────────────
    segments_with_variants: Optional[List[Dict[str, Any]]]
    retry_counts: Optional[Dict[int, int]]      # segment_idx → retry_count
    validation_stats: Optional[Dict[str, Any]]

    # ── Phase 3: LangChain Postprocessing ─────────────────────────────────────
    final_document: Optional[Dict[str, Any]]

    # ── Control & Metadata ────────────────────────────────────────────────────
    current_phase: str   # 'initialized' | 'preprocessing_complete' | 'rewriting' |
                         # 'validation_complete' | 'postprocessing_complete' | 'error'
    errors: List[str]
    total_processing_time: float


def create_initial_state(
    pdf_path: str,
    domain: Optional[str] = None,
    num_variants: int = 3,
    max_retries: int = 2,
) -> HybridWorkflowState:
    """
    Erstellt den initialen State für einen Hybrid-Workflow-Durchlauf.

    Args:
        pdf_path:     Pfad zur Eingabe-PDF
        domain:       Domäne ('math', 'languages', 'economics') oder None für Auto-Detect
        num_variants: Gewünschte Anzahl Varianten pro Segment
        max_retries:  Maximale Retry-Iterationen im LangGraph-Loop

    Returns:
        Frisch initialisierter HybridWorkflowState
    """
    return HybridWorkflowState(
        pdf_path=pdf_path,
        domain=domain,
        num_variants=num_variants,
        max_retries=max_retries,
        raw_text=None,
        ocr_metadata=None,
        segments=None,
        classified_segments=None,
        segments_with_variants=None,
        retry_counts={},
        validation_stats=None,
        final_document=None,
        current_phase="initialized",
        errors=[],
        total_processing_time=0.0,
    )
