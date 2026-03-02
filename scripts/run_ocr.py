"""
Führt OCR auf einem PDF durch und speichert das Ergebnis als JSON.
Wird vor den Framework-Pipelines aufgerufen damit OCR nur einmal läuft.

Usage:
    python scripts/run_ocr.py \
        --pdf data/input/math/equations_simple.pdf \
        --domain auto \
        --ocr-tool auto \
        --output data/output/shared/run_xyz/ocr_result.json
"""
import sys
import json
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.ocr_handler import get_ocr_handler, reset_ocr_handler
from common.logger import setup_logger

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Run OCR pre-processing")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--domain", default="auto")
    parser.add_argument("--ocr-tool", default="auto",
                        choices=["auto", "tesseract", "mistral"])
    parser.add_argument("--output", required=True, type=Path,
                        help="Pfad zum Output-JSON (ocr_result.json)")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    domain = None if args.domain == "auto" else args.domain

    reset_ocr_handler()
    ocr = get_ocr_handler(default_tool=args.ocr_tool)

    logger.info(f"Starte OCR: {args.pdf.name} mit Tool={args.ocr_tool}")
    start = time.time()

    result = ocr.pdf_to_text(args.pdf, domain=domain)

    # Tesseract-Fallback wenn Mistral 0 Zeichen zurückgibt (Rate-Limit)
    if result.get("success") and not (result.get("text") or "").strip():
        logger.warning("  ⚠ OCR lieferte keinen Text – Fallback auf Tesseract")
        reset_ocr_handler()
        ocr = get_ocr_handler(default_tool="tesseract")
        result = ocr.pdf_to_text(args.pdf, domain=domain)

    if not result["success"] or not (result.get("text") or "").strip():
        error_payload = {
            "success": False,
            "error": result.get("error") or "OCR lieferte keinen Text",
            "tool_used": result.get("tool_used", args.ocr_tool),
            "processing_time": time.time() - start,
        }
        args.output.write_text(
            json.dumps(error_payload, indent=2, ensure_ascii=False)
        )
        logger.error(f"OCR fehlgeschlagen: {error_payload['error']}")
        sys.exit(1)

    output_payload = {
        "success": True,
        "text": result["text"],
        "pages": result.get("pages", 0),
        "tool_used": result.get("tool_used", args.ocr_tool),
        "processing_time": result.get("processing_time", time.time() - start),
        "char_count": len(result["text"]),
        "word_count": len(result["text"].split()),
        "pdf_name": args.pdf.name,
        "domain": args.domain,
    }

    args.output.write_text(
        json.dumps(output_payload, indent=2, ensure_ascii=False)
    )
    logger.info(
        f"OCR erfolgreich: {output_payload['char_count']} Zeichen, "
        f"{output_payload['pages']} Seiten, {output_payload['processing_time']:.2f}s"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
