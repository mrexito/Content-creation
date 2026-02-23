"""
Testet LangGraph mit Retry-Loops
"""
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from langgraph_prototype.state.workflow_state import create_initial_state
from langgraph_prototype.graph import create_workflow_graph


def test_retry_loops():
    """Testet Retry-Loops im LangGraph Workflow"""
    
    print("="*70)
    print("LANGGRAPH WITH RETRY-LOOPS TEST")
    print("="*70 + "\n")
    
    # Test-PDF (Languages - hat niedrige Validation!)
    test_pdf = Config.DATA_INPUT_PATH / 'languages' / 'grammar_exercise.pdf'
    
    if not test_pdf.exists():
        print(f"❌ Test-PDF nicht gefunden: {test_pdf}")
        return
    
    print(f"📄 Input: {test_pdf.name}")
    print(f"🎯 Domain: languages (niedrige Validation → mehr Retries!)")
    print(f"🔄 Max Retries: 3\n")
    
    # Erstelle Workflow
    print("🔨 Erstelle Workflow mit Retry-Loops...")
    workflow = create_workflow_graph()
    print("✓ Workflow bereit\n")
    
    # Initialer State
    initial_state = create_initial_state(
        pdf_path=str(test_pdf),
        domain='languages',
        num_variants=2,
        max_retries=3
    )
    
    # Führe Workflow aus
    print("🚀 Führe Workflow aus (mit automatischen Retries)...\n")
    
    final_state = workflow.invoke(initial_state)
    
    # Ergebnisse
    print("\n" + "="*70)
    
    if final_state['current_phase'] == 'assembly_complete':
        print("✅ WORKFLOW MIT RETRY-LOOPS ERFOLGREICH!")
        print("="*70 + "\n")
        
        metadata = final_state['final_document']['metadata']
        retry_counts = final_state.get('retry_counts', {})
        
        print("📊 Statistiken:")
        print(f"   Gesamt-Zeit: {final_state['total_processing_time']:.2f}s")
        print(f"   Segmente: {len(final_state['segments'])}")
        print(f"   Varianten gesamt: {metadata['total_variants']}")
        print(f"   Varianten valide: {metadata['valid_variants']}")
        print(f"   Validierung: {metadata['validation_rate']*100:.1f}%")
        print()
        
        # Retry-Statistik
        if retry_counts:
            print("🔄 Retry-Statistik:")
            total_retries = sum(retry_counts.values())
            print(f"   Segmente mit Retries: {len(retry_counts)}")
            print(f"   Gesamte Retries: {total_retries}")
            for seg_idx, count in sorted(retry_counts.items()):
                print(f"   Segment {seg_idx}: {count} Retries")
            print()
        else:
            print("✓ Keine Retries nötig (alle Varianten sofort valide)\n")
        
        # Speichere Output
        output_path = Config.DATA_OUTPUT_PATH / 'langgraph_retry' / test_pdf.stem
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        json_path = output_path.with_suffix('.json')
        txt_path = output_path.with_suffix('.txt')
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                **final_state['final_document'],
                'retry_statistics': {
                    'retry_counts': retry_counts,
                    'total_retries': sum(retry_counts.values()) if retry_counts else 0
                }
            }, f, indent=2, ensure_ascii=False)
        
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
    test_retry_loops()