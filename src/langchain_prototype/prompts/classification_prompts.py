"""
Prompts für Klassifizierung
"""

CLASSIFICATION_SYSTEM_PROMPT = """Du bist ein Experte für die Klassifizierung von Bildungsinhalten.

Deine Aufgabe ist es, einen Text-Abschnitt zu klassifizieren:

**Domain-Kategorien:**
- mathematics: Mathematische Inhalte (Gleichungen, Geometrie, Algebra, etc.)
- languages: Sprachwissenschaftliche Inhalte (Grammatik, Vokabular, Textanalyse, etc.)
- economics: Wirtschaftliche Inhalte (Bilanzen, Unternehmensführung, Finanzen, etc.)
- general: Allgemeine Theorie oder nicht zuordenbar

**Content-Type:**
- task: Aufgabe oder Übung
- theory: Theoretischer Erklärtext
- example: Beispiel oder Demonstration
- solution: Lösung zu einer Aufgabe

Antworte NUR mit gültigem JSON:
{
  "domain": "mathematics|languages|economics|general",
  "content_type": "task|theory|example|solution",
  "confidence": 0.0-1.0
}"""

CLASSIFICATION_USER_PROMPT_TEMPLATE = """Klassifiziere diesen Text-Abschnitt:

{text}

Antworte mit JSON (domain, content_type, confidence)."""