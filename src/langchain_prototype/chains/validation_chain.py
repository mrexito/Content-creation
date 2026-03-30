"""
Validation Chain: Varianten → Validated Variants
Nutzt domain-spezifische Validators

LCEL-Kompatibilität:
    Kein LLM-Aufruf nötig — die Validierung erfolgt durch spezialisierte
    Bibliotheken (SymPy, BERTScore, Zahlen-Consistency).
    Die Chain ist via RunnableLambda als formales LCEL-Runnable verpackt.
"""
from typing import Dict, Any, List

from langchain_core.runnables import RunnableLambda

from common.validators import validate_segment
from common.logger import setup_logger

logger = setup_logger(__name__)


class ValidationChain:
    """
    Chain für Varianten-Validierung mit domain-spezifischen Validators
    """

    def __init__(self):
        """Initialisiert den LCEL-Runnable-Wrapper"""
        # RunnableLambda-Wrapper: macht ValidationChain formal LCEL-kompatibel.
        # Kein LLM-Aufruf — Validierung erfolgt durch SymPy / BERTScore / Zahlen-Check.
        self._runnable = RunnableLambda(self.invoke)
        logger.info("ValidationChain (LCEL-kompatibel) initialisiert")

    def validate_variant(
        self,
        original: str,
        variant: str,
        domain: str = 'general'
    ) -> Dict[str, Any]:
        """
        Validiert eine Variante.

        Args:
            original: Original-Text
            variant: Variante
            domain: Domain (mathematics, languages, economics, general)

        Returns:
            Dict mit validation_results, is_valid, issues
        """
        return validate_segment(original, variant, domain)

    def validate_variants(
        self,
        original: str,
        variants: List[Dict],
        domain: str = 'general'
    ) -> Dict[str, Any]:
        """
        Validiert alle Varianten

        Args:
            original: Original-Text
            variants: Liste von Varianten-Dicts
            domain: Domain

        Returns:
            Dict mit validated_variants, statistics
        """
        logger.info(f"Validiere {len(variants)} Varianten für {domain}")

        validated_variants = []

        for variant_dict in variants:
            variant_text = variant_dict.get('text')

            if not variant_text:
                validated_variants.append({
                    **variant_dict,
                    'validation': {
                        'is_valid': False,
                        'error': 'Keine Text-Variante generiert'
                    }
                })
                continue

            validation = validate_segment(original, variant_text, domain)

            validated_variants.append({
                **variant_dict,
                'validation': validation
            })

        valid_count = sum(
            1 for v in validated_variants
            if v.get('validation', {}).get('is_valid')
        )

        logger.info(f"[OK] {valid_count}/{len(variants)} Varianten bestanden Validierung")

        return {
            'validated_variants': validated_variants,
            'statistics': {
                'total': len(variants),
                'valid': valid_count,
                'invalid': len(variants) - valid_count,
                'validation_rate': valid_count / len(variants) if len(variants) > 0 else 0
            },
            'domain': domain,
            'success': True
        }

    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke Methode

        Args:
            input_data: Dict mit 'original', 'variants', 'domain'

        Returns:
            Dict mit validation results
        """
        original = input_data.get('original', '')
        variants = input_data.get('variants', [])
        domain = input_data.get('domain', 'general')

        return self.validate_variants(original, variants, domain)


def get_validation_chain() -> ValidationChain:
    """Factory für ValidationChain"""
    return ValidationChain()
