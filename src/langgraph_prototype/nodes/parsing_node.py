"""
Parsing Node: PDF → Text
"""
import time
from pathlib import Path

from common.ocr_handler import get_ocr_handler, reset_ocr_handler
from common.logger import setup_logger
from langgraph_prototype.state.workflow_state import WorkflowState

logger = setup_logger(__name__)


def parsing_node(state: WorkflowState) -> WorkflowState:
    """
    Node für PDF-Parsing mit OCR

    Input (State):
        - pdf_path
        - domain (optional)

    Output (State Updates):
        - raw_text
        - ocr_metadata
        - current_phase
    """
    # Skip if raw_text already set by shared pre-parsed OCR result
    if state.get('raw_text') and state.get('current_phase') == 'parsing_complete':
        logger.info("🔗 Parsing Node: Übersprungen (geteiltes OCR-Ergebnis)")
        return state

    logger.info(f"🔗 Parsing Node: {state['pdf_path']}")
    
    start_time = time.time()
    
    try:
        # OCR-Handler
        ocr = get_ocr_handler()
        
        # Parse PDF
        result = ocr.pdf_to_text(
            Path(state['pdf_path']),
            domain=state.get('domain')
        )
        
        if not result['success']:
            error_msg = f"Parsing failed: {result.get('error')}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state

        # Fallback: Mistral sometimes returns success with 0 chars (silent rate-limit failure)
        if not result['text'].strip():
            logger.warning("  ⚠ OCR lieferte keinen Text – Fallback auf Tesseract")
            reset_ocr_handler()
            tesseract_ocr = get_ocr_handler(default_tool="tesseract")
            result = tesseract_ocr.pdf_to_text(
                Path(state['pdf_path']), domain=state.get('domain')
            )
            if not result.get('text', '').strip():
                error_msg = "OCR konnte keinen Text extrahieren (weder Mistral noch Tesseract)"
                logger.error(error_msg)
                state['errors'].append(error_msg)
                state['current_phase'] = 'error'
                return state

        # Update State
        state['raw_text'] = result['text']
        state['ocr_metadata'] = {
            'tool_used': result['tool_used'],
            'pages': result['pages'],
            'processing_time': result['processing_time'],
            'char_count': len(result['text'])
        }
        state['current_phase'] = 'parsing_complete'
        state['total_processing_time'] += time.time() - start_time
        
        logger.info(f"  ✓ Parsed {result['pages']} pages, {len(result['text'])} chars")
        
        return state
        
    except Exception as e:
        error_msg = f"Parsing error: {str(e)}"
        logger.error(error_msg)
        state['errors'].append(error_msg)
        state['current_phase'] = 'error'
        return state