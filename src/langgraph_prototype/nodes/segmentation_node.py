"""
Segmentation Node: Text → Segments
"""
import time

from common.llm_handler import get_llm_handler
from common.logger import setup_logger
from langgraph_prototype.state.workflow_state import WorkflowState
from langchain_prototype.prompts.segmentation_prompts import (
    SEGMENTATION_SYSTEM_PROMPT,
    SEGMENTATION_USER_PROMPT_TEMPLATE
)

logger = setup_logger(__name__)


def segmentation_node(state: WorkflowState) -> WorkflowState:
    """
    Node für Text-Segmentierung
    
    Input (State):
        - raw_text
    
    Output (State Updates):
        - segments
        - current_phase
    """
    logger.info("🔗 Segmentation Node")
    
    start_time = time.time()
    
    try:
        text = state['raw_text']
        
        if not text:
            error_msg = "No text to segment"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        # LLM für Segmentierung
        llm = get_llm_handler()
        
        user_prompt = SEGMENTATION_USER_PROMPT_TEMPLATE.format(text=text)
        
        result = llm.generate_structured(
            prompt=user_prompt,
            response_format={
                "segments": [{"type": "string", "text": "string"}]
            },
            system_prompt=SEGMENTATION_SYSTEM_PROMPT
        )
        
        if not result['success']:
            error_msg = f"Segmentation failed: {result.get('error')}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        segments = result['parsed_data'].get('segments', [])

        # Update State
        state['segments'] = segments
        state['current_phase'] = 'segmentation_complete'
        state['total_processing_time'] += time.time() - start_time

        # Identische Prompts (langchain_prototype.prompts.segmentation_prompts) werden
        # von LangChain und LangGraph geteilt – methodisch erforderlich für fairen Vergleich.
        text = state.get('raw_text', '')
        logger.info(f"  ✓ Segmented into {len(segments)} segments")
        logger.debug(f"  Segmentierung: {len(segments)} Segmente aus {len(text)} Zeichen")
        
        return state
        
    except Exception as e:
        error_msg = f"Segmentation error: {str(e)}"
        logger.error(error_msg)
        state['errors'].append(error_msg)
        state['current_phase'] = 'error'
        return state