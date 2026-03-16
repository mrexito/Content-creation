"""
LangChain Agent Pipeline — Haupt-Orchestrator

Verarbeitet ein PDF end-to-end mit dem Agenten-Prototyp:
  Phase 1 (Preprocessing): Parsing + Segmentierung + Klassifizierung
    → Bestehende LangChain-Chains aus langchain_prototype (kein Agenten-Schritt)
  Phase 2 (Agenten): Für jedes Segment Rewriting via Variante A oder B
    → Variante A: OrchestratorAgent (create_tool_calling_agent, alle Tools)
    → Variante B: MultiAgent-Pipeline (3 Agenten, je 1 Tool)
  Phase 3 (Assembly): Dokument-Zusammenbau
    → AssemblyChain aus langchain_prototype

Output-Format kompatibel mit bestehenden Prototypen (langchain/langgraph).
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from common.config import Config
from common.constants import NON_REWRITABLE_TYPES
from common.logger import setup_logger
from langchain_prototype.chains.parsing_chain import get_parsing_chain
from langchain_prototype.chains.segmentation_chain import get_segmentation_chain
from langchain_prototype.chains.classification_chain import get_classification_chain
from langchain_prototype.chains.assembly_chain import get_assembly_chain
from langchain_agent_prototype.orchestrator.agent import run_orchestrator
from langchain_agent_prototype.multi_agent.pipeline import run_multi_agent_pipeline

logger = setup_logger(__name__)


class LangChainAgentPipeline:
    """
    End-to-End Pipeline mit LangChain Agent Prototyp.

    Unterstützt zwei Varianten:
      'orchestrator' — Variante A: Ein Agent, alle Tools, autonomes Reasoning
      'multi_agent'  — Variante B: 3 Agenten, je 1 Tool, sequenzielle Pipeline
    """

    def __init__(
        self,
        variant: str = "orchestrator",
        domain: str = None,
        num_variants: int = 1,
        max_retries: int = 3,
    ):
        """
        Args:
            variant:      'orchestrator' oder 'multi_agent'
            domain:       Optional Domain-Hint (math, languages, economics)
            num_variants: Anzahl Varianten pro Segment (Standard 1 für Agenten)
            max_retries:  Maximale Retries (nur für Variante A relevant)
        """
        if variant not in ("orchestrator", "multi_agent"):
            raise ValueError(f"variant muss 'orchestrator' oder 'multi_agent' sein, nicht {variant!r}")

        self.variant = variant
        self.domain = domain
        self.num_variants = num_variants
        self.max_retries = max_retries

        # Phase 1: Bestehende LangChain-Chains (kein Agenten-Schritt)
        self.parsing_chain = get_parsing_chain(domain=domain)
        self.segmentation_chain = get_segmentation_chain()
        self.classification_chain = get_classification_chain()

        # Phase 3: Bestehende Assembly-Chain
        self.assembly_chain = get_assembly_chain()

        logger.info(
            f"LangChainAgentPipeline initialisiert "
            f"(variant={variant}, domain={domain or 'auto'}, "
            f"num_variants={num_variants}, max_retries={max_retries})"
        )

    def _run_agent(self, segment: Dict, domain_hint: Optional[str]) -> Dict:
        """Delegiert an die gewählte Agenten-Variante."""
        if self.variant == "orchestrator":
            return run_orchestrator(
                segment=segment,
                domain_hint=domain_hint,
                max_retries=self.max_retries,
            )
        else:
            return run_multi_agent_pipeline(
                segment=segment,
                max_retries=self.max_retries,
            )

    def process_pdf(
        self,
        pdf_path: Path,
        output_path: Path = None,
    ) -> Dict[str, Any]:
        """
        Verarbeitet ein PDF end-to-end.

        Args:
            pdf_path:    Pfad zum Input-PDF
            output_path: Ziel-Pfad (ohne Extension)

        Returns:
            Dict mit success, output_files, statistics, assembled_document
        """
        logger.info(f"AgentPipeline ({self.variant}): starte für {pdf_path.name}")
        start_time = time.time()

        if output_path is None:
            output_path = (
                Config.DATA_OUTPUT_PATH / "langchain_agent" / self.variant / pdf_path.stem
            )

        pipeline_stats: Dict[str, Any] = {}

        try:
            # =================================================================
            # PHASE 1: Preprocessing (bestehende LangChain-Chains)
            # =================================================================
            logger.info("Phase 1/3: Parsing PDF...")
            parse_result = self.parsing_chain.invoke({"pdf_path": str(pdf_path)})
            if not parse_result["success"]:
                raise Exception(f"Parsing failed: {parse_result['metadata'].get('error')}")
            pipeline_stats["parsing"] = parse_result["metadata"]
            text = parse_result["text"]

            logger.info("Phase 1/3: Segmentierung...")
            seg_result = self.segmentation_chain.invoke({"text": text})
            if not seg_result["success"]:
                raise Exception(f"Segmentation failed: {seg_result['metadata'].get('error')}")
            pipeline_stats["segmentation"] = seg_result["metadata"]
            segments = seg_result["segments"]

            # Klassifizierung aller Segmente (für domain_hint an den Agenten)
            # Hinweis: multi_agent ignoriert domain_hint vollständig — ClassifierAgent
            # bestimmt die Domain eigenständig. Deshalb wird classification_chain
            # für multi_agent übersprungen (spart N_rewritable LLM-Calls).
            logger.info(f"Phase 1/3: Klassifizierung ({len(segments)} Segmente)...")
            classified_segments = []
            for seg in segments:
                seg_type = seg.get("type", "unknown")
                if seg_type in NON_REWRITABLE_TYPES:
                    classified_segments.append({
                        "segment": seg,
                        "domain": self.domain or "general",
                        "skip": True,
                    })
                    continue
                if self.variant == "multi_agent":
                    # multi_agent hat keinen domain_hint-Parameter — ClassifierAgent
                    # klassifiziert selbst; Pre-Klassifizierung wäre wirkungslos.
                    domain_for_seg = self.domain or "general"
                else:
                    cls_result = self.classification_chain.invoke({"segment": seg})
                    domain_for_seg = (
                        cls_result["classification"].get("domain", "general")
                        if cls_result["success"]
                        else (self.domain or "general")
                    )
                classified_segments.append({
                    "segment": seg,
                    "domain": domain_for_seg,
                    "skip": False,
                })

            # =================================================================
            # PHASE 2: Agenten-Schritt (Rewriting + Validierung)
            # =================================================================
            logger.info(
                f"Phase 2/3: Agenten-Rewriting "
                f"({len(classified_segments)} Segmente, variant={self.variant})..."
            )
            segments_with_variants: List[Dict] = []
            agent_stats = {
                "total_tool_calls": 0,
                "total_attempts": 0,
                "valid_variants": 0,
                "invalid_variants": 0,
                "skipped": 0,
            }

            for idx, cls_seg in enumerate(classified_segments, 1):
                segment = cls_seg["segment"]
                domain = cls_seg["domain"]
                logger.info(f"  Segment {idx}/{len(classified_segments)} (domain={domain})")

                # Überspringe nicht-rewritable Segmente
                if cls_seg["skip"]:
                    agent_stats["skipped"] += 1
                    segments_with_variants.append({
                        "original_segment": segment,
                        "classification": {
                            "domain": domain,
                            "content_type": segment.get("type", "unknown"),
                            "confidence": 1.0,
                        },
                        "validated_variants": [],
                        "validation_statistics": {
                            "skipped": True,
                            "reason": f"type={segment.get('type')} is not rewritable",
                        },
                        "agent_result": None,
                    })
                    continue

                # Agenten-Aufruf (Variante A oder B)
                for _ in range(self.num_variants):
                    agent_result = self._run_agent(
                        segment=segment,
                        domain_hint=domain,
                    )

                    agent_stats["total_tool_calls"] += len(agent_result.get("tool_calls", []))
                    agent_stats["total_attempts"] += agent_result.get("attempts", 1)
                    if agent_result.get("is_valid"):
                        agent_stats["valid_variants"] += 1
                    else:
                        agent_stats["invalid_variants"] += 1

                    # In assembly-kompatibles Format konvertieren
                    variant_text = agent_result.get("variant")
                    validated_variants = []
                    if variant_text:
                        validated_variants.append({
                            "variant_id": 1,
                            "text": variant_text,
                            "attempts": agent_result.get("attempts", 1),
                            "validation": {
                                "is_valid": agent_result.get("is_valid", False),
                                "issues": [],
                            },
                        })

                    segments_with_variants.append({
                        "original_segment": segment,
                        "classification": {
                            "domain": agent_result.get("domain", domain),
                            "content_type": segment.get("type", "task"),
                        },
                        "validated_variants": validated_variants,
                        "validation_statistics": {
                            "total": 1,
                            "valid": 1 if agent_result.get("is_valid") else 0,
                            "invalid": 0 if agent_result.get("is_valid") else 1,
                        },
                        "agent_result": agent_result,
                    })

            pipeline_stats["agent"] = agent_stats
            logger.info(
                f"  Agenten-Phase: "
                f"{agent_stats['valid_variants']} valide, "
                f"{agent_stats['invalid_variants']} invalide, "
                f"{agent_stats['total_tool_calls']} Tool-Calls gesamt"
            )

            # =================================================================
            # PHASE 3: Assembly (bestehende AssemblyChain)
            # =================================================================
            logger.info("Phase 3/3: Assembly...")
            assembly_result = self.assembly_chain.invoke({
                "segments_with_variants": segments_with_variants,
                "metadata": {
                    "pdf_path": str(pdf_path),
                    "domain": self.domain,
                    "variant": self.variant,
                    "num_variants_requested": self.num_variants,
                    **pipeline_stats["parsing"],
                },
            })
            pipeline_stats["assembly"] = assembly_result["statistics"]

            save_result = self.assembly_chain.save_to_file(
                assembly_result["assembled_document"],
                output_path,
            )

            # Zusätzlich: Agent-Statistiken als JSON speichern
            agent_json_path = output_path.parent / f"{output_path.stem}_agent_stats.json"
            agent_json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(agent_json_path, "w", encoding="utf-8") as f:
                # Tool-Call-Sequenzen für alle Segmente
                export = {
                    "variant": self.variant,
                    "segments": [
                        {
                            "idx": i,
                            "domain": sw.get("classification", {}).get("domain"),
                            "agent_result": {
                                k: v for k, v in (sw.get("agent_result") or {}).items()
                                if k != "variant"  # Text nicht doppelt speichern
                            },
                        }
                        for i, sw in enumerate(segments_with_variants, 1)
                        if sw.get("agent_result")
                    ],
                }
                json.dump(export, f, indent=2, ensure_ascii=False)

            total_time = time.time() - start_time
            logger.info(f"✅ AgentPipeline abgeschlossen in {total_time:.2f}s")

            return {
                "success": True,
                "output_files": save_result["saved_files"] + [str(agent_json_path)],
                "statistics": {**pipeline_stats, "total_time": total_time},
                "assembled_document": assembly_result["assembled_document"],
            }

        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"AgentPipeline fehlgeschlagen: {e}")
            return {
                "success": False,
                "error": str(e),
                "statistics": {**pipeline_stats, "total_time": total_time},
            }


def get_pipeline(
    variant: str = "orchestrator",
    domain: str = None,
    num_variants: int = 1,
    max_retries: int = 3,
) -> LangChainAgentPipeline:
    """Factory für LangChainAgentPipeline."""
    return LangChainAgentPipeline(
        variant=variant,
        domain=domain,
        num_variants=num_variants,
        max_retries=max_retries,
    )
