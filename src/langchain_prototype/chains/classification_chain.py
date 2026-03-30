"""
Classification Chain: Abschnitt → Domain/Type

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
from langchain_prototype.prompts.classification_prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    CLASSIFICATION_USER_PROMPT_TEMPLATE,
)

logger = setup_logger(__name__)


class ClassificationChain:
    """
    LCEL-Chain für Segment-Klassifizierung.

    Chain-Komposition (LCEL-Pattern):
        prompt | llm | parser
    """

    def __init__(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ])
        llm = get_lcel_llm(temperature=0.1)
        parser = StrOutputParser()

        # LCEL-Chain via |-Operator (LangChain Expression Language)
        self._chain = prompt | llm | parser

        logger.info("ClassificationChain (LCEL) initialisiert")

    def classify_segment(self, segment: Dict) -> Dict[str, Any]:
        """
        Klassifiziert ein Segment.

        Args:
            segment: Dict mit 'text' und optional 'type'

        Returns:
            Dict mit classification, metadata, success
        """
        text = segment.get("text", "")
        logger.info(f"Klassifiziere Segment ({len(text)} Zeichen)")

        user_prompt = CLASSIFICATION_USER_PROMPT_TEMPLATE.format(text=text)

        try:
            raw = self._chain.invoke({
                "system_prompt": CLASSIFICATION_SYSTEM_PROMPT,
                "user_prompt": user_prompt,
            })
            classification = _extract_json(raw)
        except Exception as e:
            logger.exception(f"Klassifizierung fehlgeschlagen: {e}")
            return {
                "classification": None,
                "success": False,
                "error": str(e),
            }

        logger.info(
            f"Klassifiziert als: {classification.get('domain')} / "
            f"{classification.get('content_type')} "
            f"(Confidence: {classification.get('confidence', 0):.2f})"
        )

        return {
            "classification": classification,
            "original_segment": segment,
            "metadata": {},
            "success": True,
        }

    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke-Methode.

        Args:
            input_data: Dict mit 'segment' key

        Returns:
            Dict mit classification results
        """
        return self.classify_segment(input_data.get("segment", {}))


def get_classification_chain() -> ClassificationChain:
    """Factory für ClassificationChain"""
    return ClassificationChain()
