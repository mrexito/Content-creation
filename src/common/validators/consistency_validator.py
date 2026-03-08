"""
Consistency Validator für Zahlen-Text-Konsistenz
Prüft ob Zahlen im Text mit Zahlen in Tabellen/Berechnungen übereinstimmen
"""
import re
from typing import Any, Dict, List, Tuple
from collections import Counter

from ..logger import setup_logger

logger = setup_logger(__name__)

class ConsistencyValidator:
    """
    Validator für Konsistenz zwischen Zahlen und Text
    """
    
    def __init__(self):
        """Initialisiert den Consistency Validator"""
        logger.info("Consistency Validator initialisiert")
    
    def extract_numbers(self, text: str) -> List[float]:
        """
        Extrahiert alle Zahlen aus Text
        
        Returns:
            Liste von Zahlen (als float)
        """
        # Pattern für Zahlen (inkl. Dezimalzahlen, Tausender-Trenner)
        # Beispiele: 1000, 1.000, 1,000, 12.5, 12,5
        pattern = r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\b'
        
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            # Normalisiere (entferne Tausender-Trenner)
            normalized = match.replace('.', '').replace(',', '.')
            try:
                # Versuche als float
                num = float(normalized)
                numbers.append(num)
            except ValueError:
                # Falls es nicht klappt, versuche ohne Punkt
                try:
                    num = float(match.replace(',', '.'))
                    numbers.append(num)
                except ValueError:
                    continue
        
        logger.debug(f"Extrahierte {len(numbers)} Zahlen")
        return numbers
    
    def check_number_consistency(
        self,
        text: str,
        expected_numbers: List[float],
        tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """
        Prüft ob erwartete Zahlen im Text vorkommen
        
        Args:
            text: Zu prüfender Text
            expected_numbers: Liste erwarteter Zahlen
            tolerance: Toleranz für Gleichheit (z.B. 0.01 = 1%)
        
        Returns:
            Dict mit is_consistent, missing_numbers, extra_numbers
        """
        found_numbers = self.extract_numbers(text)
        
        missing = []
        for expected in expected_numbers:
            # Prüfe ob Zahl vorhanden (mit Toleranz)
            found = any(
                abs(found - expected) / max(abs(expected), 1) <= tolerance
                for found in found_numbers
            )
            if not found:
                missing.append(expected)
        
        # Extra Zahlen (die nicht erwartet wurden)
        extra = []
        for found in found_numbers:
            expected = any(
                abs(found - exp) / max(abs(exp), 1) <= tolerance
                for exp in expected_numbers
            )
            if not expected:
                extra.append(found)
        
        return {
            'is_consistent': len(missing) == 0,
            'found_numbers': found_numbers,
            'expected_numbers': expected_numbers,
            'missing_numbers': missing,
            'extra_numbers': extra,
            'num_matches': len(expected_numbers) - len(missing)
        }
    
    def check_balance_sheet_consistency(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Spezielle Prüfung für Bilanzen
        Prüft ob Aktiva = Passiva
        
        Returns:
            Dict mit is_balanced, aktiva_sum, passiva_sum
        """
        # Suche nach AKTIVA und PASSIVA Sektionen
        aktiva_match = re.search(r'AKTIVA:?(.*?)(?:PASSIVA:|$)', text, re.DOTALL | re.IGNORECASE)
        passiva_match = re.search(r'PASSIVA:?(.*?)(?:$)', text, re.DOTALL | re.IGNORECASE)
        
        if not aktiva_match or not passiva_match:
            return {
                'is_balanced': None,
                'error': 'Konnte AKTIVA/PASSIVA nicht finden'
            }
        
        aktiva_numbers = self.extract_numbers(aktiva_match.group(1))
        passiva_numbers = self.extract_numbers(passiva_match.group(1))
        
        # Suche nach "Gesamt:" Zeilen
        aktiva_total = None
        passiva_total = None
        
        for line in aktiva_match.group(1).split('\n'):
            if 'gesamt' in line.lower():
                nums = self.extract_numbers(line)
                if nums:
                    aktiva_total = nums[-1]  # Letzte Zahl in Zeile
        
        for line in passiva_match.group(1).split('\n'):
            if 'gesamt' in line.lower():
                nums = self.extract_numbers(line)
                if nums:
                    passiva_total = nums[-1]
        
        if aktiva_total and passiva_total:
            is_balanced = abs(aktiva_total - passiva_total) < 1.0  # 1€ Toleranz
            
            return {
                'is_balanced': is_balanced,
                'aktiva_sum': aktiva_total,
                'passiva_sum': passiva_total,
                'difference': abs(aktiva_total - passiva_total)
            }
        else:
            return {
                'is_balanced': None,
                'error': 'Konnte Gesamt-Summen nicht finden',
                'aktiva_numbers': aktiva_numbers,
                'passiva_numbers': passiva_numbers
            }
    
    def check_calculation_consistency(
        self,
        text: str,
        calculation: str
    ) -> Dict[str, Any]:
        """
        Prüft ob eine Berechnung im Text konsistent ist
        
        Args:
            text: Text mit der Berechnung
            calculation: z.B. "Umsatz 500000 - Kosten 450000 = Gewinn"
        
        Returns:
            Dict mit is_consistent, calculated_result, stated_result
        """
        # Extrahiere Zahlen aus calculation string
        calc_numbers = self.extract_numbers(calculation)
        
        if len(calc_numbers) < 2:
            return {
                'is_consistent': None,
                'error': 'Zu wenige Zahlen für Berechnung'
            }
        
        # Einfache Heuristik: erste Zahl - zweite Zahl
        calculated = calc_numbers[0] - calc_numbers[1]
        
        # Finde "Gewinn" oder "Ergebnis" im Text
        result_match = re.search(
            r'(?:gewinn|ergebnis|profit).*?(\d+[.,]?\d*)',
            text,
            re.IGNORECASE
        )
        
        if result_match:
            stated_result = self.extract_numbers(result_match.group(0))
            if stated_result:
                is_consistent = abs(calculated - stated_result[0]) < 1.0
                
                return {
                    'is_consistent': is_consistent,
                    'calculated_result': calculated,
                    'stated_result': stated_result[0],
                    'difference': abs(calculated - stated_result[0])
                }
        
        return {
            'is_consistent': None,
            'calculated_result': calculated,
            'stated_result': None,
            'error': 'Konnte Ergebnis im Text nicht finden'
        }


# Singleton
_consistency_validator = None

def get_consistency_validator() -> ConsistencyValidator:
    """Gibt Singleton-Instanz zurück"""
    global _consistency_validator
    if _consistency_validator is None:
        _consistency_validator = ConsistencyValidator()
    return _consistency_validator