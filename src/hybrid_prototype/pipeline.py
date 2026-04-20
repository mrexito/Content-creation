"""
Hybrid Pipeline – Haupt-Orchestrator

Verbindet die drei Phasen des Hybrid-Ansatzes:

    Phase 1: LangChain Preprocessing  (OCR → Segmentierung → Klassifizierung)
             ↓ HybridWorkflowState
    Phase 2: LangGraph StateGraph      (Rewriting → Validation → [Retry-Loop])
             ↓ HybridWorkflowState
    Phase 3: LangChain Postprocessing  (Assembly → Export)

Diese Architektur kombiniert die Stärken beider Frameworks:
  - LangChain: klare, sequentielle Chains für strukturierte Vorverarbeitung
  - LangGraph: zustandsbasierte Graphen mit Retry-Loops für die komplexe,
               iterative Rewriting-Validation-Phase
  - LangChain: wieder lineare Chains für den abschliessenden Export
"""
import time
from pathlib import Path
from typing import Dict, Any

from common.config import Config
from common.logger import setup_logger
from hybrid_prototype.state.hybrid_state import create_initial_state
from hybrid_prototype.preprocessing.preprocessing_pipeline import get_preprocessing_pipeline
from hybrid_prototype.graph.hybrid_graph import run_hybrid_graph
from hybrid_prototype.postprocessing.postprocessing_pipeline import get_postprocessing_pipeline

logger = setup_logger(__name__)


class HybridPipeline:
    """
    Komplette Hybrid-Pipeline für Content-Variation.

    Orchestriert LangChain Preprocessing, LangGraph Rewriting+Validation
    und LangChain Postprocessing zu einem zusammenhängenden Workflow.
    """

    def __init__(
        self,
        domain: str = None,
        num_variants: int = 3,
        max_retries: int = 2,
    ):
        """
        Args:
            domain:           Domäne ('math', 'languages', 'economics') oder None (Auto-Detect)
            num_variants:     Gewünschte Anzahl Varianten pro Segment
            max_retries:      Maximale Retry-Iterationen im LangGraph-Loop
        """
        self.domain = domain
        self.num_variants = num_variants
        self.max_retries = max_retries

        # Phase 1 & 3: LangChain
        self.preprocessing = get_preprocessing_pipeline(domain=domain)
        self.postprocessing = get_postprocessing_pipeline()

        # Phase 2: LangGraph (Graph wird bei Bedarf erstellt)

        logger.info(
            f"HybridPipeline initialisiert – "
            f"Domain: {domain or 'auto'}, "
            f"Varianten: {num_variants}, "
            f"Max Retries: {max_retries}"
        )

    def process_pdf(
        self,
        pdf_path: Path,
        output_path: Path = None,
        pre_parsed_text: str = None,
        pre_parsed_meta: dict = None,
        progress_callback=None,
    ) -> Dict[str, Any]:
        """
        Verarbeitet ein PDF komplett durch alle drei Phasen.

        Args:
            pdf_path:    Pfad zur Input-PDF
            output_path: Optionaler Output-Pfad (ohne Extension)

        Returns:
            Dict mit success, output_files, statistics, assembled_document
        """
        logger.info("=" * 70)
        logger.info(f"HYBRID PIPELINE – Start: {pdf_path.name}")
        logger.info("=" * 70)

        pipeline_start = time.time()

        # Default output path
        if output_path is None:
            output_path = Config.DATA_OUTPUT_PATH / "hybrid" / pdf_path.stem

        # ── Initialer State ────────────────────────────────────────────────────
        state = create_initial_state(
            pdf_path=str(pdf_path),
            domain=self.domain,
            num_variants=self.num_variants,
            max_retries=self.max_retries,
        )

        # Pre-populate with shared OCR result to skip redundant parsing
        if pre_parsed_text is not None:
            state["raw_text"] = pre_parsed_text
            state["ocr_metadata"] = pre_parsed_meta or {"shared_ocr": True}

        try:
            # ── Phase 1: LangChain Preprocessing ──────────────────────────────
            state = self.preprocessing.run(state)

            if state["current_phase"] == "error":
                raise RuntimeError(
                    f"Preprocessing fehlgeschlagen: {state['errors']}"
                )

            if progress_callback:
                # Preprocessing covers parsing → segmentation → classification
                if not (pre_parsed_text is not None):
                    progress_callback("parsing")
                progress_callback("segmentation")
                progress_callback("classification")

            # ── Phase 2: LangGraph Rewriting + Validation ──────────────────────
            state = run_hybrid_graph(state, progress_callback=progress_callback)

            if state["current_phase"] == "error":
                raise RuntimeError(
                    f"LangGraph-Phase fehlgeschlagen: {state['errors']}"
                )

            # ── Phase 3: LangChain Postprocessing ─────────────────────────────
            state = self.postprocessing.run(state, output_path=output_path)

            if progress_callback:
                progress_callback("assembly")

            total_time = time.time() - pipeline_start

            # Bestimme gespeicherte Dateien
            output_files = []
            for ext in [".json", ".txt"]:
                p = output_path.with_suffix(ext)
                if p.exists():
                    output_files.append(str(p))

            final_doc = state.get("final_document") or {}
            stats = final_doc.get("statistics") or {}
            validation_stats = state.get("validation_stats") or {}

            logger.info("=" * 70)
            logger.info(f"✅ HYBRID PIPELINE – Abgeschlossen in {total_time:.2f}s")
            logger.info(
                f"   Segmente: {stats.get('total_segments', 0)}, "
                f"Varianten gesamt: {stats.get('total_variants', 0)}, "
                f"Valide: {stats.get('valid_variants', 0)}"
            )
            logger.info("=" * 70)

            return {
                "success": True,
                "output_files": output_files,
                "statistics": {
                    "preprocessing": {
                        "ocr_tool": (state.get("ocr_metadata") or {}).get("tool_used"),
                        "segments": len(state.get("segments") or []),
                    },
                    "graph": {
                        "total_valid": validation_stats.get("total_valid", 0),
                        "total_invalid": validation_stats.get("total_invalid", 0),
                        "validation_rate": validation_stats.get("validation_rate", 0.0),
                        "retry_counts": state.get("retry_counts") or {},
                    },
                    "total_time": total_time,
                    "phase_time": state.get("total_processing_time", total_time),
                },
                "assembled_document": final_doc,
            }

        except Exception as e:
            total_time = time.time() - pipeline_start
            logger.error(f"Hybrid Pipeline fehlgeschlagen: {str(e)}")

            return {
                "success": False,
                "error": str(e),
                "statistics": {
                    "total_time": total_time,
                    "errors": state.get("errors", []),
                },
            }


def get_pipeline(
    domain: str = None,
    num_variants: int = 3,
    max_retries: int = 2,
) -> HybridPipeline:
    """Factory für HybridPipeline"""
    return HybridPipeline(
        domain=domain,
        num_variants=num_variants,
        max_retries=max_retries,
    )
