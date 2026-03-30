"""
Classification Node: Segments → Classified Segments
"""
import time

from common.llm_handler import get_llm_handler
from common.logger import setup_logger
from langgraph_prototype.state.workflow_state import WorkflowState
from langchain_prototype.prompts.classification_prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    CLASSIFICATION_USER_PROMPT_TEMPLATE
)

logger = setup_logger(__name__)


def classification_node(state: WorkflowState) -> WorkflowState:
    """
    Node für Segment-Klassifizierung
    
    Input (State):
        - segments
    
    Output (State Updates):
        - classified_segments (segments + classification)
        - current_phase
    """
    logger.info("Classification Node")
    
    start_time = time.time()
    
    try:
        segments = state['segments']
        
        if not segments:
            error_msg = "No segments to classify"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        llm = get_llm_handler()
        classified_segments = []
        
        for idx, segment in enumerate(segments):
            text = segment.get('text', '')
            
            logger.debug(f"  Klassifiziere Segment {idx+1}/{len(segments)}")
            
            user_prompt = CLASSIFICATION_USER_PROMPT_TEMPLATE.format(text=text)
            
            result = llm.generate_structured(
                prompt=user_prompt,
                response_format={
                    "domain": "string",
                    "content_type": "string",
                    "confidence": "number"
                },
                system_prompt=CLASSIFICATION_SYSTEM_PROMPT
            )
            
            if result['success']:
                classification = result['parsed_data']
                classified_segments.append({
                    'segment': segment,
                    'classification': classification
                })
            else:
                # Fallback: Unclassified
                logger.warning(f"  Classification failed for segment {idx+1}")
                classified_segments.append({
                    'segment': segment,
                    'classification': {
                        'domain': 'general',
                        'content_type': 'unknown',
                        'confidence': 0.0
                    }
                })
        
        # Update State
        state['classified_segments'] = classified_segments
        state['current_phase'] = 'classification_complete'
        state['total_processing_time'] += time.time() - start_time
        
        logger.info(f"  [OK] Classified {len(classified_segments)} segments")
        
        return state
        
    except Exception as e:
        error_msg = f"Classification error: {str(e)}"
        logger.error(error_msg)
        state['errors'].append(error_msg)
        state['current_phase'] = 'error'
        return state