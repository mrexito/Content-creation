"""
Testet Rewriting + Validation Chains
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from langchain_prototype.chains.rewriting_chain import get_rewriting_chain
from langchain_prototype.chains.validation_chain import get_validation_chain

def test_rewriting_validation():
    """Testet Rewriting + Validation"""
    
    print("="*60)
    print("REWRITING + VALIDATION TEST")
    print("="*60 + "\n")
    
    # Test-Segment (Mathematik)
    segment = {
        'type': 'task',
        'text': 'Aufgabe 1: Löse die Gleichung: 2x + 5 = 13'
    }
    
    domain = 'mathematics'
    
    print(f"📝 Original-Segment:")
    print(f"   {segment['text']}\n")
    
    # ===== Rewriting =====
    print("🔗 Rewriting Chain")
    print("-" * 60)
    
    rewriting_chain = get_rewriting_chain(num_variants=3)
    
    rewrite_result = rewriting_chain.invoke({
        'segment': segment,
        'domain': domain
    })
    
    if rewrite_result['success']:
        print(f"✅ Rewriting erfolgreich")
        print(f"   Varianten: {rewrite_result['metadata']['num_successful']}/{rewrite_result['metadata']['num_requested']}\n")
        
        for variant in rewrite_result['variants']:
            if variant.get('text'):
                print(f"   Variante {variant['variant_id']}: {variant['text']}")
        print()
    else:
        print(f"❌ Rewriting fehlgeschlagen\n")
        return
    
    # ===== Validation =====
    print("🔗 Validation Chain")
    print("-" * 60)
    
    validation_chain = get_validation_chain()
    
    validation_result = validation_chain.invoke({
        'original': rewrite_result['original'],
        'variants': rewrite_result['variants'],
        'domain': domain
    })
    
    if validation_result['success']:
        stats = validation_result['statistics']
        print(f"✅ Validation abgeschlossen")
        print(f"   Gesamt: {stats['total']}")
        print(f"   Valide: {stats['valid']}")
        print(f"   Invalide: {stats['invalid']}")
        print(f"   Rate: {stats['validation_rate']*100:.1f}%\n")
        
        # Zeige Details für jede Variante
        for v in validation_result['validated_variants']:
            validation = v.get('validation', {})
            status = "✅" if validation.get('is_valid') else "❌"
            
            print(f"{status} Variante {v.get('variant_id')}:")
            if validation.get('is_valid'):
                print(f"   Alle Checks bestanden")
            else:
                issues = validation.get('issues', [])
                for issue in issues:
                    print(f"   ⚠️  {issue}")
            print()
    else:
        print(f"❌ Validation fehlgeschlagen\n")
    
    print("="*60)
    print("✅ Test abgeschlossen!")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_rewriting_validation()