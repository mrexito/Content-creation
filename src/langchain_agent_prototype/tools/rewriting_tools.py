"""
Gemeinsame @tool Definitionen für den LangChain Agent Prototyp.

Diese drei Tools werden von beiden Varianten (Orchestrator + Multi-Agent)
geteilt — kein Code-Duplikat.

Alle Tools geben str zurück, da AgentExecutor String-Outputs von Tools erwartet.
Exceptions werden intern abgefangen und als JSON-Fehler zurückgegeben.
"""
import json

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common.constants import DOMAIN_LANGUAGES
from common.logger import setup_logger
from common.utils import extract_json
from common.validators import validate_segment
from langchain_prototype.lcel_llm import get_lcel_llm
from langchain_prototype.prompts.classification_prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    CLASSIFICATION_USER_PROMPT_TEMPLATE,
)
from langchain_prototype.prompts.rewriting_prompts import (
    REWRITING_MATH_SYSTEM_PROMPT,
    REWRITING_LANGUAGES_SYSTEM_PROMPT,
    REWRITING_ECONOMICS_SYSTEM_PROMPT,
    REWRITING_GENERAL_SYSTEM_PROMPT,
    REWRITING_USER_PROMPT_TEMPLATE,
)

logger = setup_logger(__name__)

# Domain → System-Prompt
_REWRITING_PROMPTS = {
    "mathematics": REWRITING_MATH_SYSTEM_PROMPT,
    "languages": REWRITING_LANGUAGES_SYSTEM_PROMPT,
    "economics": REWRITING_ECONOMICS_SYSTEM_PROMPT,
    "general": REWRITING_GENERAL_SYSTEM_PROMPT,
}


# ---------------------------------------------------------------------------
# TOOL 1: classify_segment
# ---------------------------------------------------------------------------

@tool
def classify_segment(text: str) -> str:
    """Klassifiziert ein Textsegment nach Domain und Typ.

    Gibt JSON zurück:
    {"domain": "mathematics|languages|economics|general",
     "content_type": "task|theory|example|solution",
     "confidence": 0.0-1.0}

    Args:
        text: Das zu klassifizierende Textsegment.
    """
    logger.debug(f"[Tool] classify_segment ({len(text)} Zeichen)")
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ])
        llm = get_lcel_llm(temperature=0.1)
        chain = prompt | llm | StrOutputParser()

        raw = chain.invoke({
            "system_prompt": CLASSIFICATION_SYSTEM_PROMPT,
            "user_prompt": CLASSIFICATION_USER_PROMPT_TEMPLATE.format(text=text),
        })
        result = extract_json(raw)
        logger.debug(
            f"[Tool] classify_segment → {result.get('domain')} / "
            f"{result.get('content_type')} ({result.get('confidence', 0):.2f})"
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.exception(f"[Tool] classify_segment Fehler: {e}")
        return json.dumps({"error": str(e), "domain": "general",
                           "content_type": "task", "confidence": 0.0})


# ---------------------------------------------------------------------------
# TOOL 2: rewrite_segment
# ---------------------------------------------------------------------------

@tool
def rewrite_segment(text: str, domain: str, hint: str = "") -> str:
    """Generiert eine Textvariante für das gegebene Segment.

    Args:
        text:   Das zu variierende Textsegment.
        domain: mathematics | languages | economics | general
        hint:   Optionaler Hinweis bei Retry
                (z.B. 'Stelle sicher dass Gleichung lösbar ist').
    """
    logger.debug(f"[Tool] rewrite_segment (domain={domain}, hint={hint!r})")
    try:
        system_prompt = _REWRITING_PROMPTS.get(domain, REWRITING_GENERAL_SYSTEM_PROMPT)

        # Temperature-Paradox:
        #   languages → 0.7 (BERTScore erfordert semantische Nähe)
        #   andere    → 0.9 (mehr Kreativität für Diversität)
        temperature = 0.7 if domain == DOMAIN_LANGUAGES else 0.9

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ])
        llm = get_lcel_llm(temperature=temperature)
        chain = prompt | llm | StrOutputParser()

        user_prompt = REWRITING_USER_PROMPT_TEMPLATE.format(text=text)
        if hint:
            user_prompt += f"\n\nHinweis für diese Variante: {hint}"

        variant = chain.invoke({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }).strip()

        logger.debug(f"[Tool] rewrite_segment → {len(variant)} Zeichen")
        return variant

    except Exception as e:
        logger.exception(f"[Tool] rewrite_segment Fehler: {e}")
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# TOOL 3: validate_variant
# ---------------------------------------------------------------------------

@tool
def validate_variant(original: str, variant: str, domain: str) -> str:
    """Validiert eine Variante gegenüber dem Original.

    Gibt JSON zurück:
    {"is_valid": true|false,
     "issues": ["..."],
     "score": 0.0-1.0}

    Args:
        original: Originaltext des Segments.
        variant:  Die zu prüfende Variante.
        domain:   mathematics | languages | economics | general
    """
    logger.debug(f"[Tool] validate_variant (domain={domain})")
    try:
        result = validate_segment(original, variant, domain)

        is_valid = result["is_valid"]
        issues = result["issues"]
        score = 1.0 if is_valid else max(0.0, 1.0 - len(issues) * 0.25)

        output = {
            "is_valid": is_valid,
            "issues": issues,
            "score": round(score, 2),
            "details": result.get("validation_results", {}),
        }
        logger.debug(f"[Tool] validate_variant → valid={is_valid}, issues={len(issues)}")
        return json.dumps(output, ensure_ascii=False)

    except Exception as e:
        logger.exception(f"[Tool] validate_variant Fehler: {e}")
        return json.dumps({"is_valid": False, "issues": [str(e)], "score": 0.0})
