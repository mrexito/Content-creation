"""
Zentralisierte Segment-Validierungslogik.

Einzige Quelle der Wahrheit für domain-spezifische Validierung aller drei
Prototypen (LangChain, LangGraph, Hybrid). Alle Toleranzen und Schwellwerte
kommen aus common.constants.
"""
from typing import Any, Dict, List

from common.constants import (
    BERT_THRESHOLD,
    DOMAIN_ECONOMICS,
    DOMAIN_LANGUAGES,
    DOMAIN_MATH,
    EQUATION_COUNT_TOLERANCE,
    LENGTH_RATIO_BOUNDS,
    NUMBER_COUNT_TOLERANCE,
)
from common.utils import check_placeholder_preservation
from common.validators.sympy_validator import get_sympy_validator
from common.validators.bert_validator import get_bert_validator
from common.validators.consistency_validator import get_consistency_validator

# Marker-Strings die auf einen Prompt-Leak im LLM-Output hinweisen
_PROMPT_LEAK_MARKERS: List[str] = [
    "Erstelle eine inhaltlich äquivalente",
    "Erstelle ein inhaltlich",
    "DEUTLICH anders formulierte Variante",
    "inhaltlich äquivalente, aber DEUTLICH",
    "anders formulierte Variante",
]


def _has_prompt_leak(text: str) -> bool:
    """Prüft ob der LLM-Output versehentlich den Prompt-Text enthält."""
    return any(marker in text for marker in _PROMPT_LEAK_MARKERS)


def validate_segment(
    original: str,
    variant: str,
    domain: str = "general",
) -> Dict[str, Any]:
    """
    Validiert eine Variante gegen den Original-Text, domain-spezifisch.

    Enthält die kanonische Validierungslogik für alle drei Prototypen.
    Toleranzen und Schwellwerte werden ausschliesslich aus common.constants gelesen.

    Args:
        original: Original-Segment-Text
        variant:  Generierte Variante
        domain:   Domain-String (kanonisch, z.B. DOMAIN_MATH)

    Returns:
        Dict mit:
            is_valid          (bool)
            issues            (List[str])
            validation_results (Dict)  — domain-spezifische Rohdaten
            domain            (str)
    """
    validation_results: Dict[str, Any] = {}
    issues: List[str] = []

    # ── Prompt-Leak-Check ─────────────────────────────────────────────────────
    if _has_prompt_leak(variant):
        return {
            "is_valid": False,
            "issues": ["Prompt-Text im Output erkannt — LLM hat den Eingabe-Prompt ausgegeben"],
            "validation_results": {"prompt_leak": True},
            "domain": domain,
        }

    # ── Domain-spezifische Validierung ────────────────────────────────────────
    if domain == DOMAIN_MATH:
        sympy_validator = get_sympy_validator()
        original_val = sympy_validator.validate_text(original)
        variant_val = sympy_validator.validate_text(variant)

        validation_results["sympy"] = {
            "original_equations": original_val["equations_found"],
            "variant_equations": variant_val["equations_found"],
            "original_solvable": original_val["solvable_equations"],
            "variant_solvable": variant_val["solvable_equations"],
        }

        equation_diff = abs(
            original_val["equations_found"] - variant_val["equations_found"]
        )
        if equation_diff > EQUATION_COUNT_TOLERANCE:
            issues.append(
                f"Anzahl Gleichungen unterschiedlich: "
                f"{original_val['equations_found']} vs {variant_val['equations_found']}"
            )

    elif domain == DOMAIN_LANGUAGES:
        bert_validator = get_bert_validator()
        bert_result = bert_validator.validate_paraphrase(
            original=original,
            paraphrased=variant,
            min_threshold=BERT_THRESHOLD,
        )

        validation_results["bert"] = {
            "score": bert_result["score"],
            "is_valid": bert_result["is_valid"],
            "details": bert_result.get("details", {}),
        }

        if not bert_result["is_valid"]:
            issues.append(bert_result.get("reason", "Semantische Ähnlichkeit zu gering"))

        placeholder_result = check_placeholder_preservation(original, variant)
        validation_results["placeholder"] = placeholder_result

        if not placeholder_result.get("skipped") and not placeholder_result["is_valid"]:
            issues.append(
                f"Platzhalter nicht erhalten: "
                f"{placeholder_result['variant_count']} von "
                f"{placeholder_result['original_count']} Platzhaltern vorhanden "
                f"(min. 80% erforderlich)"
            )

    elif domain == DOMAIN_ECONOMICS:
        consistency_validator = get_consistency_validator()
        original_numbers = consistency_validator.extract_numbers(original)
        variant_numbers = consistency_validator.extract_numbers(variant)

        validation_results["consistency"] = {
            "original_numbers": original_numbers,
            "variant_numbers": variant_numbers,
            "num_original": len(original_numbers),
            "num_variant": len(variant_numbers),
        }

        if abs(len(original_numbers) - len(variant_numbers)) > NUMBER_COUNT_TOLERANCE:
            issues.append(
                f"Anzahl Zahlen stark unterschiedlich: "
                f"{len(original_numbers)} vs {len(variant_numbers)}"
            )

    # ── Längen-Check (alle Domains) ────────────────────────────────────────────
    length_ratio = len(variant) / len(original) if len(original) > 0 else 0.0
    min_ratio, max_ratio = LENGTH_RATIO_BOUNDS.get(domain, LENGTH_RATIO_BOUNDS["default"])

    if length_ratio < min_ratio or length_ratio > max_ratio:
        issues.append(
            f"Länge weicht stark ab: {len(variant)} vs {len(original)} Zeichen "
            f"(Ratio: {length_ratio:.2f}, erlaubt: {min_ratio:.1f}–{max_ratio:.1f})"
        )

    validation_results["length_check"] = {
        "original_length": len(original),
        "variant_length": len(variant),
        "ratio": length_ratio,
    }

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "validation_results": validation_results,
        "domain": domain,
    }
