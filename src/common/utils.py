"""
Gemeinsame Hilfsfunktionen für alle Prototypen.
"""
from difflib import SequenceMatcher
from typing import Dict


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Berechnet Text-Ähnlichkeit zwischen zwei Strings (0–1).

    Verwendet SequenceMatcher (difflib) auf Lowercase-Strings.
    Wird von RewritingChain und RewritingNode für den Diversity-Check genutzt.
    """
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


# Union aller Platzhalter-Zeichen über alle Prototypen:
#   □ (U+25A1) und ☐ (U+2610, Hybrid OCR) werden beide unterstützt.
_PLACEHOLDERS = ['☐', '□', '___', '→ ___', '→___', '________']


def check_placeholder_preservation(original: str, variant: str) -> Dict:
    """
    Prüft ob Aufgaben-Platzhalter aus dem Original in der Variante erhalten sind.
    Verhindert dass das LLM Lücken ausfüllt statt zu variieren.

    Unterstützt □ (U+25A1), ☐ (U+2610, Hybrid OCR), ___ und Pfeilvarianten.

    Returns:
        Dict mit is_valid, original_count, variant_count, skipped (und ratio wenn anwendbar).
    """
    original_count = sum(original.count(p) for p in _PLACEHOLDERS)
    variant_count  = sum(variant.count(p)  for p in _PLACEHOLDERS)

    if original_count == 0:
        return {'is_valid': True, 'original_count': 0, 'variant_count': 0, 'skipped': True}

    ratio = variant_count / original_count
    is_valid = ratio >= 0.8

    return {
        'is_valid': is_valid,
        'original_count': original_count,
        'variant_count': variant_count,
        'ratio': ratio,
        'skipped': False,
    }
