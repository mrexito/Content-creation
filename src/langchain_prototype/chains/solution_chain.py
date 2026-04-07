"""
Solution Chain: Variante → Musterantwort

Generiert eine korrekte Musterantwort für eine umgeschriebene Aufgabe.

LCEL-Pattern: ChatPromptTemplate | llm | StrOutputParser + _clean_solution()

Strategie:
  Die System-Prompts fordern direkte Ausgabe ohne Prefix und ohne Markdown.
  _clean_solution() entfernt als Post-Processing alle LLM-Artefakte, die
  trotzdem auftreten (Marker-Prefixe, Sterne, Backticks).
  Bei mehrzeiligem Output (CoT-Fallback) wird die letzte nicht-leere Zeile
  nach der Bereinigung verwendet.

Temperature: 0 für alle Domains (deterministisch).
"""
import re
from typing import Dict, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common.constants import DOMAIN_MATH
from common.logger import setup_logger
from langchain_prototype.lcel_llm import get_lcel_llm

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Post-Processing: Artefakte entfernen
# ---------------------------------------------------------------------------

# Prefixe die das LLM trotz Anweisung ausgibt
_PREFIX_PATTERNS = [
    r'^musterantwort\s*:\s*',
    r'^lösung\s*:\s*',
    r'^loesung\s*:\s*',
    r'^antwort\s*:\s*',
    r'^ergebnis\s*:\s*',
    r'^result\s*:\s*',
    r'^solution\s*:\s*',
]


def _clean_solution(text: str) -> Optional[str]:
    """
    Entfernt häufige LLM-Artefakte aus der Musterantwort.

    Behandelt:
    - Markdown-Fettschrift und -Kursivschrift: **text** / *text* → text
    - Backticks: `text` → text
    - Bekannte Präfix-Marker (case-insensitive): "Musterantwort: X" → "X"
    - Führende/abschliessende Whitespace
    """
    if not text:
        return None

    # Markdown-Sterne entfernen: ***text***, **text**, *text* → text
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text, flags=re.DOTALL)
    # Backticks entfernen
    text = re.sub(r'`+', '', text)
    # Bekannte Prefixe entfernen (case-insensitive, nur am Zeilenanfang)
    for pattern in _PREFIX_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    text = text.strip()
    return text if text else None


# ---------------------------------------------------------------------------
# Domain-spezifische System-Prompts
# ---------------------------------------------------------------------------

SOLUTION_MATH_SYSTEM_PROMPT = """Du löst eine Mathematik-Aufgabe und gibst die Lösung mit Berechnungsweg aus.

AUSGABE-REGELN (alle zwingend):
- Strukturierter Berechnungsweg in nummerierten Schritten:
    Schritt 1: [Ansatz / Formel aufstellen]
    Schritt 2: [Umformung / Zwischenrechnung]
    Schritt 3: [Ergebnis mit Einheit]
- KEIN "Musterantwort:", KEIN "MUSTERANTWORT:", KEIN "Lösung:", KEIN Prefix
- KEIN Markdown: keine Sterne (*), keine Backticks (`), keine Unterstriche
- Einheit exakt so wie in der Aufgabe (cm² bleibt cm², m bleibt m)
- Wenn die Aufgabe unlösbar oder widersprüchlich ist: gib nur "–" aus

FORMEL-REGELN (kritisch — lies die Aufgabe genau, bevor du rechnest):
- Rechteck-Fläche:       Länge × Breite
- Quadrat-Fläche:        Seitenlänge × Seitenlänge  (KEIN Pi — ein Quadrat ist kein Kreis!)
- Kreis-Fläche:          pi × r²  (NUR wenn die Aufgabe einen Kreis beschreibt)
- Dreieck-Fläche:        (Grundlinie × Höhe) / 2
- Trapez-Fläche:         (a + c) / 2 × Höhe
- Parallelogramm-Fläche: Grundseite × Höhe
- Wenn pi gegeben ist: verwende genau diesen Wert (pi = 3.14 → 3.14, nicht 3.14159)
"""

SOLUTION_LANGUAGES_SYSTEM_PROMPT = """Du löst eine Deutsch-Sprachaufgabe und gibst NUR die Musterantwort aus.

AUSGABE-REGELN (alle zwingend):
- Nur die korrekte Antwort, kein Kommentar, keine Erklärung
- KEIN "Musterantwort:", KEIN Prefix, KEIN Markdown
- Bei Lückentexten: vollständiger Satz mit ausgefüllten Lücken
- Bei Transformationen (Passiv, Zeitform): der fertige umgeformte Satz
- Bei Tabellen (Komparativ/Superlativ): eine Zeile pro Adjektiv
- Bei offenen Fragen: eine konkrete Musterantwort
- Bei mehreren Teilaufgaben: eine Zeile pro Teilantwort
- Falls unlösbar: nur "–"
"""

SOLUTION_ECONOMICS_SYSTEM_PROMPT = """Du löst eine Wirtschaftsaufgabe und gibst NUR das Ergebnis aus.

AUSGABE-REGELN (alle zwingend):
- Nur der nackte Zahlenwert mit Einheit und Bezeichnung, z.B.: Eigenkapitalquote: 52.2%
- KEIN "Musterantwort:", KEIN Prefix, KEIN Markdown
- KEIN Rechenweg, KEINE Formel, KEINE Erklärung im Output
- Bei mehreren Teilresultaten: eine Zeile pro Resultat
- Einheit exakt wie in der Aufgabe (CHF bleibt CHF, % bleibt %)
- Falls unlösbar: nur "–"
"""

SOLUTION_USER_PROMPT = """Aufgabe:
{variant_text}

Gib NUR das Ergebnis aus. Kein Prefix, kein Markdown, keine Erklärung."""

# ---------------------------------------------------------------------------
# Prompt-Template (einmal aufgebaut)
# ---------------------------------------------------------------------------

_SOLUTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    ("human", SOLUTION_USER_PROMPT),
])


# ---------------------------------------------------------------------------
# Chain-Klasse
# ---------------------------------------------------------------------------

class SolutionChain:
    """
    LCEL-Chain für Musterantwort-Generierung.

    Output-Strategie:
      1. LLM gibt idealerweise direkt den Wert aus (kein Prefix, kein Markdown).
      2. _clean_solution() entfernt stray Artefakte (Marker, Sterne, Backticks).
      3. Bei mehrzeiligem Output: letzte nicht-leere Zeile nach Bereinigung.
    Temperature: 0 für deterministischen Output.
    """

    DOMAIN_PROMPTS = {
        "mathematics": SOLUTION_MATH_SYSTEM_PROMPT,
        "languages":   SOLUTION_LANGUAGES_SYSTEM_PROMPT,
        "economics":   SOLUTION_ECONOMICS_SYSTEM_PROMPT,
        "general":     SOLUTION_MATH_SYSTEM_PROMPT,  # Fallback
    }

    def __init__(self):
        llm = get_lcel_llm(temperature=0)
        self._chain = _SOLUTION_PROMPT | llm | StrOutputParser()
        logger.info("SolutionChain (LCEL, temperature=0, direct+clean) initialisiert")

    def generate_solution(self, variant_text: str, domain: str) -> Optional[str]:
        """
        Generiert Musterantwort für eine umgeschriebene Aufgabe.
        Gibt None zurück bei leerem Input oder Exception.
        Gibt "–" zurück wenn LLM explizit keine Antwort kennt.
        """
        if not variant_text or not variant_text.strip():
            return None

        system_prompt = self.DOMAIN_PROMPTS.get(domain, SOLUTION_MATH_SYSTEM_PROMPT)

        try:
            raw = self._chain.invoke({
                "system_prompt": system_prompt,
                "variant_text": variant_text,
            }).strip()

            if not raw:
                return None

            # Bei Mathematik: Berechnungsweg (mehrzeilig, Absicht) vollständig behalten.
            # Sonst CoT-Fallback: letzte nicht-leere Zeile verwenden.
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            if domain == DOMAIN_MATH and len(lines) > 1:
                candidate = '\n'.join(lines)
            else:
                candidate = lines[-1] if lines else raw

            # Post-Processing: Artefakte entfernen
            answer = _clean_solution(candidate)

            logger.debug(f"SolutionChain [{domain}]: '{answer}' (raw={len(raw)}ch)")
            return answer

        except Exception as e:
            logger.warning(f"SolutionChain fehlgeschlagen für domain='{domain}': {e}")
            return None

    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        input_data: {"variant_text": str, "domain": str}
        returns:    {"solution": str | None, "success": bool}
        """
        variant_text = input_data.get("variant_text", "")
        domain = input_data.get("domain", "general")
        solution = self.generate_solution(variant_text, domain)
        return {
            "solution": solution,
            "success": solution is not None,
        }


def get_solution_chain() -> SolutionChain:
    """Factory"""
    return SolutionChain()
