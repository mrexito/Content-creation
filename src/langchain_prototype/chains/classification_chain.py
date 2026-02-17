"""
Classification Chain: Abschnitt → Domain/Type
"""
from typing import Dict, Any

from common.llm_handler import get_llm_handler
from common.logger import setup_logger
from langchain_prototype.prompts.classification_prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    CLASSIFICATION_USER_PROMPT_TEMPLATE
)

logger = setup_logger(__name__)


class ClassificationChain:
    """
    Chain für Segment-Klassifizierung
    """
    
    def __init__(self):
        """Initialisiert die Classification Chain"""
        self.llm = get_llm_handler()
        logger.info("ClassificationChain initialisiert")
    
    def classify_segment(self, segment: Dict) -> Dict[str, Any]:
        """
        Klassifiziert ein Segment
        
        Args:
            segment: Dict mit 'text' und optional 'type'
        
        Returns:
            Dict mit classification, metadata, success
        """
        text = segment.get('text', '')
        logger.info(f"Klassifiziere Segment ({len(text)} Zeichen)")
        
        # Prompt
        user_prompt = CLASSIFICATION_USER_PROMPT_TEMPLATE.format(text=text)
        
        # LLM aufrufen
        result = self.llm.generate_structured(
            prompt=user_prompt,
            response_format={
                "domain": "string",
                "content_type": "string",
                "confidence": "number"
            },
            system_prompt=CLASSIFICATION_SYSTEM_PROMPT
        )
        
        if not result['success']:
            logger.error(f"Klassifizierung fehlgeschlagen: {result.get('error')}")
            return {
                'classification': None,
                'success': False,
                'error': result.get('error')
            }
        
        classification = result['parsed_data']
        
        logger.info(
            f"Klassifiziert als: {classification.get('domain')} / "
            f"{classification.get('content_type')} "
            f"(Confidence: {classification.get('confidence', 0):.2f})"
        )
        
        return {
            'classification': classification,
            'original_segment': segment,
            'metadata': {
                'model': result.get('model'),
                'provider': result.get('provider')
            },
            'success': True
        }
    
    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke Methode
        
        Args:
            input_data: Dict mit 'segment' key
        
        Returns:
            Dict mit classification results
        """
        segment = input_data.get('segment', {})
        return self.classify_segment(segment)


def get_classification_chain() -> ClassificationChain:
    """Factory für ClassificationChain"""
    return ClassificationChain()