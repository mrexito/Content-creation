"""
Rewriting Chain: Original → Varianten
Domain-spezifische Content-Variation mit Diversity-Mechanismus
"""
from typing import Dict, Any, List
from difflib import SequenceMatcher

from common.constants import DOMAIN_LANGUAGES
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
    Chain für Content-Variation mit Diversity-Mechanismus
    """
    
    # Mapping: Domain → System Prompt
    DOMAIN_PROMPTS = {
        'mathematics': REWRITING_MATH_SYSTEM_PROMPT,
        'languages': REWRITING_LANGUAGES_SYSTEM_PROMPT,
        'economics': REWRITING_ECONOMICS_SYSTEM_PROMPT,
        'general': REWRITING_GENERAL_SYSTEM_PROMPT
    }
    
    def __init__(
        self, 
        num_variants: int = 3,
        min_similarity_threshold: float = 0.7,
        max_attempts_per_variant: int = 3
    ):
        """
        Args:
            num_variants: Anzahl zu generierender Varianten
            min_similarity_threshold: Minimale Ähnlichkeit für "zu ähnlich" (0-1)
            max_attempts_per_variant: Max Versuche pro Variante
        """
        self.llm = get_llm_handler()
        self.num_variants = num_variants
        self.min_similarity_threshold = min_similarity_threshold
        self.max_attempts_per_variant = max_attempts_per_variant
        
        logger.info(
            f"RewritingChain initialisiert "
            f"(Varianten: {num_variants}, Similarity-Threshold: {min_similarity_threshold})"
        )
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Berechnet Text-Ähnlichkeit (0-1)"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _is_too_similar(self, new_variant: str, existing_variants: List[str]) -> bool:
        """
        Prüft ob neue Variante zu ähnlich zu bestehenden ist
        
        Returns:
            True wenn zu ähnlich, False wenn ausreichend different
        """
        for existing in existing_variants:
            similarity = self._calculate_similarity(new_variant, existing)
            if similarity >= self.min_similarity_threshold:
                logger.debug(f"Variante zu ähnlich: {similarity:.2f} >= {self.min_similarity_threshold}")
                return True
        return False
    
    def rewrite_segment(
        self,
        segment: Dict,
        domain: str = 'general'
    ) -> Dict[str, Any]:
        """
        Generiert diverse Varianten eines Segments
        
        Args:
            segment: Dict mit 'text' und optional 'type'
            domain: Domain des Contents
        
        Returns:
            Dict mit variants, metadata, success
        """
        text = segment.get('text', '')
        logger.info(f"Generiere {self.num_variants} diverse Varianten für {domain}-Segment")
        
        # Wähle passenden System-Prompt
        system_prompt = self.DOMAIN_PROMPTS.get(domain, REWRITING_GENERAL_SYSTEM_PROMPT)
        
        # Sammle Varianten
        variants = []
        variant_texts = []  # Für Similarity-Check
        
        for i in range(self.num_variants):
            logger.debug(f"  Generiere Variante {i+1}/{self.num_variants}")
            
            # Versuche diverse Variante zu generieren
            attempt = 0
            success = False
            
            while attempt < self.max_attempts_per_variant and not success:
                attempt += 1
                
                # User-Prompt mit Context der bisherigen Varianten
                if variant_texts:
                    user_prompt = (
                        f"{REWRITING_USER_PROMPT_TEMPLATE.format(text=text)}\n\n"
                        f"WICHTIG: Du hast bereits folgende Varianten erstellt:\n"
                    )
                    for idx, prev_variant in enumerate(variant_texts, 1):
                        user_prompt += f"{idx}. {prev_variant}\n"
                    user_prompt += "\nErstelle eine DEUTLICH UNTERSCHIEDLICHE Variante!"
                else:
                    user_prompt = REWRITING_USER_PROMPT_TEMPLATE.format(text=text)
                
                # Temperature-Paradox: Für Languages darf Temperature nicht erhöht
                # werden, da BERTScore semantische Nähe erfordert.
                if domain == DOMAIN_LANGUAGES:
                    temperature = 0.7  # Konstant niedrig für BERT-Validierung
                else:
                    temperature = 0.9 + (attempt * 0.05)  # Steigt bei Wiederholungen

                result = self.llm.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=temperature
                )
                
                if not result['success']:
                    logger.warning(f"    Versuch {attempt} fehlgeschlagen: {result.get('error')}")
                    continue
                
                new_variant = result['text']
                
                # Prüfe Similarity
                if self._is_too_similar(new_variant, variant_texts):
                    logger.debug(f"    Versuch {attempt}: Variante zu ähnlich, versuche erneut")
                    continue
                
                # Variante akzeptiert!
                variant_texts.append(new_variant)
                variants.append({
                    'variant_id': i + 1,
                    'text': new_variant,
                    'model': result['model'],
                    'tokens': result['tokens'],
                    'attempts': attempt
                })
                success = True
                logger.debug(f"    ✓ Variante {i+1} akzeptiert (Versuch {attempt})")
            
            if not success:
                logger.warning(f"  ✗ Variante {i+1}: Keine diverse Variante nach {self.max_attempts_per_variant} Versuchen")
                variants.append({
                    'variant_id': i + 1,
                    'text': None,
                    'error': f'Keine diverse Variante nach {self.max_attempts_per_variant} Versuchen',
                    'attempts': self.max_attempts_per_variant
                })
        
        successful_variants = [v for v in variants if v.get('text')]
        
        # Berechne Diversity-Statistik
        diversity_score = None
        if len(successful_variants) >= 2:
            similarities = []
            for i in range(len(successful_variants)):
                for j in range(i + 1, len(successful_variants)):
                    sim = self._calculate_similarity(
                        successful_variants[i]['text'],
                        successful_variants[j]['text']
                    )
                    similarities.append(sim)
            
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            diversity_score = 1.0 - avg_similarity
        
        # Logging mit korrektem Format
        diversity_str = f"{diversity_score:.2f}" if diversity_score is not None else "N/A"
        logger.info(
            f"✓ {len(successful_variants)}/{self.num_variants} Varianten erfolgreich "
            f"(Diversity-Score: {diversity_str})"
        )
        
        return {
            'original': text,
            'variants': variants,
            'domain': domain,
            'metadata': {
                'num_requested': self.num_variants,
                'num_successful': len(successful_variants),
                'segment_type': segment.get('type'),
                'diversity_score': diversity_score,
                'avg_attempts': sum(v.get('attempts', 0) for v in variants) / len(variants) if variants else 0
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


def get_rewriting_chain(
    num_variants: int = 3,
    min_similarity_threshold: float = 0.7
) -> RewritingChain:
    """Factory für RewritingChain"""
    return RewritingChain(
        num_variants=num_variants,
        min_similarity_threshold=min_similarity_threshold
    )