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

if __name__ == '__main__':
    print("🚀 Erstelle Test-PDFs...\n")
    
    create_math_pdf()
    create_language_pdf()
    create_economics_pdf()
    
    print("\n✅ Alle Test-PDFs erstellt!")
    print(f"\nOrdner: {Config.DATA_INPUT_PATH}")