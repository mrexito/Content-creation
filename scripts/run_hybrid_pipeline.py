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
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.config import Config
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
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.progress
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    domain = None if args.domain == "auto" else args.domain

    base_meta = {
        "run_id": args.run_id,
        "framework": "hybrid",
        "pdf": str(args.pdf),
        "domain": args.domain,
        "variants": args.variants,
    }

    write_progress(progress_path, "running", "parsing", [], 0, base_meta)

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

        output_data = {
            "run_id": args.run_id,
            "framework": "hybrid",
            "success": True,
            "segments": transformed,
            "statistics": {
                "total_segments": len(transformed),
                "total_variants": graph_stats.get("total_valid", 0),
                "valid_variants": graph_stats.get("total_valid", 0),
                "validation_rate": graph_stats.get("validation_rate", 0.0),
                "processing_time": stats.get("total_time", 0.0),
            },
            "output_files": result.get("output_files", []),
        }

        result_path = output_dir / "result.json"
        result_path.write_text(
            json.dumps(output_data, indent=2, ensure_ascii=False)
        )

        write_progress(
            progress_path,
            "completed",
            "assembly",
            PHASES,
            100,
            {**base_meta, **output_data["statistics"]},
        )

        logger.info(f"✅ Hybrid Pipeline Runner abgeschlossen → {result_path}")

    except Exception as e:
        logger.error(f"Hybrid Pipeline Runner fehlgeschlagen: {e}")
        write_progress(
            progress_path,
            "failed",
            "error",
            [],
            0,
            {**base_meta, "error": str(e)},
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
