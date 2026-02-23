"""
Validation Chain: Varianten → Validated Variants
Nutzt domain-spezifische Validators
"""
from typing import Dict, Any, List

from common.validators import (
    get_sympy_validator,
    get_bert_validator,
    get_consistency_validator
)
from common.logger import setup_logger

logger = setup_logger(__name__)


class ValidationChain:
    """
    Chain für Varianten-Validierung mit domain-spezifischen Validators
    """
    
    def __init__(self):
        """Initialisiert alle Validators"""
        self.sympy_validator = get_sympy_validator()
        self.bert_validator = get_bert_validator()
        self.consistency_validator = get_consistency_validator()
        logger.info("ValidationChain initialisiert")
    
    def validate_variant(
        self,
        original: str,
        variant: str,
        domain: str = 'general'
    ) -> Dict[str, Any]:
        """
        Validiert eine Variante
        
        Args:
            original: Original-Text
            variant: Variante
            domain: Domain (mathematics, languages, economics, general)
        
        Returns:
            Dict mit validation_results, is_valid, issues
        """
        validation_results = {}
        issues = []
        
        # Domain-spezifische Validierung
        if domain == 'mathematics':
            # SymPy Validierung
            logger.debug("Validiere Mathematik-Inhalt mit SymPy")
            
            # Extrahiere Gleichungen
            original_validation = self.sympy_validator.validate_text(original)
            variant_validation = self.sympy_validator.validate_text(variant)
            
            validation_results['sympy'] = {
                'original_equations': original_validation['equations_found'],
                'variant_equations': variant_validation['equations_found'],
                'original_solvable': original_validation['solvable_equations'],
                'variant_solvable': variant_validation['solvable_equations']
            }
            
            # Prüfe ob Anzahl gleich
            if original_validation['equations_found'] != variant_validation['equations_found']:
                issues.append(
                    f"Anzahl Gleichungen unterschiedlich: "
                    f"{original_validation['equations_found']} vs {variant_validation['equations_found']}"
                )
        
        elif domain == 'languages':
            # BERT Validierung (semantische Ähnlichkeit)
            logger.debug("Validiere Sprachwissenschaft-Inhalt mit BERT")
            
            bert_result = self.bert_validator.validate_paraphrase(
                original=original,
                paraphrased=variant,
                min_threshold=0.7  # Etwas niedriger für Variationen
            )
            
            validation_results['bert'] = {
                'score': bert_result['score'],
                'is_valid': bert_result['is_valid'],
                'details': bert_result.get('details', {})
            }
            
            if not bert_result['is_valid']:
                issues.append(bert_result.get('reason', 'Semantische Ähnlichkeit zu gering'))
        
        elif domain == 'economics':
            # Consistency Validierung (Zahlen)
            logger.debug("Validiere Wirtschaft-Inhalt mit Consistency Validator")
            
            # Extrahiere Zahlen
            original_numbers = self.consistency_validator.extract_numbers(original)
            variant_numbers = self.consistency_validator.extract_numbers(variant)
            
            validation_results['consistency'] = {
                'original_numbers': original_numbers,
                'variant_numbers': variant_numbers,
                'num_original': len(original_numbers),
                'num_variant': len(variant_numbers)
            }
            
            # Prüfe ob ähnliche Anzahl Zahlen
            if abs(len(original_numbers) - len(variant_numbers)) > 2:
                issues.append(
                    f"Anzahl Zahlen stark unterschiedlich: "
                    f"{len(original_numbers)} vs {len(variant_numbers)}"
                )
        
        # Generelle Validierung (für alle Domains)
        # Längen-Check (sollte nicht zu stark abweichen)
        length_ratio = len(variant) / len(original) if len(original) > 0 else 0
        
        if length_ratio < 0.5 or length_ratio > 2.0:
            issues.append(
                f"Länge weicht stark ab: {len(variant)} vs {len(original)} Zeichen "
                f"(Ratio: {length_ratio:.2f})"
            )
        
        validation_results['length_check'] = {
            'original_length': len(original),
            'variant_length': len(variant),
            'ratio': length_ratio
        }
        
        # Gesamt-Validierung
        is_valid = len(issues) == 0
        
        return {
            'is_valid': is_valid,
            'validation_results': validation_results,
            'issues': issues,
            'domain': domain
        }
    
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
                # Überspringe fehlerhafte Varianten
                validated_variants.append({
                    **variant_dict,
                    'validation': {
                        'is_valid': False,
                        'error': 'Keine Text-Variante generiert'
                    }
                })
                continue
            
            # Validiere
            validation = self.validate_variant(original, variant_text, domain)
            
            validated_variants.append({
                **variant_dict,
                'validation': validation
            })
        
        # Statistik
        valid_count = sum(1 for v in validated_variants if v.get('validation', {}).get('is_valid'))
        
        logger.info(f"✓ {valid_count}/{len(variants)} Varianten bestanden Validierung")
        
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