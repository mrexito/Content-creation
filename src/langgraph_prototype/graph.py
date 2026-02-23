"""
LangGraph Workflow Graph
Definiert den kompletten State-basierten Workflow
"""
from langgraph.graph import StateGraph, END

from langgraph_prototype.state.workflow_state import WorkflowState
from langgraph_prototype.nodes.parsing_node import parsing_node
from langgraph_prototype.nodes.segmentation_node import segmentation_node
from langgraph_prototype.nodes.classification_node import classification_node
from langgraph_prototype.nodes.rewriting_node import rewriting_node
from langgraph_prototype.nodes.validation_node import validation_node
from langgraph_prototype.nodes.assembly_node import assembly_node

from common.logger import setup_logger

logger = setup_logger(__name__)


def should_continue_after_validation(state: WorkflowState) -> str:
    """
    Conditional Edge: Entscheidet ob Workflow weitergehen kann
    
    Returns:
        'assemble' wenn erfolgreich
        'error' wenn Fehler aufgetreten
    """
    if state['current_phase'] == 'error':
        return 'error'
    
    if state['current_phase'] == 'validation_complete':
        return 'assemble'
    
    return 'error'


def create_workflow_graph() -> StateGraph:
    """
    Erstellt den LangGraph Workflow
    
    Returns:
        Kompilierter StateGraph
    """
    logger.info("Erstelle LangGraph Workflow...")
    
    # Erstelle Graph
    workflow = StateGraph(WorkflowState)
    
    # Füge Nodes hinzu
    workflow.add_node("parse", parsing_node)
    workflow.add_node("segment", segmentation_node)
    workflow.add_node("classify", classification_node)
    workflow.add_node("rewrite", rewriting_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("assemble", assembly_node)
    
    # Definiere Edges (Linear Flow)
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "segment")
    workflow.add_edge("segment", "classify")
    workflow.add_edge("classify", "rewrite")
    workflow.add_edge("rewrite", "validate")
    
    # Conditional Edge nach Validation
    workflow.add_conditional_edges(
        "validate",
        should_continue_after_validation,
        {
            "assemble": "assemble",
            "error": END
        }
    )
    
    # Ende nach Assembly
    workflow.add_edge("assemble", END)
    
    # Kompiliere
    app = workflow.compile()
    
    logger.info("✓ LangGraph Workflow erstellt")
    
    return app