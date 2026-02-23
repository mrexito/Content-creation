"""
Validation Node: Variants → Validated Variants
Mit domain-spezifischen Thresholds
"""
import time

from common.validators import (
    get_sympy_validator,
    get_bert_validator,
    get_consistency_validator
)
from common.logger import setup_logger
from langgraph_prototype.state.workflow_state import WorkflowState

logger = setup_logger(__name__)


def validation_node(state: WorkflowState) -> WorkflowState:
    """
    Validation Node mit domain-spezifischen Thresholds
    
    Input (State):
        - segments_with_variants
    
    Output (State Updates):
        - segments_with_variants (updated mit validation)
        - current_phase
    """
    logger.info("🔗 Validation Node")
    
    start_time = time.time()
    
    try:
        segments_with_variants = state['segments_with_variants']
        
        if not segments_with_variants:
            error_msg = "No variants to validate"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        # Validators
        sympy_validator = get_sympy_validator()
        bert_validator = get_bert_validator()
        consistency_validator = get_consistency_validator()
        
        total_valid = 0
        total_invalid = 0
        
        for seg_data in segments_with_variants:
            segment = seg_data['segment']
            classification = seg_data['classification']
            variants = seg_data['variants']
            
            original_text = segment.get('text', '')
            domain = classification.get('domain', 'general')
            
            # Validiere jede Variante
            for variant in variants:
                variant_text = variant.get('text')
                
                if not variant_text:
                    variant['validation'] = {'is_valid': False, 'error': 'No text'}
                    total_invalid += 1
                    continue
                
                # Domain-spezifische Validation
                validation_results = {}
                issues = []
                
                if domain == 'mathematics':
                    # SymPy
                    original_val = sympy_validator.validate_text(original_text)
                    variant_val = sympy_validator.validate_text(variant_text)
                    
                    validation_results['sympy'] = {
                        'original_equations': original_val['equations_found'],
                        'variant_equations': variant_val['equations_found']
                    }
                    
                    # Toleranz: ±1 Gleichung
                    equation_diff = abs(original_val['equations_found'] - variant_val['equations_found'])
                    if equation_diff > 1:
                        issues.append(
                            f"Anzahl Gleichungen unterschiedlich: "
                            f"{original_val['equations_found']} vs {variant_val['equations_found']}"
                        )
                
                elif domain == 'languages':
                    # BERT mit niedrigerem Threshold
                    bert_result = bert_validator.validate_paraphrase(
                        original=original_text,
                        paraphrased=variant_text,
                        min_threshold=0.70  # ← GEÄNDERT von 0.85
                    )
                    
                    validation_results['bert'] = bert_result
                    
                    if not bert_result['is_valid']:
                        issues.append(f"BERT-Score zu niedrig: {bert_result['score']:.2f} < 0.70")
                
                elif domain == 'economics':
                    # Consistency mit höherer Toleranz
                    original_numbers = consistency_validator.extract_numbers(original_text)
                    variant_numbers = consistency_validator.extract_numbers(variant_text)
                    
                    validation_results['consistency'] = {
                        'original_numbers': len(original_numbers),
                        'variant_numbers': len(variant_numbers)
                    }
                    
                    # Toleranz: ±3 Zahlen
                    number_diff = abs(len(original_numbers) - len(variant_numbers))
                    if number_diff > 3:  # ← GEÄNDERT von 2
                        issues.append(
                            f"Anzahl Zahlen stark unterschiedlich: "
                            f"{len(original_numbers)} vs {len(variant_numbers)}"
                        )
                
                # Length check mit domain-spezifischer Toleranz
                length_ratio = len(variant_text) / len(original_text) if len(original_text) > 0 else 0
                
                # Domain-spezifische Ranges
                if domain == 'economics':
                    min_ratio, max_ratio = 0.4, 2.5
                elif domain == 'languages':
                    min_ratio, max_ratio = 0.6, 1.8
                else:
                    min_ratio, max_ratio = 0.5, 2.0
                
                if length_ratio < min_ratio or length_ratio > max_ratio:
                    issues.append(
                        f"Länge weicht stark ab: {len(variant_text)} vs {len(original_text)} "
                        f"Zeichen (Ratio: {length_ratio:.2f}, erlaubt: {min_ratio}-{max_ratio})"
                    )
                
                # Validation Result
                is_valid = len(issues) == 0
                
                variant['validation'] = {
                    'is_valid': is_valid,
                    'validation_results': validation_results,
                    'issues': issues
                }
                
                if is_valid:
                    total_valid += 1
                else:
                    total_invalid += 1
        
        # Update State
        state['current_phase'] = 'validation_complete'
        state['total_processing_time'] += time.time() - start_time
        
        logger.info(f"  ✓ Validated: {total_valid} valid, {total_invalid} invalid")
        
        return state
        
    except Exception as e:
        error_msg = f"Validation error: {str(e)}"
        logger.error(error_msg)
        state['errors'].append(error_msg)
        state['current_phase'] = 'error'
        return state