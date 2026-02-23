"""
Testet kompletten LangGraph Workflow
"""
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from langgraph_prototype.state.workflow_state import create_initial_state
from langgraph_prototype.graph import create_workflow_graph


def test_complete_workflow():
    """Testet kompletten LangGraph Workflow"""
    
    print("="*70)
    print("LANGGRAPH COMPLETE WORKFLOW TEST")
    print("="*70 + "\n")
    
    # Test-PDF
    test_pdf = Config.DATA_INPUT_PATH / 'math' / 'equations_simple.pdf'
    
    if not test_pdf.exists():
        print(f"❌ Test-PDF nicht gefunden: {test_pdf}")
        return
    
    print(f"📄 Input: {test_pdf.name}\n")
    
    # Erstelle Workflow
    print("🔨 Erstelle Workflow...")
    workflow = create_workflow_graph()
    print("✓ Workflow bereit\n")
    
    # Initialer State
    initial_state = create_initial_state(
        pdf_path=str(test_pdf),
        domain='math',
        num_variants=2
    )
    
    # Führe Workflow aus
    print("🚀 Führe Workflow aus...\n")
    
    final_state = workflow.invoke(initial_state)
    
    # Ergebnisse
    print("\n" + "="*70)
    
    if final_state['current_phase'] == 'assembly_complete':
        print("✅ WORKFLOW ERFOLGREICH!")
        print("="*70 + "\n")
        
        metadata = final_state['final_document']['metadata']
        
        print("📊 Statistiken:")
        print(f"   Gesamt-Zeit: {final_state['total_processing_time']:.2f}s")
        print(f"   OCR-Tool: {metadata.get('tool_used', 'N/A')}")
        print(f"   Seiten: {metadata.get('pages', 0)}")
        print(f"   Segmente: {len(final_state['segments'])}")
        print(f"   Varianten gesamt: {metadata['total_variants']}")
        print(f"   Varianten valide: {metadata['valid_variants']}")
        print(f"   Validierung: {metadata['validation_rate']*100:.1f}%")
        print()
        
        # Speichere Output
        output_path = Config.DATA_OUTPUT_PATH / 'langgraph' / test_pdf.stem
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # JSON
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(final_state['final_document'], f, indent=2, ensure_ascii=False)
        
        # TXT
        txt_path = output_path.with_suffix('.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(final_state['final_document']['text_output'])
        
        print("📁 Output-Dateien:")
        print(f"   {json_path}")
        print(f"   {txt_path}")
        
    else:
        print("❌ WORKFLOW FEHLGESCHLAGEN")
        print("="*70 + "\n")
        print(f"Phase: {final_state['current_phase']}")
        print(f"Fehler: {final_state.get('errors', [])}")
    
    print("\n" + "="*70)
    print("🎉 Test abgeschlossen!")
    print("="*70 + "\n")


if __name__ == '__main__':
    test_complete_workflow()