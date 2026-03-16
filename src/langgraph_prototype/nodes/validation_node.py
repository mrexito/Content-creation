"""
Validation Node: Variants → Validated Variants
Mit domain-spezifischen Thresholds und Retry-Tracking
"""
import time

from common.validators import (
    get_sympy_validator,
    get_bert_validator,
    get_consistency_validator
)
from common.constants import BERT_THRESHOLD, EQUATION_COUNT_TOLERANCE, NUMBER_COUNT_TOLERANCE, LENGTH_RATIO_BOUNDS
from common.utils import check_placeholder_preservation
from common.logger import setup_logger
from langgraph_prototype.state.workflow_state import WorkflowState

logger = setup_logger(__name__)


def validation_node(state: WorkflowState) -> WorkflowState:
    """
    Validation Node mit domain-spezifischen Thresholds und Retry-Tracking
    
    Input (State):
        - segments_with_variants
    
    Output (State Updates):
        - segments_with_variants (updated mit validation)
        - validation_stats (für Retry-Logik)
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
                    
                    equation_diff = abs(original_val['equations_found'] - variant_val['equations_found'])
                    if equation_diff > EQUATION_COUNT_TOLERANCE:
                        issues.append(
                            f"Anzahl Gleichungen unterschiedlich: "
                            f"{original_val['equations_found']} vs {variant_val['equations_found']}"
                        )
                
                elif domain == 'languages':
                    bert_result = bert_validator.validate_paraphrase(
                        original=original_text,
                        paraphrased=variant_text,
                        min_threshold=BERT_THRESHOLD,
                    )

                    validation_results['bert'] = bert_result

                    if not bert_result['is_valid']:
                        issues.append(f"BERT-Score zu niedrig: {bert_result['score']:.2f} < {BERT_THRESHOLD}")

                    # Placeholder-Check
                    placeholder_result = check_placeholder_preservation(original_text, variant_text)
                    validation_results['placeholder'] = placeholder_result

                    if not placeholder_result.get('skipped') and not placeholder_result['is_valid']:
                        issues.append(
                            f"Platzhalter nicht erhalten: "
                            f"{placeholder_result['variant_count']} von "
                            f"{placeholder_result['original_count']} Platzhaltern vorhanden "
                            f"(min. 80% erforderlich)"
                        )

                elif domain == 'economics':
                    # Consistency mit höherer Toleranz
                    original_numbers = consistency_validator.extract_numbers(original_text)
                    variant_numbers = consistency_validator.extract_numbers(variant_text)
                    
                    validation_results['consistency'] = {
                        'original_numbers': len(original_numbers),
                        'variant_numbers': len(variant_numbers)
                    }
                    
                    number_diff = abs(len(original_numbers) - len(variant_numbers))
                    if number_diff > NUMBER_COUNT_TOLERANCE:
                        issues.append(
                            f"Anzahl Zahlen stark unterschiedlich: "
                            f"{len(original_numbers)} vs {len(variant_numbers)}"
                        )
                
                # Length check mit domain-spezifischer Toleranz
                length_ratio = len(variant_text) / len(original_text) if len(original_text) > 0 else 0
                min_ratio, max_ratio = LENGTH_RATIO_BOUNDS.get(domain, LENGTH_RATIO_BOUNDS["default"])
                
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
        
        state['total_processing_time'] += time.time() - start_time

        logger.info(f"  ✓ Validated: {total_valid} valid, {total_invalid} invalid")

        # Identifiziere Segmente die Retry brauchen
        # WICHTIG: retry_counts hier inkrementieren (nicht in der Edge-Funktion!).
        # LangGraph persistiert State-Mutationen in Edge-Funktionen nicht.
        segments_needing_retry = []

        for seg_data in segments_with_variants:
            segment_idx = seg_data.get('segment_idx', -1)
            variants = seg_data['variants']

            # Prüfe ob ALLE Varianten invalid sind
            all_invalid = all(
                not v.get('validation', {}).get('is_valid', False)
                for v in variants
                if v.get('text')  # Nur Varianten mit Text
            )

            if all_invalid and segment_idx >= 0:
                # Prüfe ob noch Retries übrig (vor dem Increment lesen!)
                retry_count = state.get('retry_counts', {}).get(segment_idx, 0)
                max_retries = state.get('max_retries', 3)

                if retry_count < max_retries:
                    segments_needing_retry.append(segment_idx)
                    logger.info(
                        f"  🔄 Segment {segment_idx} needs retry "
                        f"({retry_count + 1}/{max_retries})"
                    )

        # retry_counts im Node-Return inkrementieren (damit LangGraph sie persistiert)
        retry_counts = dict(state.get('retry_counts') or {})
        for seg_idx in segments_needing_retry:
            retry_counts[seg_idx] = retry_counts.get(seg_idx, 0) + 1
        state['retry_counts'] = retry_counts

        state['validation_stats'] = {
            'total_valid': total_valid,
            'total_invalid': total_invalid,
            'segments_needing_retry': segments_needing_retry,
        }

        # current_phase so setzen dass die Edge-Funktion sauber routen kann
        # 'validation_failed' → Edge leitet zurück zu Rewriting
        # 'validation_complete' → Edge leitet weiter zu Assembly
        if segments_needing_retry:
            state['current_phase'] = 'validation_failed'
        else:
            state['current_phase'] = 'validation_complete'

        return state
        
    except Exception as e:
        error_msg = f"Validation error: {str(e)}"
        logger.error(error_msg)
        state['errors'].append(error_msg)
        state['current_phase'] = 'error'
        return state