"""
LangChain Postprocessing Pipeline – Phase 3 des Hybrid-Ansatzes

Übernimmt den State nach dem LangGraph-Graphen und führt durch:
    1. Sprachliche Glättung  (LLM-basiert, via LangChain)
    2. Dokument-Assembly     (via LangChain AssemblyChain)
    3. Export                (JSON + TXT)

Architektur-Entscheidung:
    Diese abschliessenden Schritte erfordern keine Rückschleifen mehr –
    die Varianten sind bereits validiert. Eine lineare LangChain-Pipeline
    ist hier optimal geeignet.
"""
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from common.llm_handler import get_llm_handler
from common.logger import setup_logger
from hybrid_prototype.state.hybrid_state import HybridWorkflowState

logger = setup_logger(__name__)

# Prompt für stilistische Glättung
SMOOTHING_SYSTEM_PROMPT = """Du bist ein Lektor. Deine Aufgabe ist es, einen 
generierten Text sprachlich zu glätten und natürlicher zu formulieren, 
ohne den Inhalt zu verändern. Behalte Fachbegriffe, Zahlen und alle 
inhaltlichen Details exakt bei."""

SMOOTHING_USER_TEMPLATE = """Bitte glätte diesen Text sprachlich:

{text}

Gib nur den verbesserten Text zurück, ohne Erklärungen."""


class HybridPostprocessingPipeline:
    """
    LangChain-basiertes Postprocessing für den Hybrid-Prototyp.

    Schritte:
        1. Sprachliche Glättung der validen Varianten via LLM
        2. Assembly des finalen Dokuments (Struktur + Text-Output)
        3. Export als JSON und TXT
    """

    def __init__(self, apply_smoothing: bool = True):
        """
        Args:
            apply_smoothing: Ob LLM-Glättung angewendet werden soll
                             (kann deaktiviert werden für Speed-Tests)
        """
        self.apply_smoothing = apply_smoothing
        self.llm = get_llm_handler()
        logger.info(
            f"HybridPostprocessingPipeline initialisiert "
            f"(Glättung: {'an' if apply_smoothing else 'aus'})"
        )

    def _smooth_variant(self, text: str) -> str:
        """
        Wendet stilistische LLM-Glättung auf eine Variante an.

        Args:
            text: Rohtext der Variante

        Returns:
            Geglätteter Text (oder Original bei Fehler)
        """
        if not self.apply_smoothing or not text:
            return text

        result = self.llm.generate(
            prompt=SMOOTHING_USER_TEMPLATE.format(text=text),
            system_prompt=SMOOTHING_SYSTEM_PROMPT,
            temperature=0.3,  # Niedrig für konsistente Glättung
        )

        if result.get("success") and result.get("text"):
            return result["text"].strip()

        logger.warning("Glättung fehlgeschlagen, Original wird verwendet")
        return text

    def _assemble_document(
        self,
        state: HybridWorkflowState,
    ) -> Dict[str, Any]:
        """
        Assembliert das finale Dokument aus dem State.

        Returns:
            assembled_document mit Struktur, Text-Output und Statistiken
        """
        segments_with_variants = state.get("segments_with_variants") or []
        ocr_metadata = state.get("ocr_metadata") or {}

        assembled_segments = []
        total_variants = 0
        valid_variants = 0
        smoothed_count = 0

        for seg_data in segments_with_variants:
            segment = seg_data.get("segment", {})
            classification = seg_data.get("classification", {})
            variants = seg_data.get("variants", [])

            # Nur valide Varianten weiterverarbeiten
            valid_vars = [
                v for v in variants
                if v.get("validation", {}).get("is_valid", False)
            ]
            total_variants += len(variants)
            valid_variants += len(valid_vars)

            # Sprachliche Glättung der validen Varianten
            smoothed_variants = []
            for v in valid_vars:
                original_variant_text = v.get("text", "")
                smoothed_text = self._smooth_variant(original_variant_text)
                if smoothed_text != original_variant_text:
                    smoothed_count += 1
                smoothed_variants.append(
                    {
                        **v,
                        "text": smoothed_text,
                        "smoothed": smoothed_text != original_variant_text,
                    }
                )

            assembled_segments.append(
                {
                    "original": segment.get("text", ""),
                    "segment_type": segment.get("type", "unknown"),
                    "classification": classification,
                    "num_variants": len(smoothed_variants),
                    "variants": [
                        {
                            "variant_id": v.get("variant_id"),
                            "text": v.get("text"),
                            "smoothed": v.get("smoothed", False),
                            "validation_score": v.get("validation", {}).get("score", 1.0),
                            "solution": v.get("solution"),  # Musterantwort (kann None sein)
                        }
                        for v in smoothed_variants
                    ],
                }
            )

        # Text-Output für Lesbarkeit
        text_lines = [
            "=" * 70,
            "HYBRID PROTOTYP – Varianten-Dokument",
            f"Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Domain: {state.get('domain') or 'auto'}",
            "=" * 70,
            "",
        ]

        for idx, seg in enumerate(assembled_segments, 1):
            text_lines.append(
                f"## Segment {idx}: {seg['segment_type'].upper()}"
            )
            text_lines.append("")
            text_lines.append("**Original:**")
            text_lines.append(seg["original"])
            text_lines.append("")

            if seg["num_variants"] > 0:
                text_lines.append(f"**Varianten ({seg['num_variants']}):**")
                text_lines.append("")
                for v in seg["variants"]:
                    smoothed_flag = " [geglättet]" if v.get("smoothed") else ""
                    text_lines.append(
                        f"Variante {v['variant_id']}{smoothed_flag}:"
                    )
                    text_lines.append(v["text"])
                    text_lines.append("")
            else:
                text_lines.append("*Keine validen Varianten generiert*")
                text_lines.append("")

            text_lines.append("-" * 70)
            text_lines.append("")

        return {
            "segments": assembled_segments,
            "text_output": "\n".join(text_lines),
            "statistics": {
                "total_segments": len(assembled_segments),
                "segments_with_variants": sum(
                    1 for s in assembled_segments if s["num_variants"] > 0
                ),
                "total_variants": total_variants,
                "valid_variants": valid_variants,
                "smoothed_variants": smoothed_count,
                "validation_rate": (
                    valid_variants / max(total_variants, 1)
                ),
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "pdf_path": state.get("pdf_path"),
                "domain": state.get("domain"),
                "num_variants_requested": state.get("num_variants"),
                "ocr_tool": ocr_metadata.get("tool_used"),
                "framework": "hybrid (LangChain + LangGraph)",
            },
        }

    def save_to_file(
        self,
        assembled_document: Dict[str, Any],
        output_path: Path,
    ) -> Dict[str, Any]:
        """
        Speichert das assemblierte Dokument (JSON + TXT).

        Args:
            assembled_document: Assembliertes Dokument-Dict
            output_path: Ziel-Pfad ohne Extension

        Returns:
            Dict mit saved_files und success
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        saved_files = []

        try:
            # 1. JSON (strukturiert)
            json_path = output_path.with_suffix(".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(assembled_document, f, indent=2, ensure_ascii=False)
            saved_files.append(str(json_path))
            logger.info(f"Gespeichert: {json_path}")

            # 2. Text (lesbar)
            txt_path = output_path.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(assembled_document.get("text_output", ""))
            saved_files.append(str(txt_path))
            logger.info(f"Gespeichert: {txt_path}")

            return {"saved_files": saved_files, "success": True}

        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")
            return {"saved_files": saved_files, "success": False, "error": str(e)}

    def run(
        self,
        state: HybridWorkflowState,
        output_path: Path = None,
    ) -> HybridWorkflowState:
        """
        Führt Postprocessing durch und aktualisiert den State.

        Args:
            state: HybridWorkflowState nach abgeschlossenem LangGraph
            output_path: Optionaler Output-Pfad (ohne Extension)

        Returns:
            State mit final_document befüllt
        """
        logger.info("=" * 60)
        logger.info("HYBRID POSTPROCESSING (LangChain) – Start")
        logger.info("=" * 60)

        start_time = time.time()

        # Glättung + Assembly
        logger.info("Step 1/2: Sprachliche Glättung + Assembly...")
        assembled_document = self._assemble_document(state)
        state["final_document"] = assembled_document

        # Export
        if output_path is not None:
            logger.info("Step 2/2: Export...")
            self.save_to_file(assembled_document, output_path)
        else:
            logger.info("Step 2/2: Export übersprungen (kein output_path)")

        elapsed = time.time() - start_time
        state["total_processing_time"] += elapsed
        state["current_phase"] = "postprocessing_complete"

        stats = assembled_document.get("statistics", {})
        logger.info(
            f"✅ Postprocessing abgeschlossen in {elapsed:.2f}s – "
            f"{stats.get('valid_variants', 0)} valide Varianten, "
            f"{stats.get('smoothed_variants', 0)} geglättet"
        )

        return state


def get_postprocessing_pipeline(apply_smoothing: bool = True) -> HybridPostprocessingPipeline:
    """Factory für HybridPostprocessingPipeline"""
    return HybridPostprocessingPipeline(apply_smoothing=apply_smoothing)
