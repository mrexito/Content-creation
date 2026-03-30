"""
Assembly Node: Validated Variants → Final Document
"""
import time
import json
from datetime import datetime

from common.logger import setup_logger
from langgraph_prototype.state.workflow_state import WorkflowState

logger = setup_logger(__name__)


def assembly_node(state: WorkflowState) -> WorkflowState:
    """
    Assembly Node
    
    Input (State):
        - segments_with_variants (mit validation)
    
    Output (State Updates):
        - final_document
        - current_phase
    """
    logger.info("Assembly Node")
    
    start_time = time.time()
    
    try:
        segments_with_variants = state['segments_with_variants']
        
        if not segments_with_variants:
            error_msg = "No variants to assemble"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        # Assembliere Dokument
        assembled_segments = []
        
        total_variants = 0
        valid_variants = 0
        
        for seg_data in segments_with_variants:
            segment = seg_data['segment']
            classification = seg_data['classification']
            variants = seg_data['variants']
            
            # Filter valide Varianten
            valid_vars = [
                v for v in variants
                if v.get('validation', {}).get('is_valid', False)
            ]
            
            total_variants += len(variants)
            valid_variants += len(valid_vars)
            
            assembled_segments.append({
                'original': segment.get('text', ''),
                'segment_type': segment.get('type', 'unknown'),
                'classification': classification,
                'num_variants': len(valid_vars),
                'variants': [
                    {
                        'variant_id': v.get('variant_id'),
                        'text': v.get('text'),
                        'validation_score': 1.0 if v.get('validation', {}).get('is_valid') else 0.0,
                        'solution': v.get('solution'),  # Musterantwort (kann None sein)
                    }
                    for v in valid_vars
                ]
            })
        
        # Erstelle Text-Output
        text_lines = []
        text_lines.append("=" * 70)
        text_lines.append("VARIANTEN-DOKUMENT (LangGraph)")
        text_lines.append(f"Original: {state['pdf_path']}")
        text_lines.append(f"Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        text_lines.append("=" * 70)
        text_lines.append("")
        
        for idx, seg in enumerate(assembled_segments, 1):
            text_lines.append(f"## Segment {idx}: {seg['segment_type'].upper()}")
            text_lines.append("")
            text_lines.append("**Original:**")
            text_lines.append(seg['original'])
            text_lines.append("")
            
            if seg['num_variants'] > 0:
                text_lines.append(f"**Varianten ({seg['num_variants']}):**")
                text_lines.append("")
                
                for variant in seg['variants']:
                    text_lines.append(f"Variante {variant['variant_id']}:")
                    text_lines.append(variant['text'])
                    text_lines.append("")
            else:
                text_lines.append("*Keine validen Varianten generiert*")
                text_lines.append("")
            
            text_lines.append("-" * 70)
            text_lines.append("")
        
        # Final Document
        final_document = {
            'segments': assembled_segments,
            'text_output': '\n'.join(text_lines),
            'metadata': {
                'pdf_path': state['pdf_path'],
                'domain': state.get('domain'),
                'num_variants_requested': state['num_variants'],
                'total_variants': total_variants,
                'valid_variants': valid_variants,
                'validation_rate': valid_variants / total_variants if total_variants > 0 else 0,
                **state.get('ocr_metadata', {})
            }
        }
        
        # Update State
        state['final_document'] = final_document
        state['current_phase'] = 'assembly_complete'
        state['total_processing_time'] += time.time() - start_time
        
        logger.info(
            f"  ✓ Assembled document: {valid_variants}/{total_variants} valid variants "
            f"({final_document['metadata']['validation_rate']*100:.1f}%)"
        )
        
        return state
        
    except Exception as e:
        error_msg = f"Assembly error: {str(e)}"
        logger.error(error_msg)
        state['errors'].append(error_msg)
        state['current_phase'] = 'error'
        return state