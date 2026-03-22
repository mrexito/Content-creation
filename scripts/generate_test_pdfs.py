"""
Generiert einfache Test-PDFs für alle drei Domänen
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from common.config import Config

def create_math_pdf():
    """Erstellt ein einfaches Mathematik-PDF"""
    output_path = Config.DATA_INPUT_PATH / 'math' / 'equations_simple.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    c = canvas.Canvas(str(output_path), pagesize=A4)
    
    # Titel
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Mathematik-Übungen")
    
    # Aufgaben
    c.setFont("Helvetica", 12)
    y = 750
    
    aufgaben = [
        "Aufgabe 1: Löse die Gleichung: 2x + 5 = 13",
        "",
        "Aufgabe 2: Vereinfache: 3(x + 2) - 2(x - 1)",
        "",
        "Aufgabe 3: Berechne den Umfang eines Dreiecks mit den Seiten:",
        "a = 5 cm, b = 7 cm, c = 9 cm",
        "",
        "Aufgabe 4: Ein Kapital von 1000 € wird zu 3% Zinsen angelegt.",
        "Wie hoch ist das Endkapital nach 5 Jahren?",
    ]
    
    for aufgabe in aufgaben:
        c.drawString(50, y, aufgabe)
        y -= 20
    
    c.save()
    print(f"✓ Erstellt: {output_path}")

def create_language_pdf():
    """Erstellt ein einfaches Sprachwissenschaft-PDF"""
    output_path = Config.DATA_INPUT_PATH / 'languages' / 'grammar_exercise.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    c = canvas.Canvas(str(output_path), pagesize=A4)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Grammatik-Übungen")
    
    c.setFont("Helvetica", 12)
    y = 750
    
    text = [
        "Aufgabe 1: Setze die richtigen Artikel ein:",
        "",
        "__ Haus steht auf __ Hügel.",
        "__ Kinder spielen in __ Garten.",
        "",
        "Aufgabe 2: Bilde das Perfekt:",
        "",
        "Ich gehe in die Schule. → _______________________",
        "Er liest ein Buch. → _______________________",
        "",
        "Aufgabe 3: Welche Wörter sind Synonyme?",
        "",
        "schnell - rasch - langsam - zügig",
    ]
    
    for line in text:
        c.drawString(50, y, line)
        y -= 20
    
    c.save()
    print(f"✓ Erstellt: {output_path}")

def create_economics_pdf():
    """Erstellt ein einfaches Wirtschaft-PDF"""
    output_path = Config.DATA_INPUT_PATH / 'economics' / 'balance_sheet.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    c = canvas.Canvas(str(output_path), pagesize=A4)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Bilanzanalyse - Fallstudie")
    
    c.setFont("Helvetica", 12)
    y = 750
    
    text = [
        "Unternehmen: TechStart GmbH",
        "",
        "Bilanz zum 31.12.2024:",
        "",
        "AKTIVA:",
        "Anlagevermögen:        150.000 €",
        "Umlaufvermögen:        80.000 €",
        "Gesamt:                230.000 €",
        "",
        "PASSIVA:",
        "Eigenkapital:          120.000 €",
        "Fremdkapital:          110.000 €",
        "Gesamt:                230.000 €",
        "",
        "Aufgabe 1: Berechne die Eigenkapitalquote.",
        "",
        "Aufgabe 2: Der Umsatz betrug 500.000 €, die Kosten 450.000 €.",
        "Wie hoch ist der Gewinn?",
    ]
    
    for line in text:
        c.drawString(50, y, line)
        y -= 20
    
    c.save()
    print(f"✓ Erstellt: {output_path}")

def create_math_advanced_pdf():
    """Fortgeschrittene Gleichungen: quadratisch, Gleichungssystem, Prozent, Pythagoras"""
    output_path = Config.DATA_INPUT_PATH / 'math' / 'equations_advanced.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Fortgeschrittene Gleichungen")

    c.setFont("Helvetica", 12)
    y = 750

    lines = [
        "Aufgabe 1: Löse die quadratische Gleichung: x^2 - 5x + 6 = 0",
        "",
        "Aufgabe 2: Löse das Gleichungssystem:",
        "2x + y = 8",
        "x - y = 1",
        "",
        "Aufgabe 3: Ein Produkt kostet nach 20% Rabatt 240 CHF.",
        "Wie hoch war der ursprüngliche Preis?",
        "",
        "Aufgabe 4: Ein rechtwinkliges Dreieck hat die Katheten a = 6 cm und b = 8 cm.",
        "Berechne die Hypotenuse c.",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    c.save()
    print(f"✓ Erstellt: {output_path}")


def create_math_word_problems_pdf():
    """Textaufgaben: Zinseszins, Geschwindigkeit, Fläche, Proportionalität"""
    output_path = Config.DATA_INPUT_PATH / 'math' / 'word_problems.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Textaufgaben")

    c.setFont("Helvetica", 12)
    y = 750

    lines = [
        "Aufgabe 1: Anna legt 2000 CHF zu einem Zinssatz von 4% pro Jahr an.",
        "Wie viel Kapital hat sie nach 3 Jahren (Zinseszinsrechnung)?",
        "",
        "Aufgabe 2: Ein Auto fährt mit einer Geschwindigkeit von 80 km/h.",
        "Wie lange braucht es für eine Strecke von 120 km?",
        "",
        "Aufgabe 3: Ein rechteckiger Garten ist 15 m lang und 8 m breit.",
        "Rund um den Garten soll ein 1 m breiter Weg angelegt werden.",
        "Wie gross ist die verbleibende Gartenfläche?",
        "",
        "Aufgabe 4: 5 Arbeiter benötigen 12 Tage für ein Bauprojekt.",
        "Wie lange brauchen 4 Arbeiter für dieselbe Arbeit?",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    c.save()
    print(f"✓ Erstellt: {output_path}")


def create_language_text_analysis_pdf():
    """Textanalyse: Hauptidee, Synonym, Passivtransformation"""
    output_path = Config.DATA_INPUT_PATH / 'languages' / 'verb_conjugation.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Textanalyse und Leseverständnis")

    c.setFont("Helvetica", 12)
    y = 750

    lines = [
        "Beispieltext:",
        "",
        "Im Frühling erwacht die Natur zu neuem Leben.",
        "Die Bäume treiben frische Blätter aus und die Wiesen",
        "bedecken sich mit bunten Blumen.",
        "Viele Zugvögel kehren aus dem Süden zurück und",
        "füllen die Morgen mit ihrem Gesang.",
        "",
        "Aufgabe 1: Was ist die Hauptaussage des Textes?",
        "Schreibe einen vollständigen Satz.",
        "",
        "Aufgabe 2: Suche im Text ein Synonym für das Wort 'bunt'.",
        "",
        "Aufgabe 3: Schreibe den folgenden Satz im Passiv:",
        "Die Zugvögel füllen die Morgen mit ihrem Gesang.",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    c.save()
    print(f"✓ Erstellt: {output_path}")


def create_language_sentence_construction_pdf():
    """Satzbau: Verbform, Konjunktion, Fehlerkorrektur, Passiv, Wortstellung"""
    output_path = Config.DATA_INPUT_PATH / 'languages' / 'sentence_construction.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Satzbau und Grammatik")

    c.setFont("Helvetica", 12)
    y = 750

    lines = [
        "Aufgabe 1: Setze das Verb in der richtigen Form ein (Präteritum):",
        "Die Schüler _______ fleissig. (lernen)",
        "",
        "Aufgabe 2: Verbinde die beiden Sätze mit einer passenden Konjunktion:",
        "Es regnete. Wir blieben zu Hause.",
        "",
        "Aufgabe 3: Korrigiere den Grammatikfehler im folgenden Satz:",
        "Gestern hat er in die Bibliothek gegangen.",
        "",
        "Aufgabe 4: Schreibe den Satz im Passiv:",
        "Der Lehrer erklärt die Aufgabe.",
        "",
        "Aufgabe 5: Bilde einen sinnvollen Satz aus diesen Wörtern:",
        "morgen / wir / ins / fahren / Kino",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    c.save()
    print(f"✓ Erstellt: {output_path}")


def create_economics_income_statement_pdf():
    """Erfolgsrechnung: Bruttogewinnmarge, Nettogewinnmarge, Umsatzsteigerung
    Zahlen intern konsistent:
      500.000 - 320.000 = 180.000 Bruttogewinn (36%)
      180.000 - 120.000 =  60.000 Jahresgewinn  (12%)
      Verdopplung Gewinn (120.000): Umsatz muss auf 560.000 steigen (+60.000)
    """
    output_path = Config.DATA_INPUT_PATH / 'economics' / 'income_statement.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Erfolgsrechnung - Fallstudie")

    c.setFont("Helvetica", 12)
    y = 750

    lines = [
        "Unternehmen: BioNova AG",
        "",
        "Erfolgsrechnung 2024:",
        "",
        "Umsatzerlöse:              500.000 CHF",
        "Materialkosten:           -320.000 CHF",
        "Bruttogewinn:              180.000 CHF",
        "",
        "Betriebskosten:           -120.000 CHF",
        "Jahresgewinn:               60.000 CHF",
        "",
        "Aufgabe 1: Berechne die Bruttogewinnmarge in Prozent.",
        "",
        "Aufgabe 2: Berechne die Nettogewinnmarge in Prozent.",
        "",
        "Aufgabe 3: Um wie viel CHF muss der Umsatz steigen,",
        "damit sich der Jahresgewinn verdoppelt (Kosten bleiben konstant)?",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    c.save()
    print(f"✓ Erstellt: {output_path}")


def create_economics_investment_pdf():
    """Investitionsrechnung: Amortisation, Kapitalwert (NPV), interner Zinsfuss
    Zahlen intern konsistent:
      Amortisation: 100.000 / 30.000 = 3,33 Jahre
      NPV@8%: 30.000 * Annuitätenfaktor(8%,5J) - 100.000 ≈ +19.781 CHF
      IRR (NPV=0): ca. 15,2%
    """
    output_path = Config.DATA_INPUT_PATH / 'economics' / 'investment_calculation.pdf'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Investitionsrechnung - Fallstudie")

    c.setFont("Helvetica", 12)
    y = 750

    lines = [
        "Investitionsprojekt: Neue Produktionsanlage",
        "",
        "Investitionsdaten:",
        "",
        "Anschaffungskosten:        100.000 CHF",
        "Jährliche Einzahlungen:     30.000 CHF",
        "Nutzungsdauer:              5 Jahre",
        "Kalkulationszinssatz:       8%",
        "",
        "Aufgabe 1: Berechne die Amortisationsdauer (Payback Period).",
        "",
        "Aufgabe 2: Berechne den Kapitalwert (NPV) bei einem Zinssatz von 8%.",
        "",
        "Aufgabe 3: Bei welchem Zinssatz ist der Kapitalwert gleich null",
        "(interner Zinsfuss, Näherungswert genügt)?",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    c.save()
    print(f"✓ Erstellt: {output_path}")


if __name__ == '__main__':
    print("🚀 Erstelle Test-PDFs...\n")

    create_math_pdf()
    create_language_pdf()
    create_economics_pdf()
    create_math_advanced_pdf()
    create_math_word_problems_pdf()
    create_language_text_analysis_pdf()
    create_language_sentence_construction_pdf()
    create_economics_income_statement_pdf()
    create_economics_investment_pdf()

    print("\n✅ Alle Test-PDFs erstellt!")
    print(f"\nOrdner: {Config.DATA_INPUT_PATH}")