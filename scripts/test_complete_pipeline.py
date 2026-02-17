"""
Test Complete LangChain Pipeline
End-to-End: PDF → Varianten-Dokument
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from langchain_prototype.pipeline import get_pipeline

def test_complete_pipeline():
    """Testet die komplette Pipeline"""
    
    print("="*70)
    print("COMPLETE LANGCHAIN PIPELINE TEST")
    print("="*70 + "\n")
    
    # Test-PDF
    test_pdf = Config.DATA_INPUT_PATH / 'math' / 'equations_simple.pdf'
    
    if not test_pdf.exists():
        print(f"❌ Test-PDF nicht gefunden: {test_pdf}")
        return
    
    print(f"📄 Input: {test_pdf}")
    print(f"🎯 Domain: mathematics")
    print(f"🔢 Varianten: 2 pro Segment\n")
    
    # Pipeline erstellen
    pipeline = get_pipeline(domain='math', num_variants=2)
    
    # Verarbeiten
    print("🚀 Starte Pipeline...\n")
    
    result = pipeline.process_pdf(test_pdf)
    
    print("\n" + "="*70)
    
    if result['success']:
        print("✅ PIPELINE ERFOLGREICH!")
        print("="*70 + "\n")
        
        stats = result['statistics']
        
        print("📊 Statistiken:")
        print(f"   Gesamt-Zeit: {stats['total_time']:.2f}s")
        print(f"   Parsing: {stats['parsing']['processing_time']:.2f}s")
        print(f"   Tool: {stats['parsing']['tool_used']}")
        print(f"   Seiten: {stats['parsing']['pages']}")
        print(f"   Segmente: {stats['segmentation']['num_segments']}")
        print(f"   Segmente mit Varianten: {stats['assembly']['segments_with_variants']}")
        print(f"   Valide Varianten: {stats['assembly']['valid_variants']}/{stats['assembly']['total_variants']}")
        print()
        
        print("📁 Output-Dateien:")
        for file in result['output_files']:
            print(f"   {file}")
        
        print("\n" + "="*70)
        print("🎉 Test abgeschlossen!")
        print("="*70 + "\n")
    else:
        print("❌ PIPELINE FEHLGESCHLAGEN")
        print("="*70 + "\n")
        print(f"Fehler: {result.get('error')}")
        print()

if __name__ == '__main__':
    test_complete_pipeline()