"""
Testet die ersten LangChain-Chains
"""
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from langchain_prototype.chains.parsing_chain import get_parsing_chain
from langchain_prototype.chains.segmentation_chain import get_segmentation_chain
from langchain_prototype.chains.classification_chain import get_classification_chain

def test_full_pipeline():
    """Testet komplette Pipeline: PDF → Parse → Segment → Classify"""
    
    print("="*60)
    print("LANGCHAIN CHAINS TEST")
    print("="*60 + "\n")
    
    # Test-PDF
    test_pdf = Config.DATA_INPUT_PATH / 'math' / 'equations_simple.pdf'
    
    if not test_pdf.exists():
        print(f"❌ Test-PDF nicht gefunden: {test_pdf}")
        print("   Führe erst aus: python scripts/generate_test_pdfs.py")
        return
    
    print(f"📄 Test-PDF: {test_pdf.name}\n")
    
    # ===== 1. Parsing Chain =====
    print("🔗 Chain 1: Parsing (PDF → Text)")
    print("-" * 60)
    
    parsing_chain = get_parsing_chain(domain='math')
    parse_result = parsing_chain.invoke({'pdf_path': str(test_pdf)})
    
    if parse_result['success']:
        text = parse_result['text']
        print(f"✅ Parsing erfolgreich")
        print(f"   Tool: {parse_result['metadata']['tool_used']}")
        print(f"   Seiten: {parse_result['metadata']['pages']}")
        print(f"   Zeit: {parse_result['metadata']['processing_time']:.2f}s")
        print(f"   Text-Länge: {len(text)} Zeichen")
        print(f"\n   Vorschau:")
        print(f"   {text[:200]}...\n")
    else:
        print(f"❌ Parsing fehlgeschlagen: {parse_result['metadata'].get('error')}")
        return
    
    # ===== 2. Segmentation Chain =====
    print("🔗 Chain 2: Segmentation (Text → Abschnitte)")
    print("-" * 60)
    
    segmentation_chain = get_segmentation_chain()
    segment_result = segmentation_chain.invoke({'text': text})
    
    if segment_result['success']:
        segments = segment_result['segments']
        print(f"✅ Segmentierung erfolgreich")
        print(f"   Abschnitte: {len(segments)}")
        print(f"\n   Segments:")
        for idx, seg in enumerate(segments, 1):
            print(f"   {idx}. [{seg.get('type')}] {seg.get('text', '')[:60]}...")
        print()
    else:
        print(f"❌ Segmentierung fehlgeschlagen: {segment_result['metadata'].get('error')}")
        return
    
    # ===== 3. Classification Chain =====
    print("🔗 Chain 3: Classification (Abschnitt → Domain/Type)")
    print("-" * 60)
    
    classification_chain = get_classification_chain()
    
    # Klassifiziere ersten Task-Segment
    for segment in segments:
        if segment.get('type') in ['task', 'theory']:
            classify_result = classification_chain.invoke({'segment': segment})
            
            if classify_result['success']:
                classification = classify_result['classification']
                print(f"✅ Klassifizierung erfolgreich")
                print(f"   Segment: {segment.get('text', '')[:50]}...")
                print(f"   Domain: {classification.get('domain')}")
                print(f"   Content-Type: {classification.get('content_type')}")
                print(f"   Confidence: {classification.get('confidence', 0):.2f}")
            else:
                print(f"❌ Klassifizierung fehlgeschlagen")
            
            break  # Nur ersten Segment testen
    
    print("\n" + "="*60)
    print("✅ Alle Chains erfolgreich getestet!")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_full_pipeline()