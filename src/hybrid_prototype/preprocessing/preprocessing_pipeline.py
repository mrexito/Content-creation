"""
LangChain Preprocessing Pipeline – Phase 1 des Hybrid-Ansatzes

Führt OCR, Segmentierung und Klassifizierung via bestehende LangChain-Chains
durch und befüllt den HybridWorkflowState für die anschliessende LangGraph-Phase.

Architektur-Entscheidung:
    Die ersten drei Schritte (Parsing, Segmentierung, Klassifizierung) eignen sich
    gut für eine lineare Chain-Verarbeitung ohne Rückschleifen. Der Hybrid-Ansatz
    nutzt daher die bewährten LangChain-Chains und übergibt den erzeugten
    strukturierten Zwischenstand an den LangGraph-Graphen.
"""
import time
from pathlib import Path

from common.logger import setup_logger
from common.ocr_handler import reset_ocr_handler, get_ocr_handler
from hybrid_prototype.state.hybrid_state import HybridWorkflowState

# Wiederverwendung der LangChain-Chains (kein Code-Duplizierung)
from langchain_prototype.chains.parsing_chain import get_parsing_chain
from langchain_prototype.chains.segmentation_chain import get_segmentation_chain
from langchain_prototype.chains.classification_chain import get_classification_chain

logger = setup_logger(__name__)


class HybridPreprocessingPipeline:
    """
    LangChain-basierte Vorverarbeitung für den Hybrid-Prototyp.

    Schritte:
        1. Parsing   (PDF → Text via OCR)
        2. Segmentierung (Text → Abschnitte)
        3. Klassifizierung (Abschnitte → domänen-klassifizierte Segmente)

    Output: befüllter HybridWorkflowState bereit für LangGraph-Phase
    """

    def __init__(self, domain: str = None):
        """
        Args:
            domain: Optional Domäne ('math', 'languages', 'economics')
        """
        self.domain = domain

        # Initialisiere LangChain Chains
        self.parsing_chain = get_parsing_chain(domain=domain)
        self.segmentation_chain = get_segmentation_chain()
        self.classification_chain = get_classification_chain()

        logger.info(
            f"HybridPreprocessingPipeline initialisiert "
            f"(Domain: {domain or 'auto'})"
        )

    def run(self, state: HybridWorkflowState) -> HybridWorkflowState:
        """
        Führt Preprocessing durch und aktualisiert den State.

        Args:
            state: Initialer HybridWorkflowState mit pdf_path

        Returns:
            State mit raw_text, segments, classified_segments befüllt
        """
        logger.info("=" * 60)
        logger.info("HYBRID PREPROCESSING (LangChain) – Start")
        logger.info("=" * 60)

        start_time = time.time()
        pdf_path = Path(state["pdf_path"])

        # ── Step 1: Parsing ───────────────────────────────────────────────────
        if state.get("raw_text"):
            logger.info("Step 1/3: Parsing übersprungen (geteiltes OCR-Ergebnis)")
            logger.info(
                f"  ✓ Parsing (geteilt): {len(state['raw_text'])} Zeichen, "
                f"Tool: {(state.get('ocr_metadata') or {}).get('tool_used', 'shared')}"
            )
        else:
            logger.info("Step 1/3: Parsing PDF...")
            parse_result = self.parsing_chain.invoke({"pdf_path": str(pdf_path)})

            if not parse_result["success"]:
                error_msg = f"Parsing fehlgeschlagen: {parse_result['metadata'].get('error')}"
                logger.error(error_msg)
                state["errors"].append(error_msg)
                state["current_phase"] = "error"
                return state

            # Fallback: Mistral sometimes returns success with 0 chars (silent rate-limit failure)
            if not parse_result["text"].strip():
                logger.warning("  ⚠ OCR lieferte keinen Text – Fallback auf Tesseract")
                reset_ocr_handler()
                get_ocr_handler(default_tool="tesseract")
                parse_result = self.parsing_chain.invoke({"pdf_path": str(pdf_path)})
                if not parse_result.get("text", "").strip():
                    error_msg = "OCR konnte keinen Text extrahieren (weder Mistral noch Tesseract)"
                    logger.error(error_msg)
                    state["errors"].append(error_msg)
                    state["current_phase"] = "error"
                    return state

            state["raw_text"] = parse_result["text"]
            state["ocr_metadata"] = parse_result["metadata"]
            logger.info(
                f"  ✓ Parsing: {len(parse_result['text'])} Zeichen, "
                f"Tool: {parse_result['metadata'].get('tool_used', 'unknown')}"
            )

        # ── Step 2: Segmentierung ─────────────────────────────────────────────
        logger.info("Step 2/3: Segmentierung...")
        seg_result = self.segmentation_chain.invoke({"text": state["raw_text"]})

        if not seg_result["success"]:
            error_msg = "Segmentierung fehlgeschlagen"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["current_phase"] = "error"
            return state

        state["segments"] = seg_result["segments"]
        logger.info(f"  ✓ Segmentierung: {len(state['segments'])} Segmente")

        # ── Step 3: Klassifizierung ───────────────────────────────────────────
        logger.info("Step 3/3: Klassifizierung...")
        classified_segments = []
        for segment in state["segments"]:
            seg_result = self.classification_chain.invoke({"segment": segment})
            if not seg_result["success"]:
                error_msg = "Klassifizierung fehlgeschlagen"
                logger.error(error_msg)
                state["errors"].append(error_msg)
                state["current_phase"] = "error"
                return state
            classified_segments.append({
                "segment": segment,
                "classification": seg_result["classification"],
            })

        state["classified_segments"] = classified_segments
        elapsed = time.time() - start_time
        state["total_processing_time"] += elapsed
        state["current_phase"] = "preprocessing_complete"

        logger.info(
            f"  ✓ Klassifizierung: {len(state['classified_segments'])} Segmente klassifiziert"
        )
        logger.info(f"✅ Preprocessing abgeschlossen in {elapsed:.2f}s")

        return state


def get_preprocessing_pipeline(domain: str = None) -> HybridPreprocessingPipeline:
    """Factory für HybridPreprocessingPipeline"""
    return HybridPreprocessingPipeline(domain=domain)
