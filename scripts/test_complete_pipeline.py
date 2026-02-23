"""
Test Complete LangChain Pipeline
End-to-End: PDF → Varianten-Dokument

Usage:
    python test_complete_pipeline.py                  # Standard: math
    python test_complete_pipeline.py math
    python test_complete_pipeline.py economics
    python test_complete_pipeline.py languages
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from langchain_prototype.pipeline import get_pipeline

INPUTS = {
    'math': {
        'pdf': 'math/equations_simple.pdf',
        'domain': 'math',
        'label': 'Mathematics',
    },
    'economics': {
        'pdf': 'economics/balance_sheet.pdf',
        'domain': 'economics',
        'label': 'Economics',
    },
    'languages': {
        'pdf': 'languages/grammar_exercise.pdf',
        'domain': 'languages',
        'label': 'Languages',
    },
}

def test_complete_pipeline(input_key: str = 'math'):
    """Testet die komplette Pipeline"""

    if input_key not in INPUTS:
        print(f"Unbekannter Input '{input_key}'. Verfügbar: {', '.join(INPUTS)}")
        sys.exit(1)

    cfg = INPUTS[input_key]
    test_pdf = Config.DATA_INPUT_PATH / cfg['pdf']

    print("="*70)
    print("COMPLETE LANGCHAIN PIPELINE TEST")
    print("="*70 + "\n")

    if not test_pdf.exists():
        print(f"Test-PDF nicht gefunden: {test_pdf}")
        return

    print(f"Input:    {test_pdf}")
    print(f"Domain:   {cfg['label']}")
    print(f"Varianten: 2 pro Segment\n")

    pipeline = get_pipeline(domain=cfg['domain'], num_variants=2)

    print("Starte Pipeline...\n")
    result = pipeline.process_pdf(test_pdf)

    print("\n" + "="*70)

    if result['success']:
        print("PIPELINE ERFOLGREICH!")
        print("="*70 + "\n")

        stats = result['statistics']

        print("Statistiken:")
        print(f"   Gesamt-Zeit: {stats['total_time']:.2f}s")
        print(f"   Parsing: {stats['parsing']['processing_time']:.2f}s")
        print(f"   Tool: {stats['parsing']['tool_used']}")
        print(f"   Seiten: {stats['parsing']['pages']}")
        print(f"   Segmente: {stats['segmentation']['num_segments']}")
        print(f"   Segmente mit Varianten: {stats['assembly']['segments_with_variants']}")
        print(f"   Valide Varianten: {stats['assembly']['valid_variants']}/{stats['assembly']['total_variants']}")
        print()

        print("Output-Dateien:")
        for file in result['output_files']:
            print(f"   {file}")

        print("\n" + "="*70)
        print("Test abgeschlossen!")
        print("="*70 + "\n")
    else:
        print("PIPELINE FEHLGESCHLAGEN")
        print("="*70 + "\n")
        print(f"Fehler: {result.get('error')}")
        print()

if __name__ == '__main__':
    key = sys.argv[1] if len(sys.argv) > 1 else 'math'
    test_complete_pipeline(key)