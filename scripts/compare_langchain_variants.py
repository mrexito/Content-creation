#!/usr/bin/env python3
"""
compare_langchain_variants.py

Direkter Vergleich der drei LangChain-Varianten auf identischen Inputs:

  Variante 1 — langchain_pipeline
    LCEL-Chains (RewritingChain + ValidationChain), sequenziell, kein Retry.
    NOTE: Classification läuft einmalig in Phase 1 (shared). In Phase 2 nur
    Rewriting + Validation, da die Pipeline-Klasse keine isolierten Segment-
    Entry-Points bietet — daher direkter Aufruf der Chain-Klassen.

  Variante 2 — agent_orchestrator
    AgentExecutor mit 3 Tools. Das LLM steuert Reihenfolge und Retry autonom.
    Entry-Point: langchain_agent_prototype.orchestrator.agent.run_orchestrator()

  Variante 3 — agent_multi
    3 spezialisierte Einzelagenten (Classifier → Rewriter → Validator), je 1 Tool.
    Kein Retry-Koordinator — degeneriert strukturell zur sequenziellen Pipeline.
    Entry-Point: langchain_agent_prototype.multi_agent.pipeline.run_multi_agent_pipeline()

Usage:
    python scripts/compare_langchain_variants.py \\
        --pdf data/input/math/equations_simple.pdf \\
        --domain mathematics \\
        --variants 1 \\
        --retries 3 \\
        --llm-provider auto
"""

import sys
import json
import argparse
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.constants import NON_REWRITABLE_TYPES, normalize_domain
from common.logger import setup_logger
from langchain_prototype.chains.parsing_chain import get_parsing_chain
from langchain_prototype.chains.segmentation_chain import get_segmentation_chain
from langchain_prototype.chains.classification_chain import get_classification_chain
from langchain_prototype.chains.rewriting_chain import get_rewriting_chain
from langchain_prototype.chains.validation_chain import get_validation_chain
from langchain_agent_prototype.orchestrator.agent import run_orchestrator
from langchain_agent_prototype.multi_agent.pipeline import run_multi_agent_pipeline

logger = setup_logger(__name__)

SEGMENT_TIMEOUT = 120  # Sekunden pro Segment


# ─────────────────────────────────────────────────────────────────────────────
# Timeout-Helper (threading, kompatibel mit Unix + macOS)
# ─────────────────────────────────────────────────────────────────────────────

class SegmentTimeoutError(Exception):
    """Raised wenn ein Segment-Aufruf das Timeout überschreitet."""


def _run_with_timeout(fn, timeout: int = SEGMENT_TIMEOUT):
    """Führt fn() in einem Thread aus; wirft SegmentTimeoutError bei Timeout."""
    result_box: List[Any] = [None]
    error_box: List[Optional[Exception]] = [None]

    def _worker():
        try:
            result_box[0] = fn()
        except Exception as exc:
            error_box[0] = exc

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        raise SegmentTimeoutError(f"Timeout nach {timeout}s")
    if error_box[0] is not None:
        raise error_box[0]
    return result_box[0]


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Shared Preprocessing
# ─────────────────────────────────────────────────────────────────────────────

def run_shared_preprocessing(
    pdf_path: Path,
    domain: Optional[str],
) -> Dict[str, Any]:
    """
    OCR → Segmentierung → Klassifizierung → Filter NON_REWRITABLE_TYPES.

    Läuft einmalig; alle drei Varianten erhalten dieselbe Segmentliste.

    Returns:
        {
          'segments':        List[Dict] — rewritable Segmente mit '_classification'
          'total_segments':  int
          'skipped_count':   int
          'parse_meta':      Dict
        }
    """
    logger.info("=" * 60)
    logger.info("PHASE 1: Shared Preprocessing")
    logger.info("=" * 60)

    parsing_chain = get_parsing_chain(domain=domain)
    segmentation_chain = get_segmentation_chain()
    classification_chain = get_classification_chain()

    # --- 1. OCR / Parsing ---
    logger.info("  [1/3] OCR / Parsing...")
    parse_result = parsing_chain.invoke({"pdf_path": str(pdf_path)})
    if not parse_result["success"]:
        raise RuntimeError(
            f"Parsing fehlgeschlagen: {parse_result['metadata'].get('error')}"
        )
    text = parse_result["text"]
    parse_meta = parse_result["metadata"]
    logger.info(
        f"  → {len(text)} Zeichen, Tool: {parse_meta.get('tool_used', 'unknown')}"
    )

    # --- 2. Segmentation ---
    logger.info("  [2/3] Segmentierung...")
    seg_result = segmentation_chain.invoke({"text": text})
    if not seg_result["success"]:
        raise RuntimeError("Segmentierung fehlgeschlagen")
    segments = seg_result["segments"]
    logger.info(f"  → {len(segments)} Segmente total")

    # --- 3. Classification + Filter ---
    logger.info("  [3/3] Klassifizierung + Filter...")
    classified: List[Dict] = []
    skipped_count = 0

    for seg in segments:
        seg_type = seg.get("type", "unknown")
        if seg_type in NON_REWRITABLE_TYPES:
            skipped_count += 1
            continue
        cls_result = classification_chain.invoke({"segment": seg})
        if not cls_result["success"]:
            logger.warning(
                f"  Klassifizierung fehlgeschlagen für: {seg.get('text', '')[:50]!r}"
            )
            continue
        enriched = dict(seg)
        enriched["_classification"] = cls_result["classification"]
        enriched["_pdf_source"] = pdf_path.name
        classified.append(enriched)

    logger.info(
        f"  → {len(classified)} rewritable Segmente, "
        f"{skipped_count} übersprungen (non-rewritable)"
    )
    return {
        "segments": classified,
        "total_segments": len(segments),
        "skipped_count": skipped_count,
        "parse_meta": parse_meta,
        "pdf_name": pdf_path.name,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: Per-Variante Verarbeitung
# ─────────────────────────────────────────────────────────────────────────────

def _process_pipeline_segment(
    segment: Dict,
    domain: str,
    rewriting_chain,
    validation_chain,
) -> Dict[str, Any]:
    """
    LangChain-Pipeline für ein Segment: RewritingChain → ValidationChain.

    NOTE: LangChainPipeline.process_pdf() ist kein geeigneter Entry-Point für
    Segment-level-Vergleiche (kein OCR-Skip, kein Segment-Input). Daher wird
    hier direkt mit den Chain-Klassen gearbeitet — identisches Verhalten zur
    Pipeline, ohne den OCR/Segmentierungs-Overhead.

    LLM-Calls: 1 (RewritingChain). ValidationChain ist regelbasiert (SymPy /
    BERTScore / Zahlencheck) — kein weiterer LLM-Aufruf.
    """
    rw_result = rewriting_chain.invoke({"segment": segment, "domain": domain})
    if not rw_result["success"]:
        return {
            "variant_text": None,
            "is_valid": False,
            "attempts": 1,
            "tool_calls_count": 1,
            "success": False,
            "error": "rewriting_failed",
        }

    val_result = validation_chain.invoke(
        {
            "original": rw_result["original"],
            "variants": rw_result["variants"],
            "domain": domain,
        }
    )

    validated = val_result.get("validated_variants", [])
    best = next(
        (v for v in validated if v.get("validation", {}).get("is_valid")), None
    )
    if best is None and validated:
        best = validated[0]

    is_valid = best.get("validation", {}).get("is_valid", False) if best else False
    variant_text = best.get("text") if best else None

    return {
        "variant_text": variant_text,
        "is_valid": is_valid,
        "attempts": 1,
        "tool_calls_count": 1,  # 1 LLM call: rewrite (validation ist regelbasiert)
        "success": variant_text is not None,
    }


def _normalize_agent_result(raw: Dict) -> Dict[str, Any]:
    """Normalisiert run_orchestrator / run_multi_agent_pipeline Output."""
    return {
        "variant_text": raw.get("variant"),
        "is_valid": raw.get("is_valid", False),
        "attempts": raw.get("attempts", 1),
        "tool_calls_count": len(raw.get("tool_calls", [])),
        "success": raw.get("success", False),
    }


def run_variant(
    variant_name: str,
    segments: List[Dict],
    domain: Optional[str],
    num_variants: int,
    max_retries: int,
    rewriting_chain=None,
    validation_chain=None,
) -> Dict[str, Any]:
    """
    Verarbeitet alle Segmente mit einer Variante.

    Returns:
        {
          'variant':         str
          'segment_results': List[Dict]  — ein Eintrag pro Segment
          'total_time':      float
          'all_failed':      bool
        }
    """
    logger.info(f"\n  ── Variante: {variant_name} ──")
    segment_results: List[Dict] = []
    phase_start = time.time()
    error_count = 0

    for idx, seg in enumerate(segments, 1):
        cls = seg.get("_classification", {})
        seg_domain = normalize_domain(cls.get("domain", domain or "general"))
        preview = seg.get("text", "")[:50].replace("\n", " ")

        logger.info(f"  [{variant_name}] Seg {idx}/{len(segments)}: {preview!r}")
        t0 = time.time()

        try:
            if variant_name == "langchain_pipeline":
                seg_result = _run_with_timeout(
                    lambda s=seg, d=seg_domain: _process_pipeline_segment(
                        s, d, rewriting_chain, validation_chain
                    )
                )
            elif variant_name == "agent_orchestrator":
                raw = _run_with_timeout(
                    lambda s=seg, d=seg_domain: run_orchestrator(
                        segment=s, domain_hint=d, max_retries=max_retries
                    )
                )
                seg_result = _normalize_agent_result(raw)
            elif variant_name == "agent_multi":
                raw = _run_with_timeout(
                    lambda s=seg: run_multi_agent_pipeline(
                        segment=s, max_retries=max_retries
                    )
                )
                seg_result = _normalize_agent_result(raw)
            else:
                raise ValueError(f"Unbekannte Variante: {variant_name}")

        except SegmentTimeoutError as exc:
            logger.warning(f"  [{variant_name}] Seg {idx}: {exc}")
            seg_result = {
                "variant_text": None,
                "is_valid": False,
                "attempts": 0,
                "tool_calls_count": 0,
                "success": False,
                "error": str(exc),
            }
            error_count += 1
        except Exception as exc:
            logger.error(f"  [{variant_name}] Seg {idx} Fehler: {exc}")
            seg_result = {
                "variant_text": None,
                "is_valid": False,
                "attempts": 0,
                "tool_calls_count": 0,
                "success": False,
                "error": str(exc),
            }
            error_count += 1

        seg_result["elapsed_seconds"] = time.time() - t0
        segment_results.append(seg_result)

    total_time = time.time() - phase_start
    all_failed = error_count == len(segments) and len(segments) > 0

    if all_failed:
        logger.error(f"  [{variant_name}] Alle {len(segments)} Segmente fehlgeschlagen!")

    return {
        "variant": variant_name,
        "segment_results": segment_results,
        "total_time": total_time,
        "all_failed": all_failed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Metriken berechnen
# ─────────────────────────────────────────────────────────────────────────────

def compute_metrics(variant_result: Dict) -> Dict[str, Any]:
    """Berechnet Aggregat-Metriken für eine Variante."""
    results = variant_result["segment_results"]
    n = len(results)
    if n == 0:
        return {
            "validation_rate": 0.0,
            "avg_time_per_segment": 0.0,
            "total_time": variant_result["total_time"],
            "total_llm_calls": 0,
            "avg_llm_calls_per_segment": 0.0,
        }

    valid_count = sum(1 for r in results if r.get("is_valid"))
    total_llm = sum(r.get("tool_calls_count", 0) for r in results)
    times = [r.get("elapsed_seconds", 0) for r in results]

    return {
        "validation_rate": valid_count / n,
        "avg_time_per_segment": sum(times) / n,
        "total_time": variant_result["total_time"],
        "total_llm_calls": total_llm,
        "avg_llm_calls_per_segment": total_llm / n,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phase 4: Output
# ─────────────────────────────────────────────────────────────────────────────

VARIANT_LABELS = {
    "langchain_pipeline": "LC Pipeline",
    "agent_orchestrator": "Orchestrator",
    "agent_multi":        "Multi-Agent",
}


def print_table(variants: List[str], metrics: Dict[str, Dict], failed: Dict[str, bool]):
    """Gibt die Vergleichstabelle auf stdout aus."""
    cols = [VARIANT_LABELS.get(v, v) for v in variants]
    col_w = 14

    def row(label, values):
        cells = "".join(f" {v:>{col_w}} │" for v in values)
        print(f"│ {label:<22}│{cells}")

    sep_top = "┌" + "─" * 24 + "┬" + ("─" * (col_w + 2) + "┬") * len(cols)
    sep_top = sep_top.rstrip("┬") + "┐"
    sep_mid = "├" + "─" * 24 + "┼" + ("─" * (col_w + 2) + "┼") * len(cols)
    sep_mid = sep_mid.rstrip("┼") + "┤"
    sep_bot = "└" + "─" * 24 + "┴" + ("─" * (col_w + 2) + "┴") * len(cols)
    sep_bot = sep_bot.rstrip("┴") + "┘"

    header_cells = "".join(f" {c:>{col_w}} │" for c in cols)

    print()
    print(sep_top)
    print(f"│ {'Metrik':<22}│{header_cells}")
    print(sep_mid)

    def fmt_val(v, variant, fmt):
        if failed.get(variant):
            return "FAILED"
        m = metrics.get(variant, {})
        return fmt.format(m.get(v, 0))

    for label, key, fmt in [
        ("Validation Rate",       "validation_rate",          "{:.0%}"),
        ("Avg Time/Segment (s)",  "avg_time_per_segment",     "{:.1f}"),
        ("Total Time (s)",        "total_time",                "{:.1f}"),
        ("Avg LLM-Calls/Seg",     "avg_llm_calls_per_segment","{:.1f}"),
        ("Total LLM-Calls",       "total_llm_calls",           "{:.0f}"),
    ]:
        values = [fmt_val(key, v, fmt) for v in variants]
        row(label, values)

    print(sep_bot)
    print()


def print_observations(variants: List[str], metrics: Dict, failed: Dict, total_segments: int = 0):
    """Automatisch generierte Beobachtungen."""
    print("Beobachtungen:")

    if total_segments > 0:
        print(f"  – Verarbeitete Segmente total: {total_segments} (über alle PDFs der Domain)")

    active = [v for v in variants if not failed.get(v)]
    if len(active) < 2:
        print("  – Zu wenige Varianten für Vergleich.")
        return

    m = {v: metrics[v] for v in active}

    # Overhead-Faktor Orchestrator vs. Pipeline
    if "langchain_pipeline" in m and "agent_orchestrator" in m:
        t_pipe = m["langchain_pipeline"]["total_time"]
        t_orch = m["agent_orchestrator"]["total_time"]
        if t_pipe > 0:
            factor = t_orch / t_pipe
            print(
                f"  – Zeitlicher Overhead Orchestrator vs. Pipeline: "
                f"×{factor:.1f} ({t_orch:.1f}s / {t_pipe:.1f}s)"
            )

    # Multi-Agent vs. Pipeline Validation-Rate (These: degeneriert)
    if "langchain_pipeline" in m and "agent_multi" in m:
        vr_pipe = m["langchain_pipeline"]["validation_rate"]
        vr_multi = m["agent_multi"]["validation_rate"]
        diff = abs(vr_pipe - vr_multi)
        if diff < 0.10:
            print(
                f"  – Multi-Agent Validation-Rate ({vr_multi:.0%}) liegt nahe bei "
                f"Pipeline ({vr_pipe:.0%}) — These bestätigt: degeneriert zur "
                f"sequenziellen Ausführung."
            )
        else:
            print(
                f"  – Multi-Agent Validation-Rate ({vr_multi:.0%}) vs. "
                f"Pipeline ({vr_pipe:.0%}) — Differenz {diff:.0%}."
            )

    # LLM-Call-Verhältnis
    if "langchain_pipeline" in m and "agent_orchestrator" in m:
        calls_pipe = m["langchain_pipeline"]["avg_llm_calls_per_segment"]
        calls_orch = m["agent_orchestrator"]["avg_llm_calls_per_segment"]
        if calls_pipe > 0:
            ratio = calls_orch / calls_pipe
            print(
                f"  – LLM-Calls/Segment: Orchestrator ×{ratio:.1f} mehr als Pipeline "
                f"({calls_orch:.1f} vs. {calls_pipe:.1f})"
            )

    print()


def save_json(
    output_dir: Path,
    domain: str,
    pdf_names: List[str],
    preprocessing_list: List[Dict],
    variant_results: List[Dict],
    metrics: Dict,
    failed: Dict,
    all_segments: Optional[List[Dict]] = None,
):
    """Speichert Rohdaten als JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comparison_{domain}_{ts}.json"
    out_path = output_dir / filename

    # ── Segment-Level-Daten: Input + Output pro Agent ────────────────────────
    segments_data: List[Dict] = []
    if all_segments:
        for i, seg in enumerate(all_segments):
            seg_entry: Dict[str, Any] = {
                "index": i,
                "pdf": seg.get("_pdf_source", "unknown"),
                "type": seg.get("type", "unknown"),
                "input_text": seg.get("text", ""),
                "agents": {},
            }
            for vr in variant_results:
                vname = vr["variant"]
                if i < len(vr["segment_results"]):
                    r = vr["segment_results"][i]
                    seg_entry["agents"][vname] = {
                        "output_text": r.get("variant_text"),
                        "is_valid": r.get("is_valid"),
                        "attempts": r.get("attempts"),
                        "tool_calls_count": r.get("tool_calls_count"),
                        "elapsed_seconds": round(r.get("elapsed_seconds", 0), 3),
                        "error": r.get("error"),
                    }
            segments_data.append(seg_entry)

    payload = {
        "timestamp": datetime.now().isoformat(),
        "pdfs": pdf_names,
        "domain": domain,
        "preprocessing": {
            "total_segments":     sum(p["total_segments"] for p in preprocessing_list),
            "rewritable_segments": sum(len(p["segments"]) for p in preprocessing_list),
            "skipped_count":      sum(p["skipped_count"] for p in preprocessing_list),
            "per_pdf": [
                {
                    "pdf": p["pdf_name"],
                    "total_segments": p["total_segments"],
                    "rewritable_segments": len(p["segments"]),
                    "skipped_count": p["skipped_count"],
                }
                for p in preprocessing_list
            ],
        },
        "segments": segments_data,
        "variants": {
            vr["variant"]: {
                "status": "failed" if failed.get(vr["variant"]) else "ok",
                "metrics": metrics.get(vr["variant"], {}),
            }
            for vr in variant_results
        },
    }

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    logger.info(f"JSON gespeichert: {out_path}")
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# Default-PDFs pro Domain (für --all-domains)
# ─────────────────────────────────────────────────────────────────────────────

_SCRIPT_DIR = Path(__file__).parent.parent  # Repo-Root

_DOMAIN_INPUT_DIRS: Dict[str, Path] = {
    "mathematics": _SCRIPT_DIR / "data" / "input" / "math",
    "languages":   _SCRIPT_DIR / "data" / "input" / "languages",
    "economics":   _SCRIPT_DIR / "data" / "input" / "economics",
}


def get_domain_pdfs(domain: str) -> List[Path]:
    """
    Gibt alle .pdf-Dateien im Input-Verzeichnis der Domain zurück.
    Mapping: mathematics → data/input/math/
             languages   → data/input/languages/
             economics   → data/input/economics/
    Gibt leere Liste zurück wenn Verzeichnis nicht existiert.
    """
    d = _DOMAIN_INPUT_DIRS.get(domain)
    if d is None or not d.exists():
        return []
    return sorted(d.glob("*.pdf"))


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Vergleich der drei LangChain-Varianten auf identischen Inputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Beispiele:\n"
            "  # Einzelne Domain:\n"
            "  python scripts/compare_langchain_variants.py \\\n"
            "      --pdf data/input/math/equations_simple.pdf --domain mathematics\n\n"
            "  # Alle Domänen (Default-PDFs):\n"
            "  python scripts/compare_langchain_variants.py --all-domains\n\n"
            "  # Alle Domänen, nur Pipeline + Orchestrator:\n"
            "  python scripts/compare_langchain_variants.py --all-domains --skip-multi"
        ),
    )
    p.add_argument("--pdf", type=Path, default=None, help="Pfad zur Input-PDF (nicht nötig bei --all-domains)")
    p.add_argument(
        "--domain",
        default=None,
        choices=["mathematics", "languages", "economics", "math", "lang", "econ"],
        help="Domain: mathematics | languages | economics (nicht nötig bei --all-domains)",
    )
    p.add_argument(
        "--all-domains",
        action="store_true",
        help=(
            "Alle drei Domänen nacheinander ausführen. "
            "Verwendet Default-PDFs pro Domain (überschreibt --pdf / --domain)."
        ),
    )
    p.add_argument("--variants", type=int, default=1, help="Varianten pro Segment (default: 1)")
    p.add_argument("--retries", type=int, default=3, help="Max Retries für Orchestrator (default: 3)")
    p.add_argument(
        "--llm-provider",
        default="auto",
        choices=["auto", "openai", "bfh"],
        help="LLM-Provider (default: auto)",
    )
    p.add_argument("--llm-model", default="", help="Modellname (optional)")
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/output/langchain_comparison"),
        help="Output-Verzeichnis (default: data/output/langchain_comparison)",
    )
    p.add_argument("--skip-pipeline",     action="store_true", help="langchain_pipeline überspringen")
    p.add_argument("--skip-orchestrator", action="store_true", help="agent_orchestrator überspringen")
    p.add_argument("--skip-multi",        action="store_true", help="agent_multi überspringen")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Single-Domain Run (extrahiert für Wiederverwendung in --all-domains)
# ─────────────────────────────────────────────────────────────────────────────

def run_single_domain(
    pdf_paths: List[Path],
    domain: str,
    active_variants: List[str],
    num_variants: int,
    max_retries: int,
    output_dir: Path,
) -> Optional[Path]:
    """
    Führt den vollständigen Vergleich für eine Domain aus.
    Verarbeitet alle übergebenen PDFs; Segmente werden über alle PDFs aggregiert.
    Gibt den Pfad zur gespeicherten JSON-Datei zurück (oder None bei Fehler).
    """
    if not pdf_paths:
        print(f"  Fehler: Keine PDFs für Domain '{domain}'.", file=sys.stderr)
        return None

    print()
    print("█" * 60)
    print(f"  DOMAIN: {domain.upper()}  |  {len(pdf_paths)} PDF(s)")
    print("█" * 60)

    # ── Phase 1: Preprocessing aller PDFs, Segmente aggregieren ─────────────
    all_segments: List[Dict] = []
    preprocessing_list: List[Dict] = []

    for i, pdf_path in enumerate(pdf_paths, 1):
        print(f"\n  PDF {i}/{len(pdf_paths)}: {pdf_path.name}")
        if not pdf_path.exists():
            print(f"  Warnung: PDF nicht gefunden: {pdf_path} — überspringe.", file=sys.stderr)
            continue
        try:
            preprocessing = run_shared_preprocessing(pdf_path, domain)
        except Exception as exc:
            print(f"  Warnung: Preprocessing fehlgeschlagen für {pdf_path.name}: {exc}", file=sys.stderr)
            continue
        preprocessing_list.append(preprocessing)
        all_segments.extend(preprocessing["segments"])

    if not all_segments:
        print("  Keine rewritable Segmente gefunden — Domain übersprungen.", file=sys.stderr)
        return None

    # ── Phase 2: Varianten auf aggregierten Segmenten ────────────────────────
    rewriting_chain = None
    validation_chain = None
    if "langchain_pipeline" in active_variants:
        rewriting_chain = get_rewriting_chain(num_variants=num_variants)
        validation_chain = get_validation_chain()

    print()
    print("=" * 60)
    print("PHASE 2: Verarbeitung pro Variante")
    print(f"  Segmente: {len(all_segments)} (aus {len(preprocessing_list)} PDF(s))  |  Domain: {domain}")
    print("=" * 60)

    variant_results: List[Dict] = []
    for vname in active_variants:
        vr = run_variant(
            variant_name=vname,
            segments=all_segments,
            domain=domain,
            num_variants=num_variants,
            max_retries=max_retries,
            rewriting_chain=rewriting_chain,
            validation_chain=validation_chain,
        )
        variant_results.append(vr)

    metrics = {vr["variant"]: compute_metrics(vr) for vr in variant_results}
    failed  = {vr["variant"]: vr["all_failed"] for vr in variant_results}

    print("=" * 60)
    print(f"ERGEBNIS: {domain.upper()}")
    print("=" * 60)
    print_table(active_variants, metrics, failed)
    print_observations(active_variants, metrics, failed, total_segments=len(all_segments))

    return save_json(
        output_dir=output_dir,
        domain=domain,
        pdf_names=[p.name for p in pdf_paths if p.exists()],
        preprocessing_list=preprocessing_list,
        variant_results=variant_results,
        metrics=metrics,
        failed=failed,
        all_segments=all_segments,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # Validierung: --pdf/--domain sind Pflicht ohne --all-domains
    if not args.all_domains:
        if args.pdf is None or args.domain is None:
            print(
                "Fehler: --pdf und --domain sind erforderlich (oder --all-domains verwenden).",
                file=sys.stderr,
            )
            sys.exit(1)

    # LLM Handler initialisieren
    from common.llm_handler import reset_llm_handler, get_llm_handler
    reset_llm_handler()
    get_llm_handler(
        provider=args.llm_provider,
        model=args.llm_model if args.llm_model else None,
    )

    # Varianten-Auswahl
    active_variants: List[str] = []
    if not args.skip_pipeline:
        active_variants.append("langchain_pipeline")
    if not args.skip_orchestrator:
        active_variants.append("agent_orchestrator")
    if not args.skip_multi:
        active_variants.append("agent_multi")

    if not active_variants:
        print("Alle Varianten übersprungen — nichts zu tun.", file=sys.stderr)
        sys.exit(1)

    # ── Alle Domänen ────────────────────────────────────────────────────────
    if args.all_domains:
        DOMAINS = ["mathematics", "languages", "economics"]
        print(f"\nStarte alle {len(DOMAINS)} Domänen: {', '.join(DOMAINS)}")

        saved_files: List[Path] = []
        for domain in DOMAINS:
            pdf_paths = get_domain_pdfs(domain)
            if not pdf_paths:
                print(f"  Keine PDFs gefunden für Domain '{domain}' — überspringe.")
                continue
            print(f"  {domain}: {len(pdf_paths)} PDF(s) gefunden: "
                  f"{', '.join(p.name for p in pdf_paths)}")
            out = run_single_domain(
                pdf_paths=pdf_paths,
                domain=domain,
                active_variants=active_variants,
                num_variants=args.variants,
                max_retries=args.retries,
                output_dir=args.output_dir,
            )
            if out:
                saved_files.append(out)

        print("\n" + "=" * 60)
        print("ALLE DOMÄNEN ABGESCHLOSSEN")
        print("=" * 60)
        for f in saved_files:
            print(f"  {f}")
        return

    # ── Einzelne Domain ─────────────────────────────────────────────────────
    domain = normalize_domain(args.domain)
    out = run_single_domain(
        pdf_paths=[args.pdf],
        domain=domain,
        active_variants=active_variants,
        num_variants=args.variants,
        max_retries=args.retries,
        output_dir=args.output_dir,
    )
    if out:
        print(f"Rohdaten: {out}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
