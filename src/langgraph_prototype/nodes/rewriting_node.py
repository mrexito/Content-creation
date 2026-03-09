"""
Rewriting Node: Original → Varianten
Domain-spezifische Content-Variation mit Diversity-Mechanismus und Retry-Awareness
"""
import time
from typing import Dict, Any
from difflib import SequenceMatcher

from common.constants import DOMAIN_LANGUAGES
from common.llm_handler import get_llm_handler
from common.logger import setup_logger
from langgraph_prototype.state.workflow_state import WorkflowState
from langchain_prototype.prompts.rewriting_prompts import (
    REWRITING_MATH_SYSTEM_PROMPT,
    REWRITING_LANGUAGES_SYSTEM_PROMPT,
    REWRITING_ECONOMICS_SYSTEM_PROMPT,
    REWRITING_GENERAL_SYSTEM_PROMPT,
    REWRITING_USER_PROMPT_TEMPLATE
)

logger = setup_logger(__name__)


class RewritingNode:
    """Node für Content-Rewriting mit Diversity und Retry-Awareness"""
    
    DOMAIN_PROMPTS = {
        'mathematics': REWRITING_MATH_SYSTEM_PROMPT,
        'languages': REWRITING_LANGUAGES_SYSTEM_PROMPT,
        'economics': REWRITING_ECONOMICS_SYSTEM_PROMPT,
        'general': REWRITING_GENERAL_SYSTEM_PROMPT
    }
    
    def __init__(self):
        self.llm = get_llm_handler()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Berechnet Text-Ähnlichkeit"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _generate_variant(
        self,
        text: str,
        domain: str,
        existing_variants: list,
        temperature: float = 0.9
    ) -> Dict[str, Any]:
        """Generiert eine einzelne Variante"""
        
        system_prompt = self.DOMAIN_PROMPTS.get(domain, REWRITING_GENERAL_SYSTEM_PROMPT)
        
        # User-Prompt mit Context
        if existing_variants:
            user_prompt = (
                f"{REWRITING_USER_PROMPT_TEMPLATE.format(text=text)}\n\n"
                f"WICHTIG: Du hast bereits folgende Varianten erstellt:\n"
            )
            for idx, var in enumerate(existing_variants, 1):
                user_prompt += f"{idx}. {var}\n"
            user_prompt += "\nErstelle eine DEUTLICH UNTERSCHIEDLICHE Variante!"
        else:
            user_prompt = REWRITING_USER_PROMPT_TEMPLATE.format(text=text)
        
        # LLM Call
        result = self.llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        return result
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        """
        Rewriting Node mit Retry-Awareness
        
        Input (State):
            - classified_segments
            - num_variants
            - similarity_threshold
            - retry_counts (für Retry-Logik)
        
        Output (State Updates):
            - segments_with_variants
            - current_phase
        """
        logger.info("🔗 Rewriting Node")
        
        # Check if this is a retry
        is_retry = state.get('current_phase') == 'validation_failed'
        
        if is_retry:
            logger.info("  🔄 RETRY MODE: Generiere neue Varianten mit höherer Temperature")
        
        start_time = time.time()
        
        try:
            classified_segments = state['classified_segments']
            num_variants = state['num_variants']
            similarity_threshold = state['similarity_threshold']
            
            if not classified_segments:
                error_msg = "No classified segments to rewrite"
                logger.error(error_msg)
                state['errors'].append(error_msg)
                return state
            
            segments_with_variants = []
            
            for idx, cs in enumerate(classified_segments):
                segment = cs['segment']
                classification = cs['classification']
                domain = classification.get('domain', 'general')
                text = segment.get('text', '')
                
                # Check retry count for this segment
                retry_count = state.get('retry_counts', {}).get(idx, 0)
                
                logger.info(f"  Rewriting segment {idx+1}/{len(classified_segments)} ({domain}, retry: {retry_count})")
                
                # Generiere Varianten mit retry-angepasster Temperature
                variants = []
                variant_texts = []
                
                # Temperature-Paradox: Für die Languages-Domain darf die Temperature
                # bei Retries NICHT erhöht werden, da BERTScore semantische Nähe zum
                # Original erfordert — höhere Temperature → grössere Abweichung →
                # niedrigerer BERTScore → mehr Retries (Teufelskreis).
                # Math/Economics: leichter Anstieg zur Diversitätssteigerung.
                base_temperature = 0.95 if is_retry else 0.9

                for v_idx in range(num_variants):
                    max_attempts = 3

                    for attempt in range(max_attempts):
                        if domain == DOMAIN_LANGUAGES:
                            # Konstant niedrig für BERT-Validierung
                            temperature = 0.7
                        else:
                            temperature = base_temperature + (retry_count * 0.05) + (attempt * 0.05)
                            temperature = min(temperature, 1.0)  # Cap bei 1.0
                        
                        result = self._generate_variant(
                            text=text,
                            domain=domain,
                            existing_variants=variant_texts,
                            temperature=temperature
                        )
                        
                        if not result['success']:
                            continue
                        
                        variant_text = result['text']
                        
                        # Check Similarity
                        is_too_similar = any(
                            self._calculate_similarity(variant_text, existing) >= similarity_threshold
                            for existing in variant_texts
                        )
                        
                        if is_too_similar and attempt < max_attempts - 1:
                            logger.debug(f"    Variante {v_idx+1} zu ähnlich, Retry {attempt+1}")
                            continue
                        
                        # Akzeptiert
                        variant_texts.append(variant_text)
                        variants.append({
                            'variant_id': v_idx + 1,
                            'text': variant_text,
                            'attempts': attempt + 1,
                            'temperature_used': temperature,
                            'retry_iteration': retry_count
                        })
                        logger.debug(f"    ✓ Variante {v_idx+1} (T={temperature:.2f}, Retry={retry_count})")
                        break
                
                segments_with_variants.append({
                    'segment_idx': idx,  # Index tracken für Retry
                    'segment': segment,
                    'classification': classification,
                    'variants': variants
                })
            
            # Update State
            state['segments_with_variants'] = segments_with_variants
            state['current_phase'] = 'rewriting_complete'
            state['total_processing_time'] += time.time() - start_time
            
            total_variants = sum(len(s['variants']) for s in segments_with_variants)
            logger.info(f"  ✓ Generated {total_variants} variants")
            
            return state
            
        except Exception as e:
            error_msg = f"Rewriting error: {str(e)}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            state['current_phase'] = 'error'
            return state


# Factory
def rewriting_node(state: WorkflowState) -> WorkflowState:
    """Factory für Rewriting Node"""
    node = RewritingNode()
    return node(state)