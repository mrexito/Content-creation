"""
Testet alle Validators
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.validators import (
    get_sympy_validator,
    get_bert_validator,
    get_consistency_validator
)

def test_sympy():
    """Testet SymPy Validator"""
    print("🧪 Test SymPy Validator\n")
    
    validator = get_sympy_validator()
    
    # Test 1: Einfache Gleichung
    eq = "2x + 5 = 13"
    parsed = validator.parse_equation(eq)
    print(f"Gleichung: {eq}")
    print(f"  Valid: {parsed['is_valid']}")
    
    if parsed['is_valid']:
        solved = validator.solve_equation(parsed)
        print(f"  Lösungen: {solved.get('solutions')}\n")
    
    # Test 2: Dreieck
    triangle = validator.check_triangle_inequality(5, 7, 15)
    print(f"Dreieck (5, 7, 15):")
    print(f"  Valid: {triangle['is_valid']}")
    print(f"  Violations: {triangle['violations']}\n")
    
    # Test 3: Zinseszins
    finance = validator.validate_financial_calculation(1000, 0.03, 5)
    print(f"Zinseszins (1000€, 3%, 5 Jahre):")
    print(f"  Endkapital: {finance['calculated_value']:.2f}€\n")

def test_bert():
    """Testet BERT Validator"""
    print("🧪 Test BERT Validator\n")
    
    validator = get_bert_validator()
    
    original = "Das Haus steht auf dem Hügel."
    paraphrase = "Auf dem Hügel befindet sich ein Haus."
    
    result = validator.validate_paraphrase(original, paraphrase)
    
    print(f"Original: {original}")
    print(f"Paraphrase: {paraphrase}")
    print(f"  Valid: {result['is_valid']}")
    print(f"  F1-Score: {result['score']:.3f}\n")

def test_consistency():
    """Testet Consistency Validator"""
    print("🧪 Test Consistency Validator\n")
    
    validator = get_consistency_validator()
    
    # Test 1: Zahlen-Extraktion
    text = "Das Unternehmen hat 150.000 € Anlagevermögen und 80.000 € Umlaufvermögen."
    numbers = validator.extract_numbers(text)
    print(f"Text: {text}")
    print(f"  Gefundene Zahlen: {numbers}\n")
    
    # Test 2: Bilanz
    bilanz_text = """
    AKTIVA:
    Anlagevermögen: 150.000 €
    Umlaufvermögen: 80.000 €
    Gesamt: 230.000 €
    
    PASSIVA:
    Eigenkapital: 120.000 €
    Fremdkapital: 110.000 €
    Gesamt: 230.000 €
    """
    
    balance = validator.check_balance_sheet_consistency(bilanz_text)
    print(f"Bilanz-Check:")
    print(f"  Balanced: {balance.get('is_balanced')}")
    print(f"  Aktiva: {balance.get('aktiva_sum')}")
    print(f"  Passiva: {balance.get('passiva_sum')}\n")

if __name__ == '__main__':
    print("="*60)
    print("VALIDATOR TESTS")
    print("="*60 + "\n")
    
    test_sympy()
    test_bert()
    test_consistency()
    
    print("✅ Alle Tests abgeschlossen!")