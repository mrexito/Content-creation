"""
Testet den kompletten Hybrid-Prototyp (alle drei Phasen)

Analog zu scripts/test_langchain_chains.py und scripts/test_langgraph_complete.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.config import Config
from common.logger import setup_logger
from hybrid_prototype.pipeline import get_pipeline

logger = setup_logger(__name__)


def test_hybrid_pipeline():
    """Testet die komplette Hybrid-Pipeline: PDF → 3 Phasen → Output"""

    print("=" * 70)
    print("HYBRID PROTOTYP – Vollständiger Test")
    print("LangChain Preprocessing + LangGraph StateGraph + LangChain Postprocessing")
    print("=" * 70 + "\n")

    # Test-PDF ermitteln
    test_pdf = Config.DATA_INPUT_PATH / "math" / "equations_simple.pdf"
    if not test_pdf.exists():
        # Fallback: erstes verfügbares PDF
        for domain in ["math", "languages", "economics"]:
            candidates = list((Config.DATA_INPUT_PATH / domain).glob("*.pdf"))
            if candidates:
                test_pdf = candidates[0]
                break

    if not test_pdf.exists():
        print("❌ Kein Test-PDF gefunden.")
        print("   Bitte erst ausführen: python scripts/generate_test_pdfs.py")
        return False

    print(f"📄 Test-PDF: {test_pdf}\n")

    # Pipeline initialisieren
    pipeline = get_pipeline(
        domain="math",
        num_variants=2,
        max_retries=1,
    )

    # Ausführen
    result = pipeline.process_pdf(test_pdf)

    # Ergebnis ausgeben
    print("\n" + "=" * 70)
    if result["success"]:
        stats = result["statistics"]
        graph_stats = stats.get("graph", {})
        pre_stats = stats.get("preprocessing", {})

        print("✅ HYBRID PIPELINE ERFOLGREICH")
        print("=" * 70)
        print(f"\n📊 Statistiken:")
        print(f"   Gesamtzeit:           {stats.get('total_time', 0):.2f}s")
        print(f"\n   Phase 1 (LangChain Preprocessing):")
        print(f"     OCR-Tool:           {pre_stats.get('ocr_tool', 'n/a')}")
        print(f"     Segmente:           {pre_stats.get('segments', 0)}")
        print(f"\n   Phase 2 (LangGraph):")
        print(f"     Valide Varianten:   {graph_stats.get('total_valid', 0)}")
        print(f"     Invalide Varianten: {graph_stats.get('total_invalid', 0)}")
        print(f"     Validation-Rate:    {graph_stats.get('validation_rate', 0) * 100:.1f}%")
        print(f"     Retry-Counts:       {graph_stats.get('retry_counts', {})}")
        print(f"\n📁 Output-Dateien:")
        for f in result.get("output_files", []):
            print(f"   → {f}")

        # Stichprobe einer Variante
        doc = result.get("assembled_document") or {}
        segments = doc.get("segments") or []
        if segments:
            seg = segments[0]
            variants = seg.get("variants") or []
            print(f"\n📝 Stichprobe (Segment 1 von {len(segments)}):")
            print(f"   Original: {seg.get('original', '')[:80]}...")
            if variants:
                v = variants[0]
                print(f"   Variante 1: {v.get('text', '')[:80]}...")

        print()
        return True

    else:
        print("❌ HYBRID PIPELINE FEHLGESCHLAGEN")
        print("=" * 70)
        print(f"   Fehler: {result.get('error')}")
        errors = result.get("statistics", {}).get("errors", [])
        for e in errors:
            print(f"   ⚠️  {e}")
        print()
        return False


if __name__ == "__main__":
    success = test_hybrid_pipeline()
    sys.exit(0 if success else 1)
