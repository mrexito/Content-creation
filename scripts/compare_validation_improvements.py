"""
Vergleicht Validation-Ergebnisse: Alte vs. Neue Thresholds
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config

# Führe Evaluation erneut aus
import evaluate_all_domains

def main():
    print("="*80)
    print("VALIDATION THRESHOLD OPTIMIZATION - BEFORE/AFTER COMPARISON")
    print("="*80)
    print("\n📋 Original Thresholds:")
    print("   - BERT (Languages): 0.85")
    print("   - Numbers (Economics): ±2")
    print("   - Length Ratio: 0.5-2.0 (all)")
    print("\n🔧 New Thresholds:")
    print("   - BERT (Languages): 0.70")
    print("   - Numbers (Economics): ±3")
    print("   - Length Ratio:")
    print("     • Math: 0.5-2.0")
    print("     • Languages: 0.6-1.8")
    print("     • Economics: 0.4-2.5")
    print("\n" + "="*80 + "\n")
    
    # Führe neue Evaluation aus
    evaluate_all_domains.main()

if __name__ == '__main__':
    main()