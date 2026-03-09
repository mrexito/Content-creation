"""
LangChain Pipeline Runner – für Frontend-Integration

Usage:
    python scripts/run_langchain_pipeline.py \
        --pdf data/input/math/equations_simple.pdf \
        --domain math \
        --variants 2 \
        --retries 3 \
        --output-dir data/output/langchain/run_xyz \
        --progress data/output/langchain/run_xyz/progress.json \
        --run-id run_xyz
"""
import sys
import json
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from common.constants import NON_REWRITABLE_TYPES
from common.logger import setup_logger
from langchain_prototype.pipeline import get_pipeline

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
    """Cumulative progress when a phase starts."""
    idx = PHASES.index(phase_name) if phase_name in PHASES else 0
    return sum(PHASE_WEIGHTS[:idx])


def transform_segments(segments_with_variants: list) -> list:
    """Transform pipeline segments_with_variants to frontend SegmentResult format."""
    result = []
    for seg in segments_with_variants:
        orig = seg.get('original_segment', {})
        raw_variants = seg.get('validated_variants', [])

        transformed_variants = []
        for vi, v in enumerate(raw_variants):
            val = v.get('validation', {})
            transformed_variants.append({
                'variant_id': v.get('variant_id', vi + 1),
                'text': v.get('text', ''),
                'is_valid': val.get('is_valid', False),
                'validation_issues': val.get('issues', []),
            })

        val_stats = seg.get('validation_statistics', {})
        skipped = val_stats.get('skipped', False)
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
    parser = argparse.ArgumentParser(description="Run LangChain Pipeline")
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
    reset_ocr_handler()
    get_ocr_handler(default_tool=args.ocr_tool)
    reset_llm_handler()
    get_llm_handler(
        provider=args.llm_provider,
        model=args.llm_model if args.llm_model else None,
    )

    # Load shared OCR result if provided
    pre_parsed_text = None
    pre_parsed_meta = {}
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
                    **{"pdf_name": pdf_path.name, "framework": "langchain",
                       "domain": args.domain, "run_id": args.run_id,
                       "ocr_tool": args.ocr_tool, "llm_provider": args.llm_provider,
                       "llm_model": args.llm_model or "default"},
                    "error": f"OCR fehlgeschlagen: {ocr_data.get('error', 'Unbekannt')}",
                })
                sys.exit(1)
        except Exception as e:
            logger.warning(f"Konnte pre-parsed-text nicht lesen: {e}. Führe eigenes OCR durch.")

    base_meta = {
        "pdf_name": pdf_path.name,
        "framework": "langchain",
        "domain": args.domain,
        "run_id": args.run_id,
        "ocr_tool": args.ocr_tool,
        "llm_provider": args.llm_provider,
        "llm_model": args.llm_model or "default",
    }

    def update(phase: str, completed: list):
        pct = phase_progress(phase)
        write_progress(progress_path, "running", phase, completed, pct, base_meta)

    try:
        # If parsing was already done via shared OCR, start at segmentation
        if pre_parsed_text is not None:
            update("segmentation", ["parsing"])
        else:
            update("parsing", [])

        pipeline = get_pipeline(domain=domain, num_variants=args.variants)

        # We wrap process_pdf to emit progress at each stage
        # Since LangChain pipeline is sequential, we track via a custom subclass
        class ProgressPipeline(pipeline.__class__):
            def process_pdf(self, pdf_path, output_path=None):
                completed = []

                def step(phase):
                    completed.append(phase)
                    next_phases = [p for p in PHASES if p not in completed]
                    nxt = next_phases[0] if next_phases else "assembly"
                    write_progress(
                        progress_path, "running", nxt, completed,
                        phase_progress(nxt) if nxt in PHASES else 95,
                        base_meta,
                    )

                # Run each step and emit progress
                import time as _time
                from pathlib import Path as _Path

                logger.info(f"Starte Pipeline für: {pdf_path.name}")
                start_time = _time.time()

                if output_path is None:
                    output_path = Config.DATA_OUTPUT_PATH / 'langchain' / pdf_path.stem

                pipeline_results = {}

                from common.logger import setup_logger as _setup_logger
                _logger = _setup_logger(__name__)

                try:
                    # 1. PARSING – skip if shared OCR result provided
                    if pre_parsed_text is not None:
                        step("parsing")
                        pipeline_results['parsing'] = pre_parsed_meta
                        text = pre_parsed_text
                    else:
                        parse_result = self.parsing_chain.invoke({'pdf_path': str(pdf_path)})
                        step("parsing")
                        if not parse_result['success']:
                            raise Exception(f"Parsing failed: {parse_result['metadata'].get('error')}")
                        pipeline_results['parsing'] = parse_result['metadata']
                        text = parse_result['text']

                    # 2. SEGMENTATION
                    seg_result = self.segmentation_chain.invoke({'text': text})
                    step("segmentation")
                    if not seg_result['success']:
                        raise Exception(f"Segmentation failed")
                    pipeline_results['segmentation'] = seg_result['metadata']
                    segments = seg_result['segments']

                    # 3-5. Classification / Rewriting / Validation
                    write_progress(progress_path, "running", "classification", ["parsing", "segmentation"],
                                   phase_progress("classification"), base_meta)
                    segments_with_variants = []
                    total = len(segments)
                    for idx, segment in enumerate(segments, 1):
                        # THESIS: Segmentfilter — Titel/Musterlösungen überspringen
                        segment_type = segment.get('type', 'unknown')
                        if segment_type in NON_REWRITABLE_TYPES:
                            _logger.info(f"  Segment {idx}: Überspringe type='{segment_type}' (nicht rewritable)")
                            segments_with_variants.append({
                                'original_segment': segment,
                                'classification': {'domain': 'general', 'content_type': segment_type, 'confidence': 1.0},
                                'validated_variants': [],
                                'validation_statistics': {'skipped': True, 'reason': f'type={segment_type} is not rewritable'},
                            })
                            continue

                        cls_result = self.classification_chain.invoke({'segment': segment})
                        if not cls_result['success']:
                            continue
                        classification = cls_result['classification']
                        seg_domain = classification.get('domain', 'general')

                        # progress within rewriting
                        rewrite_pct = phase_progress("rewriting") + int(
                            (idx / total) * PHASE_WEIGHTS[PHASES.index("rewriting")]
                        )
                        write_progress(progress_path, "running", "rewriting",
                                       ["parsing", "segmentation", "classification"],
                                       rewrite_pct, base_meta)

                        rw_result = self.rewriting_chain.invoke({'segment': segment, 'domain': seg_domain})
                        if not rw_result['success']:
                            continue

                        val_result = self.validation_chain.invoke({
                            'original': rw_result['original'],
                            'variants': rw_result['variants'],
                            'domain': seg_domain,
                        })
                        segments_with_variants.append({
                            'original_segment': segment,
                            'classification': classification,
                            'validated_variants': val_result['validated_variants'],
                            'validation_statistics': val_result['statistics'],
                        })

                    step("classification")
                    step("rewriting")
                    step("validation")

                    # 6. ASSEMBLY
                    write_progress(progress_path, "running", "assembly",
                                   ["parsing", "segmentation", "classification", "rewriting", "validation"],
                                   phase_progress("assembly"), base_meta)

                    assembly_result = self.assembly_chain.invoke({
                        'segments_with_variants': segments_with_variants,
                        'metadata': {
                            'pdf_path': str(pdf_path),
                            'domain': domain,
                            'num_variants_requested': args.variants,
                            **pipeline_results['parsing'],
                        },
                    })
                    pipeline_results['assembly'] = assembly_result['statistics']

                    save_result = self.assembly_chain.save_to_file(
                        assembly_result['assembled_document'], output_path
                    )

                    # PDF-Generierung: Aufgaben-PDF und Lösungs-PDF
                    from common.pdf_generator import PdfGenerator
                    _generator = PdfGenerator()
                    _tasks_path = output_path.parent / "tasks.pdf"
                    _solutions_path = output_path.parent / "solutions.pdf"
                    _generator.generate_tasks_pdf(assembly_result['assembled_document'], _tasks_path)
                    _generator.generate_solutions_pdf(assembly_result['assembled_document'], _solutions_path)
                    _pdf_files = {
                        'tasks': str(_tasks_path),
                        'solutions': str(_solutions_path),
                    }

                    step("assembly")
                    total_time = _time.time() - start_time

                    return {
                        'success': True,
                        'output_files': save_result['saved_files'],
                        'pdf_files': _pdf_files,
                        'statistics': {**pipeline_results, 'total_time': total_time},
                        'assembled_document': assembly_result['assembled_document'],
                        'segments_with_variants': segments_with_variants,
                    }

                except Exception as e:
                    total_time = _time.time() - start_time
                    return {'success': False, 'error': str(e),
                            'statistics': {**pipeline_results, 'total_time': total_time}}

        prog_pipeline = ProgressPipeline(domain=domain, num_variants=args.variants)
        result = prog_pipeline.process_pdf(pdf_path, output_path=output_dir / "assembled")

        if not result["success"]:
            raise RuntimeError(result.get("error", "Unknown error"))

        # Build result.json for frontend
        stats = result["statistics"]
        assembly = stats.get("assembly", {})
        parsing = stats.get("parsing", {})

        total_v = assembly.get("total_variants", 0)
        valid_v = assembly.get("valid_variants", 0)
        validation_rate = (valid_v / total_v) if total_v > 0 else 0.0

        frontend_result = {
            "success": True,
            "framework": "langchain",
            "domain": args.domain,
            "pdf_name": pdf_path.name,
            "metrics": {
                "total_time": stats.get("total_time", 0),
                "ocr_time": parsing.get("processing_time", 0),
                "ocr_tool": parsing.get("tool_used", "unknown"),
                "num_segments": stats.get("segmentation", {}).get("num_segments", 0),
                "total_variants": total_v,
                "valid_variants": valid_v,
                "validation_rate": validation_rate,
            },
            "segments": transform_segments(result.get("segments_with_variants", [])),
            "output_files": result.get("output_files", []),
            "pdf_files": result.get("pdf_files"),
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
        logger.info("Pipeline complete")
        sys.exit(0)

    except Exception as exc:
        logger.error(f"Pipeline failed: {exc}")
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
