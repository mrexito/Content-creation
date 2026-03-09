"""
Kanonische Konstanten für das gesamte Projekt.

Zentrale Definition aller Domain-Strings und Validierungs-Schwellwerte
um Inkonsistenzen zwischen LangChain, LangGraph und Hybrid-Prototyp zu vermeiden.
"""

# ── Kanonische Domain-Namen ────────────────────────────────────────────────────
# WICHTIG: Das LLM (Klassifizierungs-Prompt) gibt 'mathematics' zurück, nicht 'math'.
# Alle internen Domain-Vergleiche MÜSSEN diese Konstanten verwenden.
DOMAIN_MATH = "mathematics"
DOMAIN_LANGUAGES = "languages"
DOMAIN_ECONOMICS = "economics"
DOMAIN_GENERAL = "general"

VALID_DOMAINS = {DOMAIN_MATH, DOMAIN_LANGUAGES, DOMAIN_ECONOMICS, DOMAIN_GENERAL}

# Alias-Mapping: akzeptierte Eingaben → kanonische Form
# Wird in normalize_domain() verwendet (Frontend sendet 'math', LLM gibt 'mathematics').
_DOMAIN_ALIASES: dict = {
    "math":        DOMAIN_MATH,
    "mathematics": DOMAIN_MATH,
    "lang":        DOMAIN_LANGUAGES,
    "language":    DOMAIN_LANGUAGES,
    "languages":   DOMAIN_LANGUAGES,
    "econ":        DOMAIN_ECONOMICS,
    "economy":     DOMAIN_ECONOMICS,
    "economics":   DOMAIN_ECONOMICS,
    "general":     DOMAIN_GENERAL,
}


def normalize_domain(domain: str) -> str:
    """
    Normalisiert einen Domain-String auf die kanonische Form.

    Akzeptiert sowohl Frontend-Werte ('math') als auch LLM-Ausgaben ('mathematics').

    Args:
        domain: Beliebiger Domain-String

    Returns:
        Kanonischer Domain-String (DOMAIN_MATH, DOMAIN_LANGUAGES, etc.)
        oder DOMAIN_GENERAL als Fallback.
    """
    if not domain:
        return DOMAIN_GENERAL
    return _DOMAIN_ALIASES.get(domain.strip().lower(), DOMAIN_GENERAL)


# ── Validierungs-Schwellwerte ──────────────────────────────────────────────────
# Gemeinsamer BERTScore-Threshold für LangChain, LangGraph und Hybrid.
# Wert 0.70 ist bewusst niedriger als BERTScore-Standard (0.92),
# um bedeutungserhaltende Paraphrasen nicht zu streng zu bestrafen.
BERT_THRESHOLD: float = 0.70
