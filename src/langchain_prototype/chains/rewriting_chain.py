"""
Rewriting Chain: Original → Varianten

LCEL-Implementierung:
    ChatPromptTemplate | ChatOpenAI | StrOutputParser

Der Diversity-Mechanismus (Similarity-Check, Retry-Schleife) und das
Temperature-Paradox für Languages bleiben erhalten.  Für jeden Versuch
wird eine neue LCEL-Chain mit der passenden Temperature aufgebaut, da
die Temperature bei Languages konstant (0.7) bleibt, bei anderen Domains
aber mit jedem Retry steigt.
"""
from typing import Dict, Any, List
from difflib import SequenceMatcher

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
    LCEL-Chain für Content-Variation mit Diversity-Mechanismus.

    Für jede Variante:
    1. LCEL-Chain aufrufen (prompt | llm | parser)
    2. Similarity gegen bestehende Varianten prüfen
    3. Bei zu grosser Ähnlichkeit: Retry mit erhöhter Temperature
       (ausgenommen Domain 'languages' — Temperature-Paradox)
    """

    # Domain → System-Prompt
    DOMAIN_PROMPTS = {
        "mathematics": REWRITING_MATH_SYSTEM_PROMPT,
        "languages": REWRITING_LANGUAGES_SYSTEM_PROMPT,
        "economics": REWRITING_ECONOMICS_SYSTEM_PROMPT,
        "general": REWRITING_GENERAL_SYSTEM_PROMPT,
    }

    def __init__(
        self,
        num_variants: int = 3,
        min_similarity_threshold: float = 0.7,
        max_attempts_per_variant: int = 3,
    ):
        """
        Args:
            num_variants:             Anzahl zu generierender Varianten
            min_similarity_threshold: Schwellwert für "zu ähnlich" (0–1)
            max_attempts_per_variant: Max Versuche pro Variante
        """
        self.num_variants = num_variants
        self.min_similarity_threshold = min_similarity_threshold
        self.max_attempts_per_variant = max_attempts_per_variant

        logger.info(
            f"RewritingChain (LCEL) initialisiert "
            f"(Varianten: {num_variants}, Similarity-Threshold: {min_similarity_threshold})"
        )

    # ------------------------------------------------------------------
    # Hilfsmethoden (unverändert)
    # ------------------------------------------------------------------

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Berechnet Text-Ähnlichkeit (0–1)."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _is_too_similar(self, new_variant: str, existing_variants: List[str]) -> bool:
        """True wenn neue Variante zu ähnlich zu einer bestehenden ist."""
        for existing in existing_variants:
            similarity = self._calculate_similarity(new_variant, existing)
            if similarity >= self.min_similarity_threshold:
                logger.debug(
                    f"Variante zu ähnlich: {similarity:.2f} >= "
                    f"{self.min_similarity_threshold}"
                )
                return True
        return False

    # ------------------------------------------------------------------
    # Haupt-Logik
    # ------------------------------------------------------------------

    def rewrite_segment(
        self,
        segment: Dict,
        domain: str = "general",
    ) -> Dict[str, Any]:
        """
        Generiert diverse Varianten eines Segments.

        Args:
            segment: Dict mit 'text' und optional 'type'
            domain:  Domain des Contents

        Returns:
            Dict mit variants, metadata, success
        """
        text = segment.get("text", "")
        logger.info(f"Generiere {self.num_variants} diverse Varianten für {domain}-Segment")

        system_prompt = self.DOMAIN_PROMPTS.get(domain, REWRITING_GENERAL_SYSTEM_PROMPT)

        variants: List[Dict] = []
        variant_texts: List[str] = []  # Für Similarity-Check

        for i in range(self.num_variants):
            logger.debug(f"  Generiere Variante {i + 1}/{self.num_variants}")

            attempt = 0
            success = False

            while attempt < self.max_attempts_per_variant and not success:
                attempt += 1

                # User-Prompt mit Kontext bisheriger Varianten
                if variant_texts:
                    user_prompt = (
                        f"{REWRITING_USER_PROMPT_TEMPLATE.format(text=text)}\n\n"
                        f"WICHTIG: Du hast bereits folgende Varianten erstellt:\n"
                    )
                    for idx, prev in enumerate(variant_texts, 1):
                        user_prompt += f"{idx}. {prev}\n"
                    user_prompt += "\nErstelle eine DEUTLICH UNTERSCHIEDLICHE Variante!"
                else:
                    user_prompt = REWRITING_USER_PROMPT_TEMPLATE.format(text=text)

                # Temperature-Paradox:
                # Languages: konstant 0.7 (BERTScore erfordert semantische Nähe)
                # Andere Domains: steigt mit jedem Retry für mehr Diversität
                if domain == DOMAIN_LANGUAGES:
                    temperature = 0.7
                else:
                    temperature = 0.9 + (attempt * 0.05)

                # LCEL-Chain mit passender Temperature aufbauen
                chain = _build_rewriting_chain(temperature)

                try:
                    new_variant = chain.invoke({
                        "system_prompt": system_prompt,
                        "user_prompt": user_prompt,
                    }).strip()
                except Exception as e:
                    logger.warning(f"    Versuch {attempt} fehlgeschlagen: {e}")
                    continue

                if not new_variant:
                    logger.warning(f"    Versuch {attempt}: Leere Antwort")
                    continue

                # Similarity-Check
                if self._is_too_similar(new_variant, variant_texts):
                    logger.debug(
                        f"    Versuch {attempt}: Variante zu ähnlich, versuche erneut"
                    )
                    continue

                # Variante akzeptiert
                variant_texts.append(new_variant)
                variants.append({
                    "variant_id": i + 1,
                    "text": new_variant,
                    "attempts": attempt,
                })
                success = True
                logger.debug(f"    ✓ Variante {i + 1} akzeptiert (Versuch {attempt})")

            if not success:
                logger.warning(
                    f"  ✗ Variante {i + 1}: Keine diverse Variante nach "
                    f"{self.max_attempts_per_variant} Versuchen"
                )
                variants.append({
                    "variant_id": i + 1,
                    "text": None,
                    "error": f"Keine diverse Variante nach {self.max_attempts_per_variant} Versuchen",
                    "attempts": self.max_attempts_per_variant,
                })

        successful_variants = [v for v in variants if v.get("text")]

        # Diversity-Score
        diversity_score = None
        if len(successful_variants) >= 2:
            similarities = [
                self._calculate_similarity(
                    successful_variants[a]["text"],
                    successful_variants[b]["text"],
                )
                for a in range(len(successful_variants))
                for b in range(a + 1, len(successful_variants))
            ]
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            diversity_score = 1.0 - avg_similarity

        diversity_str = f"{diversity_score:.2f}" if diversity_score is not None else "N/A"
        logger.info(
            f"✓ {len(successful_variants)}/{self.num_variants} Varianten erfolgreich "
            f"(Diversity-Score: {diversity_str})"
        )

        return {
            "original": text,
            "variants": variants,
            "domain": domain,
            "metadata": {
                "num_requested": self.num_variants,
                "num_successful": len(successful_variants),
                "segment_type": segment.get("type"),
                "diversity_score": diversity_score,
                "avg_attempts": (
                    sum(v.get("attempts", 0) for v in variants) / len(variants)
                    if variants else 0
                ),
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


def get_rewriting_chain(
    num_variants: int = 3,
    min_similarity_threshold: float = 0.7,
) -> RewritingChain:
    """Factory für RewritingChain"""
    return RewritingChain(
        num_variants=num_variants,
        min_similarity_threshold=min_similarity_threshold,
    )
