"""
Gemeinsame @tool Definitionen für den LangChain Agent Prototyp.

Diese drei Tools werden von beiden Varianten (Orchestrator + Multi-Agent)
geteilt — kein Code-Duplikat.

Alle Tools geben str zurück, da AgentExecutor String-Outputs von Tools erwartet.
Exceptions werden intern abgefangen und als JSON-Fehler zurückgegeben.
"""
import json
from typing import Optional

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common.constants import DOMAIN_LANGUAGES
from common.logger import setup_logger
from common.validators.sympy_validator import get_sympy_validator
from common.validators.bert_validator import BERTValidator
from common.validators.consistency_validator import ConsistencyValidator
from langchain_prototype.lcel_llm import get_lcel_llm, _extract_json
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

# ---------------------------------------------------------------------------
# Interne Hilfsobjekte (lazy-initialisiert)
# ---------------------------------------------------------------------------

_sympy_validator = None
_bert_validator = None
_consistency_validator = None


def _get_sympy():
    global _sympy_validator
    if _sympy_validator is None:
        _sympy_validator = get_sympy_validator()
    return _sympy_validator


def _get_bert():
    global _bert_validator
    if _bert_validator is None:
        _bert_validator = BERTValidator()
    return _bert_validator


def _get_consistency():
    global _consistency_validator
    if _consistency_validator is None:
        _consistency_validator = ConsistencyValidator()
    return _consistency_validator


# Placeholder-Zeichen für Languages-Validierung
_PLACEHOLDERS = ["□", "___", "→ ___", "→___", "________"]

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
        result = _extract_json(raw)
        logger.debug(
            f"[Tool] classify_segment → {result.get('domain')} / "
            f"{result.get('content_type')} ({result.get('confidence', 0):.2f})"
        )
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"[Tool] classify_segment Fehler: {e}")
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
        logger.error(f"[Tool] rewrite_segment Fehler: {e}")
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
        issues = []
        validation_details = {}

        # --- Domain-spezifische Validierung ---
        if domain == "mathematics":
            sympy = _get_sympy()
            orig_v = sympy.validate_text(original)
            var_v = sympy.validate_text(variant)
            validation_details["equations_original"] = orig_v["equations_found"]
            validation_details["equations_variant"] = var_v["equations_found"]
            if orig_v["equations_found"] != var_v["equations_found"]:
                issues.append(
                    f"Anzahl Gleichungen unterschiedlich: "
                    f"{orig_v['equations_found']} vs {var_v['equations_found']}"
                )

        elif domain == "languages":
            bert = _get_bert()
            bert_result = bert.validate_paraphrase(
                original=original, paraphrased=variant, min_threshold=0.7
            )
            validation_details["bert_score"] = bert_result.get("score", 0)
            if not bert_result["is_valid"]:
                issues.append(bert_result.get("reason", "Semantische Ähnlichkeit zu gering"))

            # Placeholder-Erhalt prüfen
            orig_count = sum(original.count(p) for p in _PLACEHOLDERS)
            var_count = sum(variant.count(p) for p in _PLACEHOLDERS)
            if orig_count > 0:
                ratio = var_count / orig_count
                validation_details["placeholder_ratio"] = ratio
                if ratio < 0.8:
                    issues.append(
                        f"Platzhalter nicht erhalten: {var_count}/{orig_count} "
                        f"(min. 80% erforderlich)"
                    )

        elif domain == "economics":
            cons = _get_consistency()
            orig_nums = cons.extract_numbers(original)
            var_nums = cons.extract_numbers(variant)
            validation_details["numbers_original"] = len(orig_nums)
            validation_details["numbers_variant"] = len(var_nums)
            if abs(len(orig_nums) - len(var_nums)) > 2:
                issues.append(
                    f"Anzahl Zahlen stark unterschiedlich: "
                    f"{len(orig_nums)} vs {len(var_nums)}"
                )

        # --- Längen-Check (alle Domains) ---
        if len(original) > 0:
            ratio = len(variant) / len(original)
            validation_details["length_ratio"] = round(ratio, 2)
            if domain == "languages":
                min_r, max_r = 0.6, 1.5
            elif domain == "economics":
                min_r, max_r = 0.4, 2.5
            else:
                min_r, max_r = 0.5, 2.0
            if ratio < min_r or ratio > max_r:
                issues.append(
                    f"Länge weicht stark ab: {len(variant)} vs {len(original)} "
                    f"(Ratio {ratio:.2f}, erlaubt {min_r}–{max_r})"
                )

        is_valid = len(issues) == 0
        score = 1.0 if is_valid else max(0.0, 1.0 - len(issues) * 0.25)

        result = {
            "is_valid": is_valid,
            "issues": issues,
            "score": round(score, 2),
            "details": validation_details,
        }
        logger.debug(f"[Tool] validate_variant → valid={is_valid}, issues={len(issues)}")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"[Tool] validate_variant Fehler: {e}")
        return json.dumps({"is_valid": False, "issues": [str(e)], "score": 0.0})
