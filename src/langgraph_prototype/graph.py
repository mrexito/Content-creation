"""
LangGraph Workflow Graph mit Retry-Loops
"""
from langgraph.graph import StateGraph, END

from langgraph_prototype.state.workflow_state import WorkflowState
from langgraph_prototype.nodes.parsing_node import parsing_node
from langgraph_prototype.nodes.segmentation_node import segmentation_node
from langgraph_prototype.nodes.classification_node import classification_node
from langgraph_prototype.nodes.rewriting_node import rewriting_node
from langgraph_prototype.nodes.validation_node import validation_node
from langgraph_prototype.nodes.assembly_node import assembly_node
from langgraph_prototype.edges import should_retry_after_validation

from common.logger import setup_logger

logger = setup_logger(__name__)


def create_workflow_graph() -> StateGraph:
    """
    Erstellt den LangGraph Workflow mit Retry-Loops
    
    Returns:
        Kompilierter StateGraph
    """
    logger.info("Erstelle LangGraph Workflow mit Retry-Loops...")
    
    # Erstelle Graph
    workflow = StateGraph(WorkflowState)
    
    # Füge Nodes hinzu
    workflow.add_node("parse", parsing_node)
    workflow.add_node("segment", segmentation_node)
    workflow.add_node("classify", classification_node)
    workflow.add_node("rewrite", rewriting_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("assemble", assembly_node)
    
    # Definiere Edges (bis Validation)
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "segment")
    workflow.add_edge("segment", "classify")
    workflow.add_edge("classify", "rewrite")
    workflow.add_edge("rewrite", "validate")
    
    # ⭐ HAUPTFEATURE: Conditional Edge mit Retry-Loop
    workflow.add_conditional_edges(
        "validate",
        should_retry_after_validation,
        {
            "retry": "rewrite",      # ← LOOP zurück zu Rewriting!
            "assemble": "assemble",  # ← Weiter zu Assembly
            "error": END             # ← Bei Fehler stoppen
        }
    )
    
    # Ende nach Assembly
    workflow.add_edge("assemble", END)
    
    # Kompiliere
    app = workflow.compile()
    
    logger.info("✓ LangGraph Workflow mit Retry-Loops erstellt")
    
    return app