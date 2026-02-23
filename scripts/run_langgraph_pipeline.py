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
    "segmentation": "segmentation",
    "classification": "classification",
    "rewriting": "rewriting",
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


def main():
    parser = argparse.ArgumentParser(description="Run LangGraph Pipeline")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--domain", default="auto")
    parser.add_argument("--variants", type=int, default=2)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    pdf_path = args.pdf
    domain = None if args.domain == "auto" else args.domain
    output_dir = args.output_dir
    progress_path = args.progress

    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    base_meta = {
        "pdf_name": pdf_path.name,
        "framework": "langgraph",
        "domain": args.domain,
        "run_id": args.run_id,
    }

    # Write initial progress
    write_progress(progress_path, "running", "parsing", [], 0, base_meta)

    try:
        workflow = create_workflow_graph()

        initial_state = create_initial_state(
            pdf_path=str(pdf_path),
            domain=domain,
            num_variants=args.variants,
            max_retries=args.retries,
        )

        # LangGraph supports streaming – use stream to emit per-node progress
        completed_phases = []
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
            "segments": segments_raw,
            "output_files": [str(json_path), str(txt_path)],
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
