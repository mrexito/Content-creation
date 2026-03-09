"""
BERT Validator für semantische Ähnlichkeit
Nutzt BERTScore für Text-Vergleiche
"""
from typing import Any, Dict, List
from bert_score import score
import torch

from ..constants import BERT_THRESHOLD
from ..logger import setup_logger

logger = setup_logger(__name__)

class BERTValidator:
    """
    Validator für semantische Textähnlichkeit mit BERTScore
    """
    
    def __init__(self, model_type: str = 'bert-base-multilingual-cased', device: str = None):
        """
        Args:
            model_type: BERT-Modell zu verwenden
            device: 'cuda', 'cpu', oder None (auto)
        """
        self.model_type = model_type
        
        # Auto-detect device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        logger.info(f"BERT Validator initialisiert (Model: {model_type}, Device: {self.device})")
    
    def calculate_similarity(
        self, 
        candidate: str, 
        reference: str,
        lang: str = 'de'
    ) -> Dict[str, float]:
        """
        Berechnet BERTScore zwischen zwei Texten
        
        Args:
            candidate: Der zu prüfende Text (generierte Variante)
            reference: Der Referenz-Text (Original)
            lang: Sprache ('de', 'en', 'multi')
        
        Returns:
            Dict mit precision, recall, f1
        """
        try:
            # BERTScore berechnen
            P, R, F1 = score(
                [candidate],
                [reference],
                model_type=self.model_type,
                lang=lang,
                device=self.device,
                verbose=False
            )
            
            return {
                'precision': float(P[0]),
                'recall': float(R[0]),
                'f1': float(F1[0]),
            }
            
        except Exception as e:
            logger.error(f"Fehler bei BERTScore-Berechnung: {e}")
            return {
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0,
                'threshold_passed': False,
                'error': str(e)
            }
    
    def calculate_batch_similarity(
        self,
        candidates: List[str],
        references: List[str],
        lang: str = 'de'
    ) -> List[Dict[str, float]]:
        """
        Berechnet BERTScore für mehrere Text-Paare
        
        Returns:
            Liste von Dicts mit scores
        """
        if len(candidates) != len(references):
            raise ValueError("candidates und references müssen gleich lang sein")
        
        try:
            P, R, F1 = score(
                candidates,
                references,
                model_type=self.model_type,
                lang=lang,
                device=self.device,
                verbose=False
            )
            
            results = []
            for i in range(len(candidates)):
                results.append({
                    'precision': float(P[i]),
                    'recall': float(R[i]),
                    'f1': float(F1[i]),
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei Batch-BERTScore: {e}")
            return [{'error': str(e)} for _ in candidates]
    
    def validate_paraphrase(
        self,
        original: str,
        paraphrased: str,
        min_threshold: float = BERT_THRESHOLD
    ) -> Dict[str, Any]:
        """
        Prüft ob eine Paraphrase semantisch äquivalent ist
        
        Args:
            original: Original-Text
            paraphrased: Paraphrasierter Text
            min_threshold: Minimale F1-Score (0-1)
        
        Returns:
            Dict mit is_valid, score, reason
        """
        score_dict = self.calculate_similarity(paraphrased, original)
        
        f1_score = score_dict['f1']
        is_valid = f1_score >= min_threshold
        
        result = {
            'is_valid': is_valid,
            'score': f1_score,
            'details': score_dict
        }
        
        if not is_valid:
            result['reason'] = f'BERTScore {f1_score:.3f} unter Schwellwert {min_threshold}'
        
        return result


# Singleton
_bert_validator = None

def get_bert_validator() -> BERTValidator:
    """Gibt Singleton-Instanz zurück"""
    global _bert_validator
    if _bert_validator is None:
        _bert_validator = BERTValidator()
    return _bert_validator