"""
Segmentation Chain: Text → Abschnitte

LCEL-Implementierung:
    ChatPromptTemplate | ChatOpenAI | StrOutputParser
    (+ manuelles JSON-Parsing via _extract_json)
"""
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common.logger import setup_logger
from common.utils import extract_json as _extract_json
from langchain_prototype.lcel_llm import get_lcel_llm
from langchain_prototype.prompts.segmentation_prompts import (
    SEGMENTATION_SYSTEM_PROMPT,
    SEGMENTATION_USER_PROMPT_TEMPLATE,
)

logger = setup_logger(__name__)


class SegmentationChain:
    """
    LCEL-Chain für Text-Segmentierung.

    Chain-Komposition (LCEL-Pattern):
        prompt | llm | parser
    """

    def __init__(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ])
        llm = get_lcel_llm(temperature=0.3)
        parser = StrOutputParser()

        # LCEL-Chain via |-Operator (LangChain Expression Language)
        self._chain = prompt | llm | parser

        logger.info("SegmentationChain (LCEL) initialisiert")

    def segment_text(self, text: str) -> Dict[str, Any]:
        """
        Segmentiert Text in Abschnitte.

        Args:
            text: Zu segmentierender Text

        Returns:
            Dict mit segments, metadata, success
        """
        logger.info(f"Segmentiere Text ({len(text)} Zeichen)")

        user_prompt = SEGMENTATION_USER_PROMPT_TEMPLATE.format(text=text)

        try:
            raw = self._chain.invoke({
                "system_prompt": SEGMENTATION_SYSTEM_PROMPT,
                "user_prompt": user_prompt,
            })
            parsed = _extract_json(raw)
            segments = parsed.get("segments", [])
        except Exception as e:
            logger.exception(f"Segmentierung fehlgeschlagen: {e}")
            return {
                "segments": [],
                "metadata": {"success": False, "error": str(e)},
                "success": False,
            }

        logger.info(f"Segmentierung erfolgreich: {len(segments)} Abschnitte")
        logger.debug(f"Segmentierung: {len(segments)} Segmente aus {len(text)} Zeichen")

        return {
            "segments": segments,
            "metadata": {
                "num_segments": len(segments),
                "success": True,
            },
            "success": True,
        }

    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke-Methode.

        Args:
            input_data: Dict mit 'text' key

        Returns:
            Dict mit segmentation results
        """
        return self.segment_text(input_data.get("text", ""))


def get_segmentation_chain() -> SegmentationChain:
    """Factory für SegmentationChain"""
    return SegmentationChain()
