"""
Rewriting Chain: Original → Varianten
Domain-spezifische Content-Variation
"""
from typing import Dict, Any, List

from common.llm_handler import get_llm_handler
from common.logger import setup_logger
from langchain_prototype.prompts.rewriting_prompts import (
    REWRITING_MATH_SYSTEM_PROMPT,
    REWRITING_LANGUAGES_SYSTEM_PROMPT,
    REWRITING_ECONOMICS_SYSTEM_PROMPT,
    REWRITING_GENERAL_SYSTEM_PROMPT,
    REWRITING_USER_PROMPT_TEMPLATE
)

logger = setup_logger(__name__)


class RewritingChain:
    """
    Chain für Content-Variation (domain-spezifisch)
    """
    
    # Mapping: Domain → System Prompt
    DOMAIN_PROMPTS = {
        'mathematics': REWRITING_MATH_SYSTEM_PROMPT,
        'languages': REWRITING_LANGUAGES_SYSTEM_PROMPT,
        'economics': REWRITING_ECONOMICS_SYSTEM_PROMPT,
        'general': REWRITING_GENERAL_SYSTEM_PROMPT
    }
    
    def __init__(self, num_variants: int = 3):
        """
        Args:
            num_variants: Anzahl zu generierender Varianten
        """
        self.llm = get_llm_handler()
        self.num_variants = num_variants
        logger.info(f"RewritingChain initialisiert (Varianten: {num_variants})")
    
    def rewrite_segment(
        self,
        segment: Dict,
        domain: str = 'general'
    ) -> Dict[str, Any]:
        """
        Generiert Varianten eines Segments
        
        Args:
            segment: Dict mit 'text' und optional 'type'
            domain: Domain des Contents (mathematics, languages, economics, general)
        
        Returns:
            Dict mit variants, metadata, success
        """
        text = segment.get('text', '')
        logger.info(f"Generiere {self.num_variants} Varianten für {domain}-Segment")
        
        # Wähle passenden System-Prompt
        system_prompt = self.DOMAIN_PROMPTS.get(domain, REWRITING_GENERAL_SYSTEM_PROMPT)
        
        # User-Prompt
        user_prompt = REWRITING_USER_PROMPT_TEMPLATE.format(text=text)
        
        # Generiere Varianten
        variants = []
        
        for i in range(self.num_variants):
            logger.debug(f"  Generiere Variante {i+1}/{self.num_variants}")
            
            result = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8  # Höhere Temperature für mehr Variation
            )
            
            if result['success']:
                variants.append({
                    'variant_id': i + 1,
                    'text': result['text'],
                    'model': result['model'],
                    'tokens': result['tokens']
                })
            else:
                logger.warning(f"  Variante {i+1} fehlgeschlagen: {result.get('error')}")
                variants.append({
                    'variant_id': i + 1,
                    'text': None,
                    'error': result.get('error')
                })
        
        successful_variants = [v for v in variants if v.get('text')]
        
        logger.info(f"✓ {len(successful_variants)}/{self.num_variants} Varianten erfolgreich")
        
        return {
            'original': text,
            'variants': variants,
            'domain': domain,
            'metadata': {
                'num_requested': self.num_variants,
                'num_successful': len(successful_variants),
                'segment_type': segment.get('type')
            },
            'success': len(successful_variants) > 0
        }
    
    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke Methode
        
        Args:
            input_data: Dict mit 'segment' und 'domain'
        
        Returns:
            Dict mit rewriting results
        """
        segment = input_data.get('segment', {})
        domain = input_data.get('domain', 'general')
        return self.rewrite_segment(segment, domain)


def get_rewriting_chain(num_variants: int = 3) -> RewritingChain:
    """Factory für RewritingChain"""
    return RewritingChain(num_variants=num_variants)