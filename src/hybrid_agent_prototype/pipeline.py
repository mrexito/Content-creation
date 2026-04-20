"""
Hybrid Agent Pipeline – Haupt-Orchestrator

Architektur:

    Phase 1: LangChain Preprocessing  (OCR → Segmentierung → Klassifizierung)
             ↓ HybridWorkflowState
    Phase 2: LangChain Agent          (Rewriting + Validation via AgentExecutor)
             ↓ HybridWorkflowState
    Phase 3: LangChain Postprocessing (Assembly → Export)

Einziger Unterschied zum Hybrid-Prototyp (hybrid_prototype/):
Phase 2 verwendet LangChain AgentExecutor statt LangGraph StateGraph.
Ermöglicht isolierten Vergleich: LangGraph vs. Agent bei identischem
Pre- und Postprocessing.

Phase 1 und Phase 3 werden direkt aus hybrid_prototype importiert.
"""
import time
from pathlib import Path
from typing import Dict, Any

from common.config import Config
from common.logger import setup_logger
from hybrid_prototype.state.hybrid_state import create_initial_state
from hybrid_prototype.preprocessing.preprocessing_pipeline import get_preprocessing_pipeline
from hybrid_prototype.postprocessing.postprocessing_pipeline import get_postprocessing_pipeline
from hybrid_agent_prototype.agent_phase import run_hybrid_agent

logger = setup_logger(__name__)


class HybridAgentPipeline:
    """
    Hybrid Agent Pipeline für Content-Variation.

    Identisch mit HybridPipeline, aber Phase 2 nutzt LangChain AgentExecutor
    statt LangGraph StateGraph für Rewriting + Validation.
    """

    def __init__(
        self,
        domain: str = None,
        num_variants: int = 1,
        max_retries: int = 3,
    ):
        """
        Args:
            domain:          Domäne ('math', 'languages', 'economics') oder None
            num_variants:    Varianten pro Segment (Standard 1 für Agenten)
            max_retries:     Max. Retry-Versuche im Agent
        """
        self.domain = domain
        self.num_variants = num_variants
        self.max_retries = max_retries

        # Phase 1 & 3: identisch mit hybrid_prototype
        self.preprocessing = get_preprocessing_pipeline(domain=domain)
        self.postprocessing = get_postprocessing_pipeline()

        logger.info(
            f"HybridAgentPipeline initialisiert – "
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
        Verarbeitet ein PDF durch alle drei Phasen.

        Args:
            pdf_path:          Pfad zur Input-PDF
            output_path:       Output-Pfad (ohne Extension)
            pre_parsed_text:   Vorverarbeiteter OCR-Text (überspringt Parsing)
            pre_parsed_meta:   Metadaten zum OCR-Schritt
            progress_callback: Callable[[str], None] für Fortschritts-Events

        Returns:
            Dict mit success, output_files, statistics, assembled_document
        """
        logger.info("=" * 70)
        logger.info(f"HYBRID AGENT PIPELINE – Start: {pdf_path.name}")
        logger.info("=" * 70)

        pipeline_start = time.time()

        if output_path is None:
            output_path = Config.DATA_OUTPUT_PATH / "hybrid_agent" / pdf_path.stem

        state = create_initial_state(
            pdf_path=str(pdf_path),
            domain=self.domain,
            num_variants=self.num_variants,
            max_retries=self.max_retries,
        )

        # Pre-populate mit gemeinsamem OCR-Ergebnis
        if pre_parsed_text is not None:
            state["raw_text"] = pre_parsed_text
            state["ocr_metadata"] = pre_parsed_meta or {"shared_ocr": True}

        try:
            # ── Phase 1: LangChain Preprocessing (identisch mit hybrid_prototype) ─
            state = self.preprocessing.run(state)

            if state["current_phase"] == "error":
                raise RuntimeError(
                    f"Preprocessing fehlgeschlagen: {state['errors']}"
                )

            if progress_callback:
                if pre_parsed_text is None:
                    progress_callback("parsing")
                progress_callback("segmentation")
                progress_callback("classification")

            # ── Phase 2: LangChain Agent (statt LangGraph StateGraph) ─────────────
            state = run_hybrid_agent(
                state,
                max_retries=self.max_retries,
                progress_callback=progress_callback,
            )

            if state["current_phase"] not in ("agent_complete", "postprocessing_complete"):
                raise RuntimeError(
                    f"Agent-Phase fehlgeschlagen: {state.get('errors', [])}"
                )

            # ── Phase 3: LangChain Postprocessing (identisch mit hybrid_prototype) ─
            state = self.postprocessing.run(state, output_path=output_path)

            if progress_callback:
                progress_callback("assembly")

            total_time = time.time() - pipeline_start

            output_files = []
            for ext in [".json", ".txt"]:
                p = output_path.with_suffix(ext)
                if p.exists():
                    output_files.append(str(p))

            final_doc = state.get("final_document") or {}
            stats = final_doc.get("statistics") or {}
            validation_stats = state.get("validation_stats") or {}
            agent_stats = state.get("agent_stats") or {}

            logger.info("=" * 70)
            logger.info(f"✅ HYBRID AGENT PIPELINE – Abgeschlossen in {total_time:.2f}s")
            logger.info(
                f"   Segmente: {stats.get('total_segments', 0)}, "
                f"Varianten: {stats.get('total_variants', 0)}, "
                f"Valide: {stats.get('valid_variants', 0)}, "
                f"Tool-Calls: {agent_stats.get('total_tool_calls', 0)}"
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
                    "agent": {
                        "total_valid": validation_stats.get("total_valid", 0),
                        "total_invalid": validation_stats.get("total_invalid", 0),
                        "validation_rate": validation_stats.get("validation_rate", 0.0),
                        "retry_counts": state.get("retry_counts") or {},
                        "total_tool_calls": agent_stats.get("total_tool_calls", 0),
                        "tool_calls_per_segment": agent_stats.get("tool_calls_per_segment", []),
                        "total_retries": agent_stats.get("total_retries", 0),
                        "hallucinated_calls": agent_stats.get("hallucinated_calls", 0),
                    },
                    "total_time": total_time,
                    "phase_time": state.get("total_processing_time", total_time),
                },
                "assembled_document": final_doc,
            }

        except Exception as e:
            total_time = time.time() - pipeline_start
            logger.error(f"Hybrid Agent Pipeline fehlgeschlagen: {str(e)}")
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
    num_variants: int = 1,
    max_retries: int = 3,
) -> HybridAgentPipeline:
    """Factory für HybridAgentPipeline."""
    return HybridAgentPipeline(
        domain=domain,
        num_variants=num_variants,
        max_retries=max_retries,
    )
