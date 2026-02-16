"""
SymPy Validator für mathematische Korrektheit
Prüft Gleichungen, Formeln, geometrische Bedingungen
"""
import re
from typing import Dict, List, Any
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from pathlib import Path

from ..logger import setup_logger

logger = setup_logger(__name__)

class SymPyValidator:
    """
    Validator für mathematische Ausdrücke und Gleichungen
    """
    
    def __init__(self):
        """Initialisiert den SymPy Validator"""
        logger.info("SymPy Validator initialisiert")
    
    def extract_equations(self, text: str) -> List[str]:
        """
        Extrahiert Gleichungen aus Text
        
        Patterns:
        - "2x + 5 = 13"
        - "x^2 + 3x - 4 = 0"
        - etc.
        """
        # Pattern für Gleichungen (simple Heuristik)
        equation_pattern = r'([a-z]\s*[\+\-\*/\^]\s*[\d\w\s\+\-\*/\^()]+\s*=\s*[\d\w\s\+\-\*/\^()]+)'
        
        equations = re.findall(equation_pattern, text, re.IGNORECASE)
        
        logger.debug(f"Extrahierte {len(equations)} Gleichungen")
        return equations
    
    def parse_equation(self, equation_str: str) -> Dict[str, Any]:
        """
        Parsed eine Gleichung und gibt SymPy-Objekte zurück
        
        Args:
            equation_str: z.B. "2x + 5 = 13"
        
        Returns:
            Dict mit left_side, right_side, variables, is_valid
        """
        try:
            # Säubere String
            equation_str = equation_str.replace('^', '**')  # Python-Syntax
            equation_str = equation_str.strip()
            
            # Splitte bei '='
            if '=' not in equation_str:
                return {'is_valid': False, 'error': 'Kein = gefunden'}
            
            left, right = equation_str.split('=', 1)
            
            # Parse beide Seiten
            left_expr = parse_expr(left.strip(), transformations='all')
            right_expr = parse_expr(right.strip(), transformations='all')
            
            # Finde Variablen
            variables = list(left_expr.free_symbols.union(right_expr.free_symbols))
            
            return {
                'is_valid': True,
                'left_side': left_expr,
                'right_side': right_expr,
                'variables': variables,
                'equation_str': equation_str
            }
            
        except Exception as e:
            logger.warning(f"Fehler beim Parsen von '{equation_str}': {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'equation_str': equation_str
            }
    
    def solve_equation(self, equation_dict: Dict) -> Dict[str, Any]:
        """
        Löst eine geparste Gleichung
        
        Returns:
            Dict mit solutions, is_solvable
        """
        if not equation_dict.get('is_valid'):
            return {
                'is_solvable': False,
                'error': equation_dict.get('error')
            }
        
        try:
            left = equation_dict['left_side']
            right = equation_dict['right_side']
            variables = equation_dict['variables']
            
            # Gleichung als left - right = 0
            equation = sp.Eq(left, right)
            
            # Löse für alle Variablen
            if len(variables) == 1:
                solutions = sp.solve(equation, variables[0])
            else:
                solutions = sp.solve(equation, variables)
            
            return {
                'is_solvable': True,
                'solutions': solutions,
                'num_solutions': len(solutions) if isinstance(solutions, list) else 1
            }
            
        except Exception as e:
            logger.warning(f"Fehler beim Lösen: {e}")
            return {
                'is_solvable': False,
                'error': str(e)
            }
    
    def check_triangle_inequality(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        Prüft Dreiecksungleichung: a + b > c, a + c > b, b + c > a
        
        Returns:
            Dict mit is_valid, violations
        """
        violations = []
        
        if a + b <= c:
            violations.append(f"{a} + {b} ≤ {c}")
        if a + c <= b:
            violations.append(f"{a} + {c} ≤ {b}")
        if b + c <= a:
            violations.append(f"{b} + {c} ≤ {a}")
        
        return {
            'is_valid': len(violations) == 0,
            'violations': violations
        }
    
    def check_quadratic_discriminant(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        Prüft Diskriminante einer quadratischen Gleichung ax² + bx + c = 0
        
        Returns:
            Dict mit discriminant, has_real_solutions, num_solutions
        """
        discriminant = b**2 - 4*a*c
        
        if discriminant > 0:
            return {
                'discriminant': discriminant,
                'has_real_solutions': True,
                'num_solutions': 2
            }
        elif discriminant == 0:
            return {
                'discriminant': discriminant,
                'has_real_solutions': True,
                'num_solutions': 1
            }
        else:
            return {
                'discriminant': discriminant,
                'has_real_solutions': False,
                'num_solutions': 0
            }
    
    def validate_financial_calculation(
        self, 
        principal: float, 
        rate: float, 
        time: float,
        expected_result: float = None
    ) -> Dict[str, Any]:
        """
        Validiert Zinseszins-Berechnung
        
        Formula: A = P(1 + r)^t
        
        Returns:
            Dict mit calculated_value, is_realistic, matches_expected
        """
        if rate < 0 or rate > 1:
            return {
                'is_valid': False,
                'error': f'Unrealistischer Zinssatz: {rate*100}%'
            }
        
        if principal <= 0:
            return {
                'is_valid': False,
                'error': f'Kapital muss positiv sein: {principal}'
            }
        
        # Berechne Zinseszins
        calculated = principal * (1 + rate) ** time
        
        result = {
            'is_valid': True,
            'calculated_value': calculated,
            'is_realistic': 100 <= calculated <= 1_000_000  # Realistische Grenzen
        }
        
        if expected_result:
            # Prüfe ob Abweichung < 1%
            deviation = abs(calculated - expected_result) / expected_result
            result['matches_expected'] = deviation < 0.01
            result['deviation'] = deviation
        
        return result
    
    def validate_text(self, text: str) -> Dict[str, Any]:
        """
        Validiert mathematischen Text komplett
        
        Returns:
            Dict mit equations_found, solvable_equations, issues
        """
        equations = self.extract_equations(text)
        
        results = {
            'equations_found': len(equations),
            'parsed_equations': [],
            'solvable_equations': 0,
            'unsolvable_equations': 0,
            'issues': []
        }
        
        for eq_str in equations:
            parsed = self.parse_equation(eq_str)
            
            if parsed['is_valid']:
                solved = self.solve_equation(parsed)
                
                if solved['is_solvable']:
                    results['solvable_equations'] += 1
                else:
                    results['unsolvable_equations'] += 1
                    results['issues'].append({
                        'equation': eq_str,
                        'error': solved.get('error')
                    })
                
                results['parsed_equations'].append({
                    'equation': eq_str,
                    'solvable': solved['is_solvable'],
                    'solutions': solved.get('solutions')
                })
            else:
                results['unsolvable_equations'] += 1
                results['issues'].append({
                    'equation': eq_str,
                    'error': parsed.get('error')
                })
        
        return results


# Singleton
_sympy_validator = None

def get_sympy_validator() -> SymPyValidator:
    """Gibt Singleton-Instanz zurück"""
    global _sympy_validator
    if _sympy_validator is None:
        _sympy_validator = SymPyValidator()
    return _sympy_validator