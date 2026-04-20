"""
Validation Node: Variants → Validated Variants
Mit domain-spezifischen Thresholds und Retry-Tracking
"""
import time

from common.validators import validate_segment
from common.logger import setup_logger
from langgraph_prototype.state.workflow_state import WorkflowState

try:
    from langchain_prototype.chains.solution_chain import get_solution_chain as _get_solution_chain
    _solution_chain = _get_solution_chain()
except Exception:
    _solution_chain = None

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
    logger.info("[OK] Validation Node")

    start_time = time.time()

    try:
        segments_with_variants = state['segments_with_variants']

        if not segments_with_variants:
            error_msg = "No variants to validate"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state

        total_valid = 0
        total_invalid = 0

        for seg_data in segments_with_variants:
            segment = seg_data['segment']
            classification = seg_data['classification']
            variants = seg_data['variants']

            original_text = segment.get('text', '')
            domain = classification.get('domain', 'general')

            for variant in variants:
                variant_text = variant.get('text')

                if not variant_text:
                    variant['validation'] = {'is_valid': False, 'error': 'No text'}
                    total_invalid += 1
                    continue

                result = validate_segment(original_text, variant_text, domain)

                variant['validation'] = {
                    'is_valid': result['is_valid'],
                    'validation_results': result['validation_results'],
                    'issues': result['issues'],
                }

                if result['is_valid']:
                    total_valid += 1
                    # Musterantwort für valide Variante generieren
                    if _solution_chain is not None:
                        try:
                            sol = _solution_chain.invoke({
                                'variant_text': variant_text,
                                'domain': domain,
                            })
                            variant['solution'] = sol.get('solution')
                        except Exception as _e:
                            logger.warning(f"Solution-Generierung fehlgeschlagen: {_e}")
                            variant['solution'] = None
                    else:
                        variant['solution'] = None
                else:
                    total_invalid += 1
                    variant['solution'] = None

        state['total_processing_time'] += time.time() - start_time

        logger.info(f"  [OK] Validated: {total_valid} valid, {total_invalid} invalid")

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
                        f"  [RETRY] Segment {segment_idx} needs retry "
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
            # Skalaren Retry-Zähler erhöhen (1 pro ausgelöstem Retry-Zyklus)
            state['retry_count'] = state.get('retry_count', 0) + 1
        else:
            state['current_phase'] = 'validation_complete'

        return state

    except Exception as e:
        error_msg = f"Validation error: {str(e)}"
        logger.exception(error_msg)
        state['errors'].append(error_msg)
        state['current_phase'] = 'error'
        return state
