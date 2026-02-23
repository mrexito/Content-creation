"""
Systematische Evaluation: LangChain vs LangGraph
Testet beide Prototypen mit allen Domains (math, languages, economics)
"""
from pathlib import Path
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from langchain_prototype.pipeline import get_pipeline as get_langchain_pipeline
from langgraph_prototype.state.workflow_state import create_initial_state
from langgraph_prototype.graph import create_workflow_graph

# Test-Konfiguration
TEST_CONFIG = {
    'math': {
        'pdf': 'equations_simple.pdf',
        'domain': 'math',
        'num_variants': 2
    },
    'languages': {
        'pdf': 'grammar_exercise.pdf',
        'domain': 'languages',
        'num_variants': 2
    },
    'economics': {
        'pdf': 'balance_sheet.pdf',
        'domain': 'economics',
        'num_variants': 2
    }
}


def run_langchain_test(domain_name: str, config: dict) -> dict:
    """
    Führt LangChain-Test für eine Domain aus
    
    Returns:
        Dict mit results und metadata
    """
    print(f"\n{'='*70}")
    print(f"LangChain - {domain_name.upper()}")
    print(f"{'='*70}\n")
    
    pdf_path = Config.DATA_INPUT_PATH / domain_name / config['pdf']
    
    if not pdf_path.exists():
        print(f"❌ PDF nicht gefunden: {pdf_path}")
        return {
            'success': False,
            'error': f'PDF not found: {pdf_path}',
            'domain': domain_name,
            'framework': 'langchain'
        }
    
    try:
        # Pipeline erstellen
        pipeline = get_langchain_pipeline(
            domain=config['domain'],
            num_variants=config['num_variants']
        )
        
        # Ausführen
        start_time = time.time()
        result = pipeline.process_pdf(pdf_path)
        total_time = time.time() - start_time
        
        if result['success']:
            stats = result['statistics']
            
            print(f"✅ Erfolgreich!")
            print(f"   Zeit: {total_time:.2f}s")
            print(f"   Segmente: {stats['segmentation']['num_segments']}")
            print(f"   Varianten: {stats['assembly']['valid_variants']}/{stats['assembly']['total_variants']}")
            print(f"   Validierung: {stats['assembly']['valid_variants']/stats['assembly']['total_variants']*100:.1f}%")
            
            return {
                'success': True,
                'framework': 'langchain',
                'domain': domain_name,
                'pdf_path': str(pdf_path),
                'total_time': total_time,
                'num_segments': stats['segmentation']['num_segments'],
                'total_variants': stats['assembly']['total_variants'],
                'valid_variants': stats['assembly']['valid_variants'],
                'validation_rate': stats['assembly']['valid_variants']/stats['assembly']['total_variants'],
                'ocr_tool': stats['parsing']['tool_used'],
                'ocr_time': stats['parsing']['processing_time'],
                'output_files': result['output_files']
            }
        else:
            print(f"❌ Fehlgeschlagen: {result.get('error')}")
            return {
                'success': False,
                'framework': 'langchain',
                'domain': domain_name,
                'error': result.get('error')
            }
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {
            'success': False,
            'framework': 'langchain',
            'domain': domain_name,
            'error': str(e)
        }


def run_langgraph_test(domain_name: str, config: dict) -> dict:
    """
    Führt LangGraph-Test für eine Domain aus
    
    Returns:
        Dict mit results und metadata
    """
    print(f"\n{'='*70}")
    print(f"LangGraph - {domain_name.upper()}")
    print(f"{'='*70}\n")
    
    pdf_path = Config.DATA_INPUT_PATH / domain_name / config['pdf']
    
    if not pdf_path.exists():
        print(f"❌ PDF nicht gefunden: {pdf_path}")
        return {
            'success': False,
            'error': f'PDF not found: {pdf_path}',
            'domain': domain_name,
            'framework': 'langgraph'
        }
    
    try:
        # Workflow erstellen
        workflow = create_workflow_graph()
        
        # Initial State
        initial_state = create_initial_state(
            pdf_path=str(pdf_path),
            domain=config['domain'],
            num_variants=config['num_variants']
        )
        
        # Ausführen
        start_time = time.time()
        final_state = workflow.invoke(initial_state)
        total_time = time.time() - start_time
        
        if final_state['current_phase'] == 'assembly_complete':
            metadata = final_state['final_document']['metadata']
            
            print(f"✅ Erfolgreich!")
            print(f"   Zeit: {total_time:.2f}s")
            print(f"   Segmente: {len(final_state['segments'])}")
            print(f"   Varianten: {metadata['valid_variants']}/{metadata['total_variants']}")
            print(f"   Validierung: {metadata['validation_rate']*100:.1f}%")
            
            # Speichere Output
            output_path = Config.DATA_OUTPUT_PATH / 'langgraph' / domain_name / pdf_path.stem
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            json_path = output_path.with_suffix('.json')
            txt_path = output_path.with_suffix('.txt')
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(final_state['final_document'], f, indent=2, ensure_ascii=False)
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(final_state['final_document']['text_output'])
            
            return {
                'success': True,
                'framework': 'langgraph',
                'domain': domain_name,
                'pdf_path': str(pdf_path),
                'total_time': total_time,
                'num_segments': len(final_state['segments']),
                'total_variants': metadata['total_variants'],
                'valid_variants': metadata['valid_variants'],
                'validation_rate': metadata['validation_rate'],
                'ocr_tool': metadata.get('tool_used', 'N/A'),
                'ocr_time': metadata.get('processing_time', 0),
                'output_files': [str(json_path), str(txt_path)]
            }
        else:
            print(f"❌ Fehlgeschlagen: {final_state.get('errors')}")
            return {
                'success': False,
                'framework': 'langgraph',
                'domain': domain_name,
                'error': final_state.get('errors')
            }
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {
            'success': False,
            'framework': 'langgraph',
            'domain': domain_name,
            'error': str(e)
        }


def generate_comparison_report(results: list) -> str:
    """Generiert Vergleichs-Report"""
    
    lines = []
    lines.append("=" * 80)
    lines.append("EVALUATION REPORT: LangChain vs LangGraph")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    
    # Gruppiere nach Domain
    domains = {}
    for r in results:
        domain = r['domain']
        if domain not in domains:
            domains[domain] = {}
        domains[domain][r['framework']] = r
    
    # Domain-by-Domain Comparison
    for domain_name, frameworks in domains.items():
        lines.append(f"\n## DOMAIN: {domain_name.upper()}")
        lines.append("-" * 80)
        
        lc = frameworks.get('langchain', {})
        lg = frameworks.get('langgraph', {})
        
        if lc.get('success') and lg.get('success'):
            lines.append(f"\n{'Metrik':<30} {'LangChain':<20} {'LangGraph':<20} {'Delta'}")
            lines.append("-" * 80)
            
            # Zeit
            lc_time = lc['total_time']
            lg_time = lg['total_time']
            delta_time = ((lg_time - lc_time) / lc_time * 100)
            lines.append(f"{'Total Time (s)':<30} {lc_time:<20.2f} {lg_time:<20.2f} {delta_time:+.1f}%")
            
            # OCR Zeit
            lines.append(f"{'OCR Time (s)':<30} {lc['ocr_time']:<20.2f} {lg['ocr_time']:<20.2f}")
            lines.append(f"{'OCR Tool':<30} {lc['ocr_tool']:<20} {lg['ocr_tool']:<20}")
            
            # Segmente
            lines.append(f"{'Segments':<30} {lc['num_segments']:<20} {lg['num_segments']:<20}")
            
            # Varianten
            lines.append(f"{'Total Variants':<30} {lc['total_variants']:<20} {lg['total_variants']:<20}")
            lines.append(f"{'Valid Variants':<30} {lc['valid_variants']:<20} {lg['valid_variants']:<20}")
            
            # Validierung
            lc_val = lc['validation_rate'] * 100
            lg_val = lg['validation_rate'] * 100
            lines.append(f"{'Validation Rate (%)':<30} {lc_val:<20.1f} {lg_val:<20.1f}")
            
        else:
            if not lc.get('success'):
                lines.append(f"\n❌ LangChain failed: {lc.get('error')}")
            if not lg.get('success'):
                lines.append(f"\n❌ LangGraph failed: {lg.get('error')}")
        
        lines.append("")
    
    # Gesamt-Statistik
    lines.append("\n## GESAMTSTATISTIK")
    lines.append("-" * 80)
    
    successful_lc = [r for r in results if r['framework'] == 'langchain' and r['success']]
    successful_lg = [r for r in results if r['framework'] == 'langgraph' and r['success']]
    
    if successful_lc and successful_lg:
        avg_time_lc = sum(r['total_time'] for r in successful_lc) / len(successful_lc)
        avg_time_lg = sum(r['total_time'] for r in successful_lg) / len(successful_lg)
        
        avg_val_lc = sum(r['validation_rate'] for r in successful_lc) / len(successful_lc) * 100
        avg_val_lg = sum(r['validation_rate'] for r in successful_lg) / len(successful_lg) * 100
        
        lines.append(f"\n{'Metrik':<30} {'LangChain':<20} {'LangGraph':<20} {'Delta'}")
        lines.append("-" * 80)
        lines.append(f"{'Durchschn. Zeit (s)':<30} {avg_time_lc:<20.2f} {avg_time_lg:<20.2f} {((avg_time_lg-avg_time_lc)/avg_time_lc*100):+.1f}%")
        lines.append(f"{'Durchschn. Validierung (%)':<30} {avg_val_lc:<20.1f} {avg_val_lg:<20.1f} {(avg_val_lg-avg_val_lc):+.1f}pp")
        lines.append(f"{'Erfolgreiche Tests':<30} {len(successful_lc):<20} {len(successful_lg):<20}")
    
    lines.append("\n" + "=" * 80)
    
    return "\n".join(lines)


def main():
    """Hauptfunktion: Führt alle Tests aus"""
    
    print("=" * 80)
    print("MULTI-DOMAIN EVALUATION: LangChain vs LangGraph")
    print("=" * 80)
    print(f"\nTesting {len(TEST_CONFIG)} domains with 2 frameworks each")
    print(f"Total tests: {len(TEST_CONFIG) * 2}\n")
    
    results = []
    
    # Für jede Domain: LangChain + LangGraph
    for domain_name, config in TEST_CONFIG.items():
        
        # LangChain
        lc_result = run_langchain_test(domain_name, config)
        results.append(lc_result)
        
        # LangGraph
        lg_result = run_langgraph_test(domain_name, config)
        results.append(lg_result)
    
    # Generiere Report
    print("\n\n" + "=" * 80)
    print("GENERATING COMPARISON REPORT")
    print("=" * 80)
    
    report = generate_comparison_report(results)
    print(report)
    
    # Speichere Ergebnisse
    output_dir = Config.DATA_OUTPUT_PATH / 'evaluation'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON (strukturiert)
    json_path = output_dir / f'evaluation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'test_config': TEST_CONFIG,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    # Report (lesbar)
    report_path = output_dir / f'comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📁 Ergebnisse gespeichert:")
    print(f"   {json_path}")
    print(f"   {report_path}")
    
    print("\n" + "=" * 80)
    print("✅ EVALUATION ABGESCHLOSSEN!")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()