"""
Hybrid LangGraph StateGraph – Phase 2 des Hybrid-Ansatzes

Modelliert den Rewriting+Validation-Loop als gerichteten Graphen:

    rewrite ──→ validate ──→ [done]     → Postprocessing übernimmt
                    └──────→ [retry]    → zurück zu rewrite
                    └──────→ [error]    → Abbruch

Dieser Graph erhält einen vorbereiteten HybridWorkflowState aus der
LangChain-Preprocessing-Phase und gibt ihn nach Abschluss an die
LangChain-Postprocessing-Phase zurück.
"""
from langgraph.graph import StateGraph, END

from common.logger import setup_logger
from hybrid_prototype.state.hybrid_state import HybridWorkflowState
from hybrid_prototype.graph.rewriting_node import hybrid_rewriting_node
from hybrid_prototype.graph.validation_node import hybrid_validation_node
from hybrid_prototype.graph.edges import should_retry_or_proceed

logger = setup_logger(__name__)


def create_hybrid_graph():
    """
    Erstellt und kompiliert den LangGraph StateGraph für Phase 2.

    Returns:
        Kompilierter LangGraph (StateGraph.compile())
    """
    logger.info("Erstelle Hybrid LangGraph mit Retry-Loop...")

    workflow = StateGraph(HybridWorkflowState)

    # ── Nodes ─────────────────────────────────────────────────────────────────
    workflow.add_node("rewrite", hybrid_rewriting_node)
    workflow.add_node("validate", hybrid_validation_node)

    # ── Edges ─────────────────────────────────────────────────────────────────
    workflow.set_entry_point("rewrite")
    workflow.add_edge("rewrite", "validate")

    # ⭐ Conditional Edge: Retry-Loop
    workflow.add_conditional_edges(
        "validate",
        should_retry_or_proceed,
        {
            "retry": "rewrite",  # ← Schleife zurück zu Rewriting
            "done": END,         # ← Weiter zu LangChain Postprocessing
            "error": END,        # ← Bei Fehler abbrechen
        },
    )

    app = workflow.compile()

    logger.info("✓ Hybrid LangGraph erstellt (rewrite → validate → [retry|done|error])")
    return app


def run_hybrid_graph(state: HybridWorkflowState) -> HybridWorkflowState:
    """
    Führt den Hybrid-Graphen mit dem gegebenen State aus.

    Args:
        state: HybridWorkflowState nach abgeschlossenem Preprocessing

    Returns:
        Aktualisierter State mit segments_with_variants und validation_stats
    """
    app = create_hybrid_graph()
    logger.info("=" * 60)
    logger.info("HYBRID LANGGRAPH (Rewriting + Validation) – Start")
    logger.info("=" * 60)

    final_state = app.invoke(state)

    if final_state.get("current_phase") == "error":
        logger.error("LangGraph Phase mit Fehler beendet")
    else:
        stats = final_state.get("validation_stats") or {}
        logger.info(
            f"✅ LangGraph Phase abgeschlossen – "
            f"{stats.get('total_valid', 0)} valide Varianten, "
            f"Rate: {stats.get('validation_rate', 0) * 100:.1f}%"
        )

    return final_state
