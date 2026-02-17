"""
Segmentation Chain: Text → Abschnitte
Nutzt LLM für intelligente Segmentierung
"""
from typing import Dict, Any, List
import json

from common.llm_handler import get_llm_handler
from common.logger import setup_logger
from langchain_prototype.prompts.segmentation_prompts import (
    SEGMENTATION_SYSTEM_PROMPT,
    SEGMENTATION_USER_PROMPT_TEMPLATE
)

logger = setup_logger(__name__)


class SegmentationChain:
    """
    Chain für Text-Segmentierung
    """
    
    def __init__(self):
        """Initialisiert die Segmentation Chain"""
        self.llm = get_llm_handler()
        logger.info("SegmentationChain initialisiert")
    
    def segment_text(self, text: str) -> Dict[str, Any]:
        """
        Segmentiert Text in Abschnitte
        
        Args:
            text: Zu segmentierender Text
        
        Returns:
            Dict mit segments, metadata, success
        """
        logger.info(f"Segmentiere Text ({len(text)} Zeichen)")
        
        # Prompt zusammenbauen
        user_prompt = SEGMENTATION_USER_PROMPT_TEMPLATE.format(text=text)
        
        # LLM aufrufen (strukturiertes JSON)
        result = self.llm.generate_structured(
            prompt=user_prompt,
            response_format={
                "segments": [
                    {"type": "string", "text": "string"}
                ]
            },
            system_prompt=SEGMENTATION_SYSTEM_PROMPT
        )
        
        if not result['success']:
            logger.error(f"Segmentierung fehlgeschlagen: {result.get('error')}")
            return {
                'segments': [],
                'metadata': {
                    'success': False,
                    'error': result.get('error')
                },
                'success': False
            }
        
        # Parse Segments
        segments = result['parsed_data'].get('segments', [])
        
        logger.info(f"Segmentierung erfolgreich: {len(segments)} Abschnitte")
        
        return {
            'segments': segments,
            'metadata': {
                'num_segments': len(segments),
                'model': result.get('model'),
                'provider': result.get('provider'),
                'success': True
            },
            'success': True
        }
    
    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke Methode
        
        Args:
            input_data: Dict mit 'text' key
        
        Returns:
            Dict mit segmentation results
        """
        text = input_data.get('text', '')
        return self.segment_text(text)


def get_segmentation_chain() -> SegmentationChain:
    """Factory für SegmentationChain"""
    return SegmentationChain()