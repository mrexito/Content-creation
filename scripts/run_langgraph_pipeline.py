"""
LangGraph Pipeline Runner – für Frontend-Integration

Usage:
    python scripts/run_langgraph_pipeline.py \
        --pdf data/input/math/equations_simple.pdf \
        --domain math \
        --variants 2 \
        --retries 3 \
        --output-dir data/output/langgraph/run_xyz \
        --progress data/output/langgraph/run_xyz/progress.json \
        --run-id run_xyz
"""
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from common.logger import setup_logger
from langgraph_prototype.graph import create_workflow_graph
from langgraph_prototype.state.workflow_state import create_initial_state

logger = setup_logger(__name__)

PHASES = ["parsing", "segmentation", "classification", "rewriting", "validation", "assembly"]
PHASE_WEIGHTS = [10, 15, 15, 40, 15, 5]

PHASE_FROM_STATE = {
    "initialized": "parsing",
    "parsing": "parsing",
    "parsing_complete": "parsing",
    "segmentation": "segmentation",
    "segmentation_complete": "segmentation",
    "classification": "classification",
    "classification_complete": "classification",
    "rewriting": "rewriting",
    "rewriting_complete": "rewriting",
    "validation_failed": "validation",
    "validation_complete": "validation",
    "assembly_complete": "assembly",
    "error": "error",
}


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
    """Transform LangGraph state segments_with_variants to frontend SegmentResult format."""
    result = []
    for seg in segments_with_variants:
        orig = seg.get('segment', {})
        raw_variants = seg.get('variants', [])

        transformed_variants = []
        for vi, v in enumerate(raw_variants):
            val = v.get('validation', {})
            transformed_variants.append({
                'variant_id': v.get('variant_id', vi + 1),
                'text': v.get('text', ''),
                'is_valid': val.get('is_valid', False),
                'validation_issues': val.get('issues', []),
            })

        skipped = seg.get('skipped', False)
        valid_count = sum(1 for v in transformed_variants if v['is_valid'])
        result.append({
            'original_segment': {
                'text': orig.get('text', '') if isinstance(orig, dict) else str(orig),
                'type': orig.get('type', 'unknown') if isinstance(orig, dict) else 'unknown',
            },
            'classification': seg.get('classification', {}),
            'validated_variants': transformed_variants,
            'validation_statistics': {
                'total': len(transformed_variants),
                'valid': valid_count,
                'avg_diversity': 0.0,
                'skipped': skipped,
            },
        })
    return result


def main():
    parser = argparse.ArgumentParser(description="Run LangGraph Pipeline")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--domain", default="auto")
    parser.add_argument("--variants", type=int, default=2)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--ocr-tool", default="auto",
                        choices=["auto", "tesseract", "mistral"])
    parser.add_argument("--llm-provider", default="auto",
                        choices=["auto", "openai", "bfh"])
    parser.add_argument("--llm-model", default="")
    parser.add_argument("--pre-parsed-text", type=Path, default=None,
                        help="Pfad zu ocr_result.json (überspringt eigenen Parsing-Schritt)")
    args = parser.parse_args()

    pdf_path = args.pdf
    domain = None if args.domain == "auto" else args.domain
    output_dir = args.output_dir
    progress_path = args.progress

    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    # Singleton-Handler mit CLI-Einstellungen initialisieren
    from common.ocr_handler import reset_ocr_handler, get_ocr_handler
    from common.llm_handler import reset_llm_handler, get_llm_handler
    # Config-Override – wichtig falls Nodes intern LCEL-Komponenten nutzen
    # und für konsistente Provider-/Modell-Auflösung über alle Pfade.
    Config.apply_llm_cli_overrides(args.llm_provider, args.llm_model)
    reset_ocr_handler()
    get_ocr_handler(default_tool=args.ocr_tool)
    reset_llm_handler()
    get_llm_handler(
        provider=args.llm_provider,
        model=args.llm_model if args.llm_model else None,
    )

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
                    "pdf_name": pdf_path.name, "framework": "langgraph",
                    "domain": args.domain, "run_id": args.run_id,
                    "ocr_tool": args.ocr_tool, "llm_provider": args.llm_provider,
                    "llm_model": args.llm_model or "default",
                    "error": f"OCR fehlgeschlagen: {ocr_data.get('error', 'Unbekannt')}",
                })
                sys.exit(1)
        except Exception as e:
            logger.warning(f"Konnte pre-parsed-text nicht lesen: {e}. Führe eigenes OCR durch.")

    base_meta = {
        "pdf_name": pdf_path.name,
        "framework": "langgraph",
        "domain": args.domain,
        "run_id": args.run_id,
        "ocr_tool": args.ocr_tool,
        "llm_provider": args.llm_provider,
        "llm_model": args.llm_model or "default",
    }

    # Write initial progress – if parsing already done, skip to segmentation
    if pre_parsed_text is not None:
        write_progress(progress_path, "running", "segmentation", ["parsing"], 10, base_meta)
    else:
        write_progress(progress_path, "running", "parsing", [], 0, base_meta)

    try:
        workflow = create_workflow_graph()

        initial_state = create_initial_state(
            pdf_path=str(pdf_path),
            domain=domain,
            num_variants=args.variants,
            max_retries=args.retries,
        )

        # Inject shared OCR result so parsing_node skips OCR
        if pre_parsed_text is not None:
            initial_state['raw_text'] = pre_parsed_text
            initial_state['ocr_metadata'] = pre_parsed_meta
            initial_state['current_phase'] = 'parsing_complete'

        # LangGraph supports streaming – use stream to emit per-node progress
        completed_phases = ["parsing"] if pre_parsed_text is not None else []
        final_state = None

        for state in workflow.stream(initial_state):
            # state is a dict: {node_name: state_snapshot}
            node_name = list(state.keys())[0]
            node_state = state[node_name]
            current_phase_raw = node_state.get("current_phase", "")

            phase = PHASE_FROM_STATE.get(current_phase_raw, node_name)
            if phase in PHASES and phase not in completed_phases:
                completed_phases.append(phase)

            # Determine next phase to show
            remaining = [p for p in PHASES if p not in completed_phases]
            next_phase = remaining[0] if remaining else "assembly"
            pct = phase_progress(next_phase) if next_phase in PHASES else 95

            write_progress(
                progress_path, "running", next_phase,
                completed_phases, pct, base_meta
            )
            final_state = node_state

        if final_state is None:
            raise RuntimeError("No state produced by workflow")

        if final_state.get("current_phase") != "assembly_complete":
            errors = final_state.get("errors", [])
            raise RuntimeError(f"Workflow failed: {errors}")

        # Save output
        final_doc = final_state["final_document"]
        json_path = output_dir / f"{pdf_path.stem}.json"
        txt_path = output_dir / f"{pdf_path.stem}.txt"

        json_path.write_text(json.dumps(final_doc, indent=2, ensure_ascii=False))
        if final_doc.get("text_output"):
            txt_path.write_text(final_doc["text_output"])

        # PDF-Generierung: Aufgaben-PDF und Lösungs-PDF
        from common.pdf_generator import PdfGenerator
        _generator = PdfGenerator()
        tasks_path = output_dir / "tasks.pdf"
        solutions_path = output_dir / "solutions.pdf"
        _generator.generate_tasks_pdf(final_doc, tasks_path)
        _generator.generate_solutions_pdf(final_doc, solutions_path)

        # Build frontend result.json
        meta = final_doc.get("metadata", {})
        segments_raw = final_state.get("segments_with_variants") or []

        frontend_result = {
            "success": True,
            "framework": "langgraph",
            "domain": args.domain,
            "pdf_name": pdf_path.name,
            "metrics": {
                "total_time": final_state.get("total_processing_time", 0),
                "ocr_time": (final_state.get("ocr_metadata") or {}).get("processing_time", 0),
                "ocr_tool": (final_state.get("ocr_metadata") or {}).get("tool_used", "unknown"),
                "num_segments": len(final_state.get("segments") or []),
                "total_variants": meta.get("total_variants", 0),
                "valid_variants": meta.get("valid_variants", 0),
                "validation_rate": meta.get("validation_rate", 0),
            },
            "segments": transform_segments(segments_raw),
            "output_files": [str(json_path), str(txt_path)],
            "pdf_files": {
                "tasks": str(tasks_path),
                "solutions": str(solutions_path),
            },
        }

        result_path = output_dir / "result.json"
        result_path.write_text(json.dumps(frontend_result, indent=2, ensure_ascii=False))

        write_progress(
            progress_path,
            "complete",
            "complete",
            PHASES,
            100,
            {**base_meta, "result_path": str(result_path)},
        )
        logger.info("LangGraph pipeline complete")
        sys.exit(0)

    except Exception as exc:
        logger.error(f"LangGraph pipeline failed: {exc}")
        write_progress(
            progress_path,
            "error",
            "error",
            [],
            0,
            {**base_meta, "error": str(exc)},
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
