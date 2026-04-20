"""
Hybrid Prototype – Einstiegspunkt

Analog zu run_langchain.py und run_langgraph.py.

Usage:
    python src/hybrid_prototype/run_hybrid.py
    python src/hybrid_prototype/run_hybrid.py --domain math --variants 2
    python src/hybrid_prototype/run_hybrid.py --pdf data/input/economics/case_study.pdf
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import Config
from common.logger import setup_logger
from hybrid_prototype.pipeline import get_pipeline

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Hybrid Prototype (LangChain + LangGraph)"
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=None,
        help="Pfad zur Input-PDF (default: erstes verfügbares Test-PDF)",
    )
    parser.add_argument(
        "--domain",
        default=None,
        choices=["math", "languages", "economics"],
        help="Domäne (default: Auto-Detect)",
    )
    parser.add_argument(
        "--variants",
        type=int,
        default=3,
        help="Anzahl Varianten pro Segment (default: 3)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Maximale Retry-Iterationen im LangGraph-Loop (default: 2)",
    )
    args = parser.parse_args()

    # Test-PDF auswählen
    pdf_path = args.pdf
    if pdf_path is None:
        for domain_dir in ["math", "languages", "economics"]:
            candidate = Config.DATA_INPUT_PATH / domain_dir
            if candidate.exists():
                pdfs = list(candidate.glob("*.pdf"))
                if pdfs:
                    pdf_path = pdfs[0]
                    break

    if pdf_path is None or not pdf_path.exists():
        logger.error(
            "Keine Test-PDF gefunden. Bitte erst ausführen: "
            "python scripts/generate_test_pdfs.py"
        )
        sys.exit(1)

    logger.info(f"📄 Input: {pdf_path}")
    logger.info(f"   Domain:   {args.domain or 'auto'}")
    logger.info(f"   Varianten:{args.variants}")
    logger.info(f"   Retries:  {args.retries}")

    pipeline = get_pipeline(
        domain=args.domain,
        num_variants=args.variants,
        max_retries=args.retries,
    )

    result = pipeline.process_pdf(pdf_path)

    if result["success"]:
        stats = result["statistics"]
        graph_stats = stats.get("graph", {})
        print("\n" + "=" * 60)
        print("✅ HYBRID PIPELINE ERFOLGREICH")
        print("=" * 60)
        print(f"  Verarbeitungszeit:    {stats.get('total_time', 0):.2f}s")
        print(f"  Segmente:             {stats.get('preprocessing', {}).get('segments', 0)}")
        print(f"  Valide Varianten:     {graph_stats.get('total_valid', 0)}")
        print(f"  Validation-Rate:      {graph_stats.get('validation_rate', 0) * 100:.1f}%")
        print(f"\n  Output-Dateien:")
        for f in result.get("output_files", []):
            print(f"    → {f}")
        print("=" * 60 + "\n")
    else:
        print("\n" + "=" * 60)
        print("❌ HYBRID PIPELINE FEHLGESCHLAGEN")
        print("=" * 60)
        print(f"  Fehler: {result.get('error')}")
        print("=" * 60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
