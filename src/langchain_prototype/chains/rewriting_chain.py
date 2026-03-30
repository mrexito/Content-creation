"""
Rewriting Chain: Original → Varianten

LCEL-Implementierung:
    ChatPromptTemplate | ChatOpenAI | StrOutputParser

Strikte lineare Pipeline: Pro Variante genau ein LLM-Aufruf.
Keine Retry-Schleife, kein Similarity-Check.
Temperature: Languages = 0.7 (BERTScore), alle anderen Domains = 0.9.
"""
from typing import Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from common.constants import DOMAIN_LANGUAGES
from common.logger import setup_logger
from langchain_prototype.lcel_llm import get_lcel_llm
from langchain_prototype.prompts.rewriting_prompts import (
    REWRITING_MATH_SYSTEM_PROMPT,
    REWRITING_LANGUAGES_SYSTEM_PROMPT,
    REWRITING_ECONOMICS_SYSTEM_PROMPT,
    REWRITING_GENERAL_SYSTEM_PROMPT,
    REWRITING_USER_PROMPT_TEMPLATE,
)

logger = setup_logger(__name__)

# Prompt-Template ist domainunabhängig – wird einmal aufgebaut
_REWRITING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    ("human", "{user_prompt}"),
])


def _build_rewriting_chain(temperature: float) -> Runnable:
    """
    Baut eine LCEL-Chain mit der angegebenen Temperature.

    Pattern: prompt | llm | parser
    Pro Retry-Versuch wird eine neue Instanz erzeugt, da Temperature
    ein Initialisierungsparameter von ChatOpenAI ist.
    """
    llm = get_lcel_llm(temperature=temperature)
    return _REWRITING_PROMPT | llm | StrOutputParser()


class RewritingChain:
    """
    LCEL-Chain für Content-Variation.

    Strikte lineare Pipeline: Pro Variante genau ein LLM-Aufruf.
    Keine Retry-Schleife, kein Similarity-Check.
    """

    # Domain → System-Prompt
    DOMAIN_PROMPTS = {
        "mathematics": REWRITING_MATH_SYSTEM_PROMPT,
        "languages": REWRITING_LANGUAGES_SYSTEM_PROMPT,
        "economics": REWRITING_ECONOMICS_SYSTEM_PROMPT,
        "general": REWRITING_GENERAL_SYSTEM_PROMPT,
    }

    def __init__(self, num_variants: int = 3):
        """
        Args:
            num_variants: Anzahl zu generierender Varianten
        """
        self.num_variants = num_variants
        logger.info(f"RewritingChain (LCEL) initialisiert (Varianten: {num_variants})")

    # ------------------------------------------------------------------
    # Haupt-Logik
    # ------------------------------------------------------------------

    def rewrite_segment(
        self,
        segment: Dict,
        domain: str = "general",
    ) -> Dict[str, Any]:
        """
        Generiert Varianten eines Segments (ein LLM-Aufruf pro Variante).

        Args:
            segment: Dict mit 'text' und optional 'type'
            domain:  Domain des Contents

        Returns:
            Dict mit variants, metadata, success
        """
        text = segment.get("text", "")
        logger.info(f"Generiere {self.num_variants} Varianten für {domain}-Segment")

        system_prompt = self.DOMAIN_PROMPTS.get(domain, REWRITING_GENERAL_SYSTEM_PROMPT)

        # Temperature: Languages = 0.7 (BERTScore), alle anderen = 0.9
        temperature = 0.7 if domain == DOMAIN_LANGUAGES else 0.9
        chain = _build_rewriting_chain(temperature)
        user_prompt = REWRITING_USER_PROMPT_TEMPLATE.format(text=text)

        variants: List[Dict] = []

        for i in range(self.num_variants):
            logger.debug(f"  Generiere Variante {i + 1}/{self.num_variants}")
            try:
                new_variant = chain.invoke({
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                }).strip()
                variants.append({
                    "variant_id": i + 1,
                    "text": new_variant if new_variant else None,
                    "attempts": 1,
                })
                logger.debug(f"    [OK] Variante {i + 1} generiert")
            except Exception as e:
                logger.warning(f"    Variante {i + 1} fehlgeschlagen: {e}")
                variants.append({
                    "variant_id": i + 1,
                    "text": None,
                    "error": str(e),
                    "attempts": 1,
                })

        successful_variants = [v for v in variants if v.get("text")]

        logger.info(f"[OK] {len(successful_variants)}/{self.num_variants} Varianten erfolgreich")

        return {
            "original": text,
            "variants": variants,
            "domain": domain,
            "metadata": {
                "num_requested": self.num_variants,
                "num_successful": len(successful_variants),
                "segment_type": segment.get("type"),
                "diversity_score": None,
                "avg_attempts": 1,
            },
            "success": len(successful_variants) > 0,
        }

    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke-Methode.

        Args:
            input_data: Dict mit 'segment' und 'domain'

        Returns:
            Dict mit rewriting results
        """
        segment = input_data.get("segment", {})
        domain = input_data.get("domain", "general")
        return self.rewrite_segment(segment, domain)


def get_rewriting_chain(num_variants: int = 3) -> RewritingChain:
    """Factory für RewritingChain"""
    return RewritingChain(num_variants=num_variants)
