"""
Testet die ersten LangGraph Nodes
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from langgraph_prototype.state.workflow_state import create_initial_state
from langgraph_prototype.nodes.parsing_node import parsing_node
from langgraph_prototype.nodes.segmentation_node import segmentation_node
from langgraph_prototype.nodes.classification_node import classification_node


def test_nodes():
    """Testet Nodes einzeln"""
    
    print("="*60)
    print("LANGGRAPH NODES TEST")
    print("="*60 + "\n")
    
    # Test-PDF
    test_pdf = Config.DATA_INPUT_PATH / 'math' / 'equations_simple.pdf'
    
    if not test_pdf.exists():
        print(f"❌ Test-PDF nicht gefunden: {test_pdf}")
        return
    
    # Initialer State
    state = create_initial_state(
        pdf_path=str(test_pdf),
        domain='math',
        num_variants=2
    )
    
    print(f"📄 Input: {test_pdf.name}")
    print(f"🎯 Domain: {state['domain']}")
    print(f"🔢 Varianten: {state['num_variants']}\n")
    
    # ===== Node 1: Parsing =====
    print("🔗 Node 1: Parsing")
    print("-" * 60)
    state = parsing_node(state)
    
    if state['current_phase'] == 'parsing_complete':
        print(f"✅ Parsing erfolgreich")
        print(f"   Tool: {state['ocr_metadata']['tool_used']}")
        print(f"   Chars: {state['ocr_metadata']['char_count']}")
        print(f"   Zeit: {state['ocr_metadata']['processing_time']:.2f}s\n")
    else:
        print(f"❌ Parsing fehlgeschlagen: {state['errors']}\n")
        return
    
    # ===== Node 2: Segmentation =====
    print("🔗 Node 2: Segmentation")
    print("-" * 60)
    state = segmentation_node(state)
    
    if state['current_phase'] == 'segmentation_complete':
        print(f"✅ Segmentation erfolgreich")
        print(f"   Segmente: {len(state['segments'])}")
        for idx, seg in enumerate(state['segments'][:3], 1):
            print(f"   {idx}. [{seg['type']}] {seg['text'][:50]}...")
        print()
    else:
        print(f"❌ Segmentation fehlgeschlagen: {state['errors']}\n")
        return
    
    # ===== Node 3: Classification =====
    print("🔗 Node 3: Classification")
    print("-" * 60)
    state = classification_node(state)
    
    if state['current_phase'] == 'classification_complete':
        print(f"✅ Classification erfolgreich")
        for idx, cs in enumerate(state['classified_segments'][:3], 1):
            c = cs['classification']
            print(f"   {idx}. {c['domain']} / {c['content_type']} (conf: {c['confidence']:.2f})")
        print()
    else:
        print(f"❌ Classification fehlgeschlagen: {state['errors']}\n")
        return
    
    print("="*60)
    print("✅ Alle Nodes erfolgreich getestet!")
    print(f"Gesamt-Zeit: {state['total_processing_time']:.2f}s")
    print("="*60 + "\n")


if __name__ == '__main__':
    test_nodes()