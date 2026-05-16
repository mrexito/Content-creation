"""
Agent Pipeline Runner – für Frontend-Integration

Usage:
    python scripts/run_agent_pipeline.py \
        --pdf data/input/math/equations_simple.pdf \
        --domain math \
        --variants 1 \
        --retries 3 \
        --agent-variant orchestrator \
        --output-dir data/output/agent_orchestrator/run_xyz \
        --progress data/output/agent_orchestrator/run_xyz/progress.json \
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
from langchain_agent_prototype.pipeline import LangChainAgentPipeline

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
    parser = argparse.ArgumentParser(description="Run Agent Pipeline")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--domain", default="auto")
    parser.add_argument("--variants", type=int, default=1)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--agent-variant", default="orchestrator",
                        choices=["orchestrator", "multi_agent"])
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
    agent_variant = args.agent_variant
    framework_name = "agent_orchestrator" if agent_variant == "orchestrator" else "agent_multi"

    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    from common.ocr_handler import reset_ocr_handler, get_ocr_handler
    from common.llm_handler import reset_llm_handler, get_llm_handler
    # Config-Override – Agents nutzen LCEL-Tools, die Config.LLM_PROVIDER direkt lesen.
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
                    "pdf_name": pdf_path.name, "framework": framework_name,
                    "domain": args.domain, "run_id": args.run_id,
                    "agent_variant": agent_variant,
                    "error": f"OCR fehlgeschlagen: {ocr_data.get('error', 'Unbekannt')}",
                })
                sys.exit(1)
        except Exception as e:
            logger.warning(f"Konnte pre-parsed-text nicht lesen: {e}. Führe eigenes OCR durch.")

    base_meta = {
        "pdf_name": pdf_path.name,
        "framework": framework_name,
        "domain": args.domain,
        "run_id": args.run_id,
        "ocr_tool": args.ocr_tool,
        "llm_provider": args.llm_provider,
        "llm_model": args.llm_model or "default",
        "agent_variant": agent_variant,
    }

    def update(phase: str, completed: list):
        pct = phase_progress(phase)
        write_progress(progress_path, "running", phase, completed, pct, base_meta)

    try:
        if pre_parsed_text is not None:
            update("segmentation", ["parsing"])
        else:
            update("parsing", [])

        class ProgressPipeline(LangChainAgentPipeline):
            def process_pdf(self, pdf_path, output_path=None):
                import time as _time
                from common.logger import setup_logger as _sl
                _logger = _sl(__name__)

                start_time = _time.time()
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

                if output_path is None:
                    output_path = (
                        Config.DATA_OUTPUT_PATH / 'langchain_agent' / agent_variant / pdf_path.stem
                    )

                pipeline_stats = {}

                try:
                    # PHASE 1: Parsing
                    if pre_parsed_text is not None:
                        step("parsing")
                        pipeline_stats['parsing'] = pre_parsed_meta
                        text = pre_parsed_text
                    else:
                        parse_result = self.parsing_chain.invoke({'pdf_path': str(pdf_path)})
                        step("parsing")
                        if not parse_result['success']:
                            raise Exception(f"Parsing failed: {parse_result['metadata'].get('error')}")
                        pipeline_stats['parsing'] = parse_result['metadata']
                        text = parse_result['text']

                    # PHASE 1b: Segmentation
                    seg_result = self.segmentation_chain.invoke({'text': text})
                    step("segmentation")
                    if not seg_result['success']:
                        raise Exception("Segmentation failed")
                    pipeline_stats['segmentation'] = seg_result['metadata']
                    segments = seg_result['segments']

                    # PHASE 1c: Classification (übersprungen — Agent klassifiziert selbst)
                    # domain_hint aus CLI-Parameter wird direkt übergeben;
                    # der AgentExecutor ruft classify_segment als erstes Tool auf.
                    write_progress(
                        progress_path, "running", "classification",
                        ["parsing", "segmentation"], phase_progress("classification"), base_meta,
                    )

                    classified_segments = []
                    for seg in segments:
                        seg_type = seg.get('type', 'unknown')
                        classified_segments.append({
                            'segment': seg,
                            'domain': domain or 'general',
                            'skip': seg_type in NON_REWRITABLE_TYPES,
                        })

                    step("classification")

                    # PHASE 2: Agent rewriting (rewriting + validation combined)
                    total = len(classified_segments)
                    segments_with_variants = []
                    agent_stats = {
                        'total_tool_calls': 0,
                        'total_attempts': 0,
                        'valid_variants': 0,
                        'invalid_variants': 0,
                        'skipped': 0,
                    }

                    for idx, cls_seg in enumerate(classified_segments, 1):
                        segment = cls_seg['segment']
                        seg_domain = cls_seg['domain']

                        rewrite_pct = phase_progress("rewriting") + int(
                            (idx / total) * PHASE_WEIGHTS[PHASES.index("rewriting")]
                        )
                        write_progress(
                            progress_path, "running", "rewriting",
                            ["parsing", "segmentation", "classification"],
                            rewrite_pct, base_meta,
                        )

                        if cls_seg['skip']:
                            agent_stats['skipped'] += 1
                            segments_with_variants.append({
                                'original_segment': segment,
                                'classification': {
                                    'domain': seg_domain,
                                    'content_type': segment.get('type', 'unknown'),
                                    'confidence': 1.0,
                                },
                                'validated_variants': [],
                                'validation_statistics': {
                                    'skipped': True,
                                    'reason': f"type={segment.get('type')} is not rewritable",
                                },
                                'agent_result': None,
                            })
                            continue

                        for _ in range(self.num_variants):
                            agent_result = self._run_agent(
                                segment=segment, domain_hint=seg_domain
                            )
                            agent_stats['total_tool_calls'] += len(
                                agent_result.get('tool_calls', [])
                            )
                            agent_stats['total_attempts'] += agent_result.get('attempts', 1)
                            if agent_result.get('is_valid'):
                                agent_stats['valid_variants'] += 1
                            else:
                                agent_stats['invalid_variants'] += 1

                            variant_text = agent_result.get('variant')
                            validated_variants = []
                            if variant_text:
                                validated_variants.append({
                                    'variant_id': 1,
                                    'text': variant_text,
                                    'attempts': agent_result.get('attempts', 1),
                                    'validation': {
                                        'is_valid': agent_result.get('is_valid', False),
                                        'issues': [],
                                    },
                                })
                            segments_with_variants.append({
                                'original_segment': segment,
                                'classification': {
                                    'domain': agent_result.get('domain', seg_domain),
                                    'content_type': segment.get('type', 'task'),
                                },
                                'validated_variants': validated_variants,
                                'validation_statistics': {
                                    'total': 1,
                                    'valid': 1 if agent_result.get('is_valid') else 0,
                                    'invalid': 0 if agent_result.get('is_valid') else 1,
                                },
                                'agent_result': agent_result,
                            })

                    pipeline_stats['agent'] = agent_stats
                    step("rewriting")
                    step("validation")

                    # PHASE 3: Assembly
                    write_progress(
                        progress_path, "running", "assembly",
                        ["parsing", "segmentation", "classification", "rewriting", "validation"],
                        phase_progress("assembly"), base_meta,
                    )

                    assembly_result = self.assembly_chain.invoke({
                        'segments_with_variants': segments_with_variants,
                        'metadata': {
                            'pdf_path': str(pdf_path),
                            'domain': domain,
                            'variant': agent_variant,
                            'num_variants_requested': self.num_variants,
                            **pipeline_stats['parsing'],
                        },
                    })
                    pipeline_stats['assembly'] = assembly_result['statistics']

                    save_result = self.assembly_chain.save_to_file(
                        assembly_result['assembled_document'], output_path
                    )

                    from common.pdf_generator import PdfGenerator
                    _generator = PdfGenerator()
                    _tasks_path = output_path.parent / "tasks.pdf"
                    _solutions_path = output_path.parent / "solutions.pdf"
                    _generator.generate_tasks_pdf(
                        assembly_result['assembled_document'], _tasks_path
                    )
                    _generator.generate_solutions_pdf(
                        assembly_result['assembled_document'], _solutions_path
                    )

                    step("assembly")
                    total_time = _time.time() - start_time

                    return {
                        'success': True,
                        'output_files': save_result['saved_files'],
                        'pdf_files': {
                            'tasks': str(_tasks_path),
                            'solutions': str(_solutions_path),
                        },
                        'statistics': {**pipeline_stats, 'total_time': total_time},
                        'assembled_document': assembly_result['assembled_document'],
                        'segments_with_variants': segments_with_variants,
                    }

                except Exception as e:
                    total_time = _time.time() - start_time
                    return {
                        'success': False,
                        'error': str(e),
                        'statistics': {**pipeline_stats, 'total_time': total_time},
                    }

        prog_pipeline = ProgressPipeline(
            variant=agent_variant,
            domain=domain,
            num_variants=args.variants,
            max_retries=args.retries,
        )
        result = prog_pipeline.process_pdf(pdf_path, output_path=output_dir / "assembled")

        if not result["success"]:
            raise RuntimeError(result.get("error", "Unknown error"))

        stats = result["statistics"]
        parsing = stats.get("parsing", {})
        agent_stats = stats.get("agent", {})
        segments_with_variants = result.get("segments_with_variants", [])

        rewritable_count = agent_stats.get('valid_variants', 0) + agent_stats.get('invalid_variants', 0)
        tool_calls_per_segment = [
            len(sw['agent_result'].get('tool_calls', []))
            for sw in segments_with_variants
            if sw.get('agent_result') is not None
        ]

        frontend_result = {
            "success": True,
            "framework": framework_name,
            "domain": args.domain,
            "pdf_name": pdf_path.name,
            "metrics": {
                "total_time": stats.get("total_time", 0),
                "ocr_time": parsing.get("processing_time", 0),
                "ocr_tool": parsing.get("tool_used", "unknown"),
                "num_segments": stats.get("segmentation", {}).get("num_segments", 0),
                "total_variants": rewritable_count,
                "valid_variants": agent_stats.get("valid_variants", 0),
                "validation_rate": (
                    agent_stats.get("valid_variants", 0) / max(1, rewritable_count)
                ),
                "agent_variant": agent_variant,
                "tool_calls_total": agent_stats.get("total_tool_calls", 0),
                "tool_calls_per_segment": tool_calls_per_segment,
                "total_attempts": agent_stats.get("total_attempts", 0),
                "skipped_segments": agent_stats.get("skipped", 0),
            },
            "segments": transform_segments(segments_with_variants),
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
        logger.info("Agent pipeline complete")
        sys.exit(0)

    except Exception as exc:
        logger.error(f"Agent pipeline failed: {exc}")
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
