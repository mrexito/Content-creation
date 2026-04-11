"""
Zentralisierte Segment-Validierungslogik.

Einzige Quelle der Wahrheit für domain-spezifische Validierung aller drei
Prototypen (LangChain, LangGraph, Hybrid). Alle Toleranzen und Schwellwerte
kommen aus common.constants.
"""
import re
from typing import Any, Dict, List

from common.constants import (
    BERT_THRESHOLD,
    DOMAIN_ECONOMICS,
    DOMAIN_LANGUAGES,
    DOMAIN_MATH,
    EQUATION_COUNT_TOLERANCE,
    LENGTH_RATIO_BOUNDS,
    MIN_NUMBER_CHANGE_MATH,
    NUMBER_COUNT_TOLERANCE,
)
from common.logger import setup_logger
from common.utils import check_placeholder_preservation
from common.validators.sympy_validator import get_sympy_validator
from common.validators.bert_validator import get_bert_validator
from common.validators.consistency_validator import get_consistency_validator
from common.llm_handler import get_llm_handler

logger = setup_logger(__name__)

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


def _llm_plausibility_check(
    original: str,
    variant: str,
    domain: str,
) -> Dict[str, Any]:
    """
    LLM-basierter Plausibilitäts-Check für Mathematik und Wirtschaft.

    Vorstudie S. 11 (Tabelle 4): Mathematik — gleiche Lösungsmethode prüfen.
    Vorstudie S. 12 (Tabelle 1): Wirtschaft — betriebswirtschaftliche Regeln prüfen.

    Graceful degradation: Bei LLM-Fehler oder -Ausfall wird is_valid=True
    zurückgegeben und skipped=True gesetzt, damit die Pipeline nicht abbricht.

    Returns:
        Dict mit is_valid (bool), issues (List[str]), skipped (bool),
        und optional reasoning (str).
    """
    if domain == DOMAIN_MATH:
        system_prompt = (
            "Du bist ein Mathematik-Experte. Deine Aufgabe ist es zu prüfen, "
            "ob eine Aufgaben-Variante dieselbe Lösungsmethode wie das Original verwendet. "
            "Erlaubt sind andere Zahlen und Variablen. "
            "Nicht erlaubt sind andere mathematische Operationen, Konzepte oder Strukturen. "
            "Antworte ausschliesslich im vorgegebenen JSON-Format."
        )
        user_prompt = (
            f"Original-Aufgabe:\n{original}\n\n"
            f"Variante:\n{variant}\n\n"
            "Prüfe: Verwendet die Variante dieselbe Lösungsmethode wie das Original? "
            "(z.B. gleiche Gleichungstypen, gleiche Operationen, gleiche Lösungsstruktur)"
        )
    elif domain == DOMAIN_ECONOMICS:
        system_prompt = (
            "Du bist ein Betriebswirtschafts-Experte. Deine Aufgabe ist es zu prüfen, "
            "ob eine Aufgaben-Variante betriebswirtschaftlich plausibel ist. "
            "Prüfe: logische Konsistenz der Zahlen, korrekte Verhältnisse "
            "(z.B. Gewinn < Umsatz), realistische Werte und sinnvolle Umformulierungen. "
            "Antworte ausschliesslich im vorgegebenen JSON-Format."
        )
        user_prompt = (
            f"Original-Aufgabe:\n{original}\n\n"
            f"Variante:\n{variant}\n\n"
            "Prüfe: Ist die Variante betriebswirtschaftlich plausibel und konsistent?"
        )
    else:
        return {"is_valid": True, "issues": [], "skipped": True}

    try:
        llm = get_llm_handler()
        result = llm.generate_structured(
            prompt=user_prompt,
            response_format={"is_valid": True, "issues": [], "reasoning": ""},
            system_prompt=system_prompt,
        )
    except Exception as exc:
        logger.warning(
            f"LLM-Plausibilitäts-Check fehlgeschlagen für domain={domain}: "
            f"{exc} — Check übersprungen"
        )
        return {"is_valid": True, "issues": [], "skipped": True}

    if not result.get("success") or result.get("parsed_data") is None:
        logger.warning(
            f"LLM-Plausibilitäts-Check fehlgeschlagen für domain={domain}: "
            f"{result.get('error', 'unbekannter Fehler')} — Check übersprungen"
        )
        return {"is_valid": True, "issues": [], "skipped": True}

    parsed = result["parsed_data"]
    return {
        "is_valid": bool(parsed.get("is_valid", True)),
        "issues": parsed.get("issues", []),
        "reasoning": parsed.get("reasoning", ""),
        "skipped": False,
    }


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

        # ── Zahlenänderungs-Check (Vorstudie Tabelle 1: ≥ 30 %) ──────────────
        _num_pattern = re.compile(r'\b\d+(?:[.,]\d+)?\b')
        orig_nums = [
            float(n.replace(',', '.'))
            for n in _num_pattern.findall(original)
            if float(n.replace(',', '.')) >= 1.0
        ]
        var_nums = [
            float(n.replace(',', '.'))
            for n in _num_pattern.findall(variant)
            if float(n.replace(',', '.')) >= 1.0
        ]
        if len(orig_nums) >= 2 and len(var_nums) >= 2:
            pairs = list(zip(orig_nums, var_nums))
            changes = [
                abs(o - v) / max(abs(o), 1.0)
                for o, v in pairs
            ]
            avg_change = sum(changes) / len(changes)
            validation_results["sympy"]["avg_number_change"] = round(avg_change, 4)
            if avg_change < MIN_NUMBER_CHANGE_MATH:
                issues.append(
                    f"Zahlenvariation zu gering: Ø {avg_change:.0%} "
                    f"(Minimum: {MIN_NUMBER_CHANGE_MATH:.0%} gemäss Vorstudie)"
                )

        # ── LLM-Plausibilitäts-Check (Vorstudie S. 11, Tabelle 4) ───────────
        llm_check_math = _llm_plausibility_check(original, variant, DOMAIN_MATH)
        validation_results["llm_plausibility"] = llm_check_math
        if not llm_check_math.get("skipped") and not llm_check_math["is_valid"]:
            for issue in llm_check_math.get("issues", []):
                issues.append(f"LLM-Check (Mathematik): {issue}")

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

        # ── BERTScore für narrativen Teil (Vorstudie S. 12 + Anhang c) ───────
        bert_validator_econ = get_bert_validator()
        bert_econ = bert_validator_econ.validate_paraphrase(
            original=original,
            paraphrased=variant,
            min_threshold=BERT_THRESHOLD,
        )
        validation_results["bert_economics"] = {
            "score": bert_econ["score"],
            "is_valid": bert_econ["is_valid"],
        }
        if not bert_econ["is_valid"]:
            issues.append(
                f"Semantische Ähnlichkeit zu gering (Wirtschaft): "
                f"BERTScore {bert_econ['score']:.3f} < {BERT_THRESHOLD}"
            )

        # ── LLM-Plausibilitäts-Check (Vorstudie S. 12, Tabelle 1) ───────────
        llm_check_econ = _llm_plausibility_check(original, variant, DOMAIN_ECONOMICS)
        validation_results["llm_plausibility"] = llm_check_econ
        if not llm_check_econ.get("skipped") and not llm_check_econ["is_valid"]:
            for issue in llm_check_econ.get("issues", []):
                issues.append(f"LLM-Check (Wirtschaft): {issue}")

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
