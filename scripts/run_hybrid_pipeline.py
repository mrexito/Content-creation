"""
Hybrid Pipeline Runner – für Frontend-Integration

Analog zu run_langchain_pipeline.py und run_langgraph_pipeline.py.

Usage:
    python scripts/run_hybrid_pipeline.py \
        --pdf data/input/math/equations_simple.pdf \
        --domain math \
        --variants 2 \
        --retries 2 \
        --output-dir data/output/hybrid/run_xyz \
        --progress data/output/hybrid/run_xyz/progress.json \
        --run-id run_xyz
"""
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.logger import setup_logger
from hybrid_prototype.pipeline import get_pipeline

logger = setup_logger(__name__)

PHASES = ["parsing", "segmentation", "classification", "rewriting", "validation", "assembly"]
PHASE_WEIGHTS = [10, 15, 15, 40, 15, 5]  # sum = 100


def write_progress(
    progress_path: Path,
    status: str,
    current_phase: str,
    phases_completed: list,
    progress_percent: int,
    metadata: dict,
) -> None:
    data = {
        "status": status,
        "current_phase": current_phase,
        "phases_completed": phases_completed,
        "progress_percent": progress_percent,
        "metadata": metadata,
    }
    progress_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def phase_progress(phase_name: str) -> int:
    idx = PHASES.index(phase_name) if phase_name in PHASES else 0
    return sum(PHASE_WEIGHTS[:idx])


def transform_segments(segments_with_variants: list) -> list:
    """Transformiert Pipeline-Segmente ins Frontend-SegmentResult-Format."""
    result = []
    for seg in segments_with_variants:
        orig = seg.get("segment", {})
        raw_variants = seg.get("variants", [])

        transformed_variants = []
        for vi, v in enumerate(raw_variants):
            val = v.get("validation", {})
            transformed_variants.append(
                {
                    "variant_id": v.get("variant_id", vi + 1),
                    "text": v.get("text", ""),
                    "is_valid": val.get("is_valid", False),
                    "validation_issues": val.get("issues", []),
                }
            )

        valid_count = sum(1 for v in transformed_variants if v["is_valid"])
        result.append(
            {
                "original_segment": {
                    "text": orig.get("text", "") if isinstance(orig, dict) else str(orig),
                    "type": orig.get("type", "unknown") if isinstance(orig, dict) else "unknown",
                },
                "classification": seg.get("classification", {}),
                "validated_variants": transformed_variants,
                "validation_statistics": {
                    "total": len(transformed_variants),
                    "valid": valid_count,
                    "avg_diversity": 0.0,
                },
            }
        )
    return result


def main():
    parser = argparse.ArgumentParser(description="Run Hybrid Pipeline")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--domain", default="auto")
    parser.add_argument("--variants", type=int, default=2)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--no-smoothing", action="store_true")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--progress", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--ocr-tool", default="auto",
                        choices=["auto", "tesseract", "mistral"],
                        help="OCR tool: auto | tesseract | mistral")
    parser.add_argument("--llm-provider", default="auto",
                        choices=["auto", "openai", "bfh"],
                        help="LLM provider: auto | openai | bfh")
    parser.add_argument("--llm-model", default="",
                        help="LLM model name (empty = provider default)")
    parser.add_argument("--pre-parsed-text", type=Path, default=None,
                        help="Pfad zu ocr_result.json (überspringt eigenen Parsing-Schritt)")
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.progress
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialise OCR and LLM singletons with CLI settings
    from common.ocr_handler import reset_ocr_handler, get_ocr_handler
    from common.llm_handler import reset_llm_handler, get_llm_handler
    reset_ocr_handler()
    get_ocr_handler(default_tool=args.ocr_tool)
    reset_llm_handler()
    get_llm_handler(
        provider=args.llm_provider,
        model=args.llm_model if args.llm_model else None,
    )

    domain = None if args.domain == "auto" else args.domain

    # Load shared OCR result if provided
    pre_parsed_text = None
    pre_parsed_meta = None
    if args.pre_parsed_text and args.pre_parsed_text.exists():
        try:
            ocr_data = json.loads(args.pre_parsed_text.read_text())
            if ocr_data.get("success"):
                pre_parsed_text = ocr_data["text"]
                pre_parsed_meta = {
                    "tool_used": ocr_data.get("tool_used", "shared"),
                    "pages": ocr_data.get("pages", 0),
                    "processing_time": ocr_data.get("processing_time", 0),
                    "char_count": ocr_data.get("char_count", 0),
                    "shared_ocr": True,
                }
                logger.info(
                    f"Verwende geteiltes OCR-Ergebnis: {pre_parsed_meta['char_count']} Zeichen"
                )
            else:
                logger.error(f"Geteiltes OCR fehlgeschlagen: {ocr_data.get('error')}")
                write_progress(progress_path, "error", "error", [], 0, {
                    "pdf_name": args.pdf.name, "run_id": args.run_id, "framework": "hybrid",
                    "domain": args.domain, "ocr_tool": args.ocr_tool,
                    "llm_provider": args.llm_provider, "llm_model": args.llm_model or "default",
                    "error": f"OCR fehlgeschlagen: {ocr_data.get('error', 'Unbekannt')}",
                })
                sys.exit(1)
        except Exception as e:
            logger.warning(f"Konnte pre-parsed-text nicht lesen: {e}. Führe eigenes OCR durch.")

    base_meta = {
        "pdf_name": args.pdf.name,
        "run_id": args.run_id,
        "framework": "hybrid",
        "domain": args.domain,
        "ocr_tool": args.ocr_tool,
        "llm_provider": args.llm_provider,
        "llm_model": args.llm_model or "default",
    }

    completed_phases_hybrid: list = ["parsing"] if pre_parsed_text is not None else []

    if pre_parsed_text is not None:
        write_progress(progress_path, "running", "segmentation", ["parsing"], 10, base_meta)
    else:
        write_progress(progress_path, "running", "parsing", [], 0, base_meta)

    def on_phase_complete(phase: str) -> None:
        if phase not in completed_phases_hybrid:
            completed_phases_hybrid.append(phase)
        remaining = [p for p in PHASES if p not in completed_phases_hybrid]
        next_phase = remaining[0] if remaining else "assembly"
        pct = phase_progress(next_phase) if next_phase in PHASES else 95
        write_progress(progress_path, "running", next_phase, list(completed_phases_hybrid), pct, base_meta)

    try:
        pipeline = get_pipeline(
            domain=domain,
            num_variants=args.variants,
            max_retries=args.retries,
            apply_smoothing=not args.no_smoothing,
        )

        result = pipeline.process_pdf(
            pdf_path=args.pdf,
            output_path=output_dir / args.run_id,
            pre_parsed_text=pre_parsed_text,
            pre_parsed_meta=pre_parsed_meta,
            progress_callback=on_phase_complete,
        )

        if not result["success"]:
            raise RuntimeError(result.get("error", "Unbekannter Fehler"))

        # Transformiere Segmente für Frontend
        assembled_doc = result.get("assembled_document") or {}
        segments_raw = []

        # Hole Segmente aus State (über assembled_document.segments)
        for seg in assembled_doc.get("segments", []):
            segments_raw.append(
                {
                    "segment": {
                        "text": seg.get("original", ""),
                        "type": seg.get("segment_type", "unknown"),
                    },
                    "classification": seg.get("classification", {}),
                    "variants": [
                        {
                            "variant_id": v.get("variant_id"),
                            "text": v.get("text", ""),
                            "validation": {
                                "is_valid": True,  # Nur valide Varianten im assembled_document
                                "issues": [],
                                "score": v.get("validation_score", 1.0),
                            },
                        }
                        for v in seg.get("variants", [])
                    ],
                }
            )

        transformed = transform_segments(segments_raw)

        stats = result.get("statistics", {})
        graph_stats = stats.get("graph", {})
        preproc_stats = stats.get("preprocessing", {})

        total_valid = graph_stats.get("total_valid", 0)
        total_invalid = graph_stats.get("total_invalid", 0)
        total_variants = total_valid + total_invalid

        # PDF-Generierung: Aufgaben-PDF und Lösungs-PDF
        tasks_path = output_dir / "tasks.pdf"
        solutions_path = output_dir / "solutions.pdf"
        pdf_files = None
        try:
            from common.pdf_generator import PdfGenerator
            _generator = PdfGenerator()
            _generator.generate_tasks_pdf(assembled_doc, tasks_path)
            _generator.generate_solutions_pdf(assembled_doc, solutions_path)
            pdf_files = {"tasks": str(tasks_path), "solutions": str(solutions_path)}
        except Exception as pdf_err:
            logger.warning(f"PDF-Generierung fehlgeschlagen: {pdf_err}")

        # Ergebnis im Frontend-Format (identisch zu LangChain/LangGraph)
        frontend_result: dict = {
            "success": True,
            "framework": "hybrid",
            "domain": args.domain,
            "pdf_name": args.pdf.name,
            "metrics": {
                "total_time": stats.get("total_time", 0.0),
                "ocr_time": preproc_stats.get("ocr_time", 0),
                "ocr_tool": preproc_stats.get("ocr_tool", "unknown"),
                "num_segments": len(transformed),
                "total_variants": total_variants,
                "valid_variants": total_valid,
                "validation_rate": graph_stats.get("validation_rate", 0.0),
            },
            "segments": transformed,
            "output_files": result.get("output_files", []),
        }
        if pdf_files:
            frontend_result["pdf_files"] = pdf_files

        result_path = output_dir / "result.json"
        result_path.write_text(
            json.dumps(frontend_result, indent=2, ensure_ascii=False)
        )

        write_progress(
            progress_path,
            "complete",
            "complete",
            PHASES,
            100,
            {**base_meta, "result_path": str(result_path)},
        )

        logger.info(f"✅ Hybrid Pipeline Runner abgeschlossen → {result_path}")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Hybrid Pipeline Runner fehlgeschlagen: {e}")
        write_progress(
            progress_path,
            "error",
            "error",
            [],
            0,
            {**base_meta, "error": str(e)},
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
