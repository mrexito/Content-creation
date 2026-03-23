"""
evaluate_all_frameworks_mistral_ocr.py
=======================================
Identisch zu evaluate_all_frameworks.py, aber mit Mistral OCR für ALLE
drei Domains (math, languages, economics).

Setzt OCR_FORCE_MISTRAL=1 vor allen Imports, damit OCRHandler.__init__()
die domain_preferences auf 'mistral' überschreibt.

Usage:
    python scripts/evaluate_all_frameworks_mistral_ocr.py
    python scripts/evaluate_all_frameworks_mistral_ocr.py --domains languages
    python scripts/evaluate_all_frameworks_mistral_ocr.py --domains languages --no-agents
    python scripts/evaluate_all_frameworks_mistral_ocr.py --variants 1 --frameworks langchain langgraph hybrid
    python scripts/evaluate_all_frameworks_mistral_ocr.py --fast
"""
from __future__ import annotations

# WICHTIG: Muss VOR allen anderen Imports gesetzt werden, damit OCRHandler
# bei Initialisierung die env-Variable bereits liest.
import os
os.environ['OCR_FORCE_MISTRAL'] = '1'

import argparse
import json
import multiprocessing
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.config import Config
from common.llm_handler import reset_llm_handler

# ─── Konfiguration ────────────────────────────────────────────────────────────

DOMAIN_CONFIG: dict[str, dict] = {
    "math": {
        "pdfs": [
            "math/equations_simple.pdf",
            "math/equations_advanced.pdf",
            "math/word_problems.pdf",
        ],
        "label":     "Mathematik",
        "validator": "SymPy",
    },
    "languages": {
        "pdfs": [
            "languages/grammar_exercise.pdf",
            "languages/sentence_construction.pdf",
            "languages/verb_conjugation.pdf",
        ],
        "label":     "Sprachen",
        "validator": "BERTScore",
    },
    "economics": {
        "pdfs": [
            "economics/balance_sheet.pdf",
            "economics/income_statement.pdf",
            "economics/investment_calculation.pdf",
        ],
        "label":     "Wirtschaft",
        "validator": "ConsistencyCheck",
    },
}

ALL_FRAMEWORKS = [
    "langchain",
    "langgraph",
    "hybrid",
    "hybrid_agent",
    "agent_orchestrator",
    "agent_multi",
]
ALL_DOMAINS = ["math", "languages", "economics"]

TIMEOUT_SECONDS = 600  # 10 Minuten pro Run

EMOJI: dict[str, str] = {
    "langchain":          "🔗",
    "langgraph":          "🕸️ ",
    "hybrid":             "🔀",
    "hybrid_agent":       "🤖",
    "agent_orchestrator": "⚡",
    "agent_multi":        "📋",
}

FRAMEWORK_LABELS: dict[str, str] = {
    "langchain":          "LangChain",
    "langgraph":          "LangGraph",
    "hybrid":             "Hybrid",
    "hybrid_agent":       "Hybrid+Agent",
    "agent_orchestrator": "Agent Orchestrator",
    "agent_multi":        "Agent Multi-Step",
}

ARCHITECTURE_TABLE = [
    ("LangChain",          "Chain",      "Chain",            "Chain"),
    ("LangGraph",          "Node",       "StateGraph",       "Node"),
    ("Hybrid",             "LangChain",  "LangGraph",        "LangChain"),
    ("Hybrid+Agent",       "LangChain",  "AgentExecutor",    "LangChain"),
    ("Agent Orchestrator", "Chain",      "AgentExecutor",    "Chain"),
    ("Agent Multi-Step",   "Chain",      "3× AgentExecutor", "Chain"),
]

IS_AGENT = {"hybrid_agent", "agent_orchestrator", "agent_multi"}

STATUS = {True: "✅", False: "❌"}


# ─── Framework-Runner ─────────────────────────────────────────────────────────

def _run_langchain(pdf_path: Path, domain: str, num_variants: int) -> dict:
    from langchain_prototype.pipeline import get_pipeline
    reset_llm_handler()
    pipeline = get_pipeline(domain=domain, num_variants=num_variants)
    result   = pipeline.process_pdf(pdf_path)
    return _normalise_langchain(result, domain, pdf_path.name)


def _run_langgraph(pdf_path: Path, domain: str, num_variants: int) -> dict:
    from langgraph_prototype.graph import create_workflow_graph
    from langgraph_prototype.state.workflow_state import create_initial_state
    reset_llm_handler()
    graph = create_workflow_graph()
    state = create_initial_state(
        pdf_path=str(pdf_path),
        domain=domain,
        num_variants=num_variants,
    )
    start = time.time()
    final = graph.invoke(state)
    elapsed = time.time() - start
    return _normalise_langgraph(final, elapsed, domain, pdf_path.name)


def _run_hybrid(pdf_path: Path, domain: str, num_variants: int) -> dict:
    from hybrid_prototype.pipeline import get_pipeline as get_hybrid_pipeline
    reset_llm_handler()
    pipeline = get_hybrid_pipeline(domain=domain, num_variants=num_variants)
    result   = pipeline.process_pdf(pdf_path)
    return _normalise_hybrid(result, domain, pdf_path.name)


def _run_hybrid_agent(pdf_path: Path, domain: str, num_variants: int) -> dict:
    from hybrid_agent_prototype.pipeline import get_pipeline as get_hybrid_agent_pipeline
    reset_llm_handler()
    pipeline = get_hybrid_agent_pipeline(
        domain=domain, num_variants=num_variants, max_retries=3
    )
    result = pipeline.process_pdf(pdf_path)
    return _normalise_hybrid_agent(result, domain, pdf_path.name)


def _run_agent_orchestrator(pdf_path: Path, domain: str, num_variants: int) -> dict:
    from langchain_agent_prototype.pipeline import get_pipeline as get_agent_pipeline
    reset_llm_handler()
    pipeline = get_agent_pipeline(
        variant="orchestrator", domain=domain,
        num_variants=num_variants, max_retries=3,
    )
    result = pipeline.process_pdf(pdf_path)
    return _normalise_agent_pipeline(result, "agent_orchestrator", domain, pdf_path.name)


def _run_agent_multi(pdf_path: Path, domain: str, num_variants: int) -> dict:
    from langchain_agent_prototype.pipeline import get_pipeline as get_agent_pipeline
    reset_llm_handler()
    pipeline = get_agent_pipeline(
        variant="multi_agent", domain=domain,
        num_variants=num_variants, max_retries=3,
    )
    result = pipeline.process_pdf(pdf_path)
    return _normalise_agent_pipeline(result, "agent_multi", domain, pdf_path.name)


# ─── Normalisierung → einheitliches Schema ────────────────────────────────────

def _base_agent_metrics() -> dict:
    return {"tool_calls_total": None, "retries_total": None, "hallucinated_calls": None}


def _error_result(framework: str, domain: str, pdf_name: str, error: str) -> dict:
    return {
        "success":   False,
        "framework": framework,
        "domain":    domain,
        "pdf_name":  pdf_name,
        "error":     error,
        "metrics": {
            "total_time":      0.0,
            "ocr_time":        0.0,
            "ocr_tool":        "?",
            "num_segments":    0,
            "total_variants":  0,
            "valid_variants":  0,
            "validation_rate": 0.0,
            **_base_agent_metrics(),
        },
        "segments": [],
    }


def _seg_from_assembled(seg: dict) -> dict:
    """Konvertiert assembled_document-Segment ins einheitliche Schema."""
    variants = []
    for v in seg.get("variants", []):
        variants.append({
            "variant_id":        v.get("variant_id", 0),
            "text":              v.get("text", ""),
            "is_valid":          True,
            "validation_issues": [],
        })
    total = seg.get("num_variants", len(variants))
    return {
        "original_segment": {
            "text": seg.get("original", ""),
            "type": seg.get("segment_type", "unknown"),
        },
        "classification": seg.get("classification", {}),
        "validated_variants": variants,
        "validation_statistics": {"total": total, "valid": len(variants)},
    }


def _normalise_segments_with_variants(swv: list) -> list:
    """Für LangGraph segments_with_variants aus dem State."""
    result = []
    for seg in swv:
        orig         = seg.get("segment", {})
        raw_variants = seg.get("variants", [])
        variants = []
        for v in raw_variants:
            val      = v.get("validation", {}) if isinstance(v.get("validation"), dict) else {}
            is_valid = val.get("is_valid", False)
            issues   = val.get("issues", [])
            variants.append({
                "variant_id":        v.get("variant_id", 0),
                "text":              v.get("text", ""),
                "is_valid":          is_valid,
                "validation_issues": issues,
            })
        valid_count = sum(1 for v in variants if v["is_valid"])
        result.append({
            "original_segment": {
                "text": orig.get("text", "") if isinstance(orig, dict) else str(orig),
                "type": orig.get("segment_type", "unknown") if isinstance(orig, dict) else "unknown",
            },
            "classification":     seg.get("classification", {}),
            "validated_variants": variants,
            "validation_statistics": {"total": len(variants), "valid": valid_count},
        })
    return result


def _normalise_langchain(result: dict, domain: str, pdf_name: str) -> dict:
    if not result.get("success"):
        return _error_result("langchain", domain, pdf_name, result.get("error", "unknown"))

    stats    = result.get("statistics", {})
    assembly = stats.get("assembly", {})
    parsing  = stats.get("parsing", {})
    doc      = result.get("assembled_document", {})
    segments = [_seg_from_assembled(s) for s in doc.get("segments", [])]

    total_v = assembly.get("total_variants", 0)
    valid_v = assembly.get("valid_variants", 0)

    return {
        "success": True, "framework": "langchain", "domain": domain,
        "pdf_name": pdf_name, "error": None,
        "metrics": {
            "total_time":      round(stats.get("total_time", 0), 2),
            "ocr_time":        round(parsing.get("processing_time", 0), 2),
            "ocr_tool":        parsing.get("tool_used", "?"),
            "num_segments":    stats.get("segmentation", {}).get("num_segments", len(segments)),
            "total_variants":  total_v,
            "valid_variants":  valid_v,
            "validation_rate": round(valid_v / total_v, 4) if total_v else 0.0,
            **_base_agent_metrics(),
        },
        "segments": segments,
    }


def _normalise_langgraph(final: dict, elapsed: float, domain: str, pdf_name: str) -> dict:
    if final.get("errors"):
        return _error_result("langgraph", domain, pdf_name, str(final["errors"]))

    swv          = final.get("segments_with_variants") or []
    doc          = final.get("assembled_document") or {}
    segments_raw = doc.get("segments", []) if isinstance(doc, dict) else []

    if not swv and not segments_raw:
        phase = final.get("current_phase", "unknown")
        errs  = final.get("errors") or []
        msg   = f"Keine Segmente produziert (Phase: {phase})"
        if errs:
            msg += f" – {'; '.join(str(e) for e in errs)}"
        return _error_result("langgraph", domain, pdf_name, msg)

    segments = _normalise_segments_with_variants(swv) if swv else [
        _seg_from_assembled(s) for s in segments_raw
    ]

    total_v = sum(s["validation_statistics"]["total"] for s in segments)
    valid_v = sum(s["validation_statistics"]["valid"] for s in segments)
    ocr_meta = final.get("ocr_metadata", {}) or {}

    return {
        "success": True, "framework": "langgraph", "domain": domain,
        "pdf_name": pdf_name, "error": None,
        "metrics": {
            "total_time":      round(elapsed, 2),
            "ocr_time":        round(ocr_meta.get("processing_time", 0), 2),
            "ocr_tool":        ocr_meta.get("tool_used", "?"),
            "num_segments":    len(segments),
            "total_variants":  total_v,
            "valid_variants":  valid_v,
            "validation_rate": round(valid_v / total_v, 4) if total_v else 0.0,
            **_base_agent_metrics(),
        },
        "segments": segments,
    }


def _normalise_hybrid(result: dict, domain: str, pdf_name: str) -> dict:
    if not result.get("success"):
        return _error_result("hybrid", domain, pdf_name, result.get("error", "unknown"))

    stats       = result.get("statistics", {})
    preproc     = stats.get("preprocessing", {})
    graph_stats = stats.get("graph", {})
    doc         = result.get("assembled_document") or {}
    segments    = [_seg_from_assembled(s) for s in doc.get("segments", [])]

    total_valid   = graph_stats.get("total_valid", 0)
    total_invalid = graph_stats.get("total_invalid", 0)
    total_v = total_valid + total_invalid
    valid_v = total_valid

    return {
        "success": True, "framework": "hybrid", "domain": domain,
        "pdf_name": pdf_name, "error": None,
        "metrics": {
            "total_time":      round(stats.get("total_time", 0), 2),
            "ocr_time":        round(preproc.get("ocr_time", 0), 2),
            "ocr_tool":        preproc.get("ocr_tool", "?"),
            "num_segments":    preproc.get("segments", len(segments)),
            "total_variants":  total_v,
            "valid_variants":  valid_v,
            "validation_rate": round(valid_v / total_v, 4) if total_v else 0.0,
            **_base_agent_metrics(),
        },
        "segments": segments,
    }


def _normalise_hybrid_agent(result: dict, domain: str, pdf_name: str) -> dict:
    if not result.get("success"):
        return _error_result("hybrid_agent", domain, pdf_name, result.get("error", "unknown"))

    stats    = result.get("statistics", {})
    preproc  = stats.get("preprocessing", {})
    agent_st = stats.get("agent", {})
    doc      = result.get("assembled_document") or {}
    segments = [_seg_from_assembled(s) for s in doc.get("segments", [])]

    total_valid   = agent_st.get("total_valid", 0)
    total_invalid = agent_st.get("total_invalid", 0)
    total_v = total_valid + total_invalid
    valid_v = total_valid

    return {
        "success": True, "framework": "hybrid_agent", "domain": domain,
        "pdf_name": pdf_name, "error": None,
        "metrics": {
            "total_time":      round(stats.get("total_time", 0), 2),
            "ocr_time":        round(preproc.get("ocr_time", 0), 2),
            "ocr_tool":        preproc.get("ocr_tool", "?"),
            "num_segments":    preproc.get("segments", len(segments)),
            "total_variants":  total_v,
            "valid_variants":  valid_v,
            "validation_rate": round(valid_v / total_v, 4) if total_v else 0.0,
            "tool_calls_total":  agent_st.get("total_tool_calls"),
            "retries_total":     agent_st.get("total_retries"),
            "hallucinated_calls": agent_st.get("hallucinated_calls"),
        },
        "segments": segments,
    }


def _normalise_agent_pipeline(
    result: dict, framework: str, domain: str, pdf_name: str
) -> dict:
    """Normalisiert LangChainAgentPipeline.process_pdf()-Ergebnis."""
    if not result.get("success"):
        return _error_result(framework, domain, pdf_name, result.get("error", "unknown"))

    stats    = result.get("statistics", {})
    agent_st = stats.get("agent", {})
    parsing  = stats.get("parsing", {})
    doc      = result.get("assembled_document") or {}
    segments = [_seg_from_assembled(s) for s in doc.get("segments", [])]

    valid_v = agent_st.get("valid_variants", 0)
    invalid_v = agent_st.get("invalid_variants", 0)
    total_v = valid_v + invalid_v

    return {
        "success": True, "framework": framework, "domain": domain,
        "pdf_name": pdf_name, "error": None,
        "metrics": {
            "total_time":      round(stats.get("total_time", 0), 2),
            "ocr_time":        round(parsing.get("processing_time", 0), 2),
            "ocr_tool":        parsing.get("tool_used", "?"),
            "num_segments":    stats.get("segmentation", {}).get("num_segments", len(segments)),
            "total_variants":  total_v,
            "valid_variants":  valid_v,
            "validation_rate": round(valid_v / total_v, 4) if total_v else 0.0,
            "tool_calls_total":  agent_st.get("total_tool_calls"),
            "retries_total":     agent_st.get("total_attempts"),
            "hallucinated_calls": None,
        },
        "segments": segments,
    }


# ─── Timeout-Wrapper ──────────────────────────────────────────────────────────

def _runner_worker(
    queue: multiprocessing.Queue,
    runner_name: str,
    pdf_path_str: str,
    domain: str,
    num_variants: int,
) -> None:
    """Wird in einem separaten Prozess ausgeführt."""
    # Env-Variable muss auch im Subprocess gesetzt sein (wird via fork/spawn vererbt,
    # aber explizit setzen ist sicherer für spawn-basierte Prozesse)
    os.environ['OCR_FORCE_MISTRAL'] = '1'
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    try:
        pdf_path = Path(pdf_path_str)
        runner = _RUNNERS[runner_name]
        result = runner(pdf_path, domain, num_variants)
        queue.put(("ok", result))
    except Exception as exc:
        queue.put(("error", str(exc)))


def _run_with_timeout(
    framework: str,
    pdf_path: Path,
    domain: str,
    num_variants: int,
    timeout: int = TIMEOUT_SECONDS,
) -> dict:
    """
    Führt einen Framework-Runner in einem separaten Prozess aus.
    Bei Überschreitung von `timeout` Sekunden: Timeout-Fehler.
    """
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_runner_worker,
        args=(queue, framework, str(pdf_path), domain, num_variants),
        daemon=True,
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        return _error_result(
            framework, domain, pdf_path.name,
            f"Timeout nach {timeout}s überschritten"
        )

    if not queue.empty():
        status, payload = queue.get_nowait()
        if status == "ok":
            return payload
        return _error_result(framework, domain, pdf_path.name, payload)

    return _error_result(
        framework, domain, pdf_path.name,
        "Prozess beendet ohne Ergebnis (Exit-Code != 0)"
    )


# ─── Konsolen-Ausgabe ─────────────────────────────────────────────────────────

def _fmt_rate(r: dict) -> str:
    if not r["success"]:
        return "FEHLER"
    v = r["metrics"]["validation_rate"]
    return f"{v * 100:.0f}%"


def _fmt_time(r: dict) -> str:
    if not r["success"]:
        return "–"
    return f"{r['metrics']['total_time']:.1f}s"


def _fmt_valid(r: dict) -> str:
    if not r["success"]:
        return "–"
    m = r["metrics"]
    return f"{m['valid_variants']}/{m['total_variants']}"


def _fmt_agent(r: dict, key: str) -> str:
    v = r["metrics"].get(key)
    if v is None:
        return "–"
    return str(v)


def _print_domain_table(domain: str, domain_results: list[dict]) -> None:
    cfg = DOMAIN_CONFIG[domain]
    label = cfg["label"].upper()
    w = 70
    print(f"\n{'═' * w}")
    print(f"  DOMAIN: {label}  ({cfg['validator']})")
    print(f"{'═' * w}")

    col_fw    = 22
    col_time  = 8
    col_segs  = 6
    col_valid = 12
    col_rate  = 6
    col_ret   = 8
    col_tools = 7

    header = (
        f"  {'Framework':<{col_fw}}"
        f" {'Zeit':>{col_time}}"
        f" {'Segm.':>{col_segs}}"
        f" {'Valid/Total':>{col_valid}}"
        f" {'Rate':>{col_rate}}"
        f" {'Retries':>{col_ret}}"
        f" {'Tools':>{col_tools}}"
    )
    sep_line = f"  {'─' * (col_fw + col_time + col_segs + col_valid + col_rate + col_ret + col_tools + 6)}"

    # Group by PDF
    pdf_names = list(dict.fromkeys(r["pdf_name"] for r in domain_results))
    for pdf_name in pdf_names:
        print(f"\n  PDF: {pdf_name}")
        print(header)
        print(sep_line)
        for r in [x for x in domain_results if x["pdf_name"] == pdf_name]:
            fw    = r["framework"]
            icon  = EMOJI.get(fw, "  ")
            label_fw = f"{icon} {FRAMEWORK_LABELS.get(fw, fw)}"
            segs  = str(r["metrics"]["num_segments"]) if r["success"] else "–"
            line = (
                f"  {label_fw:<{col_fw}}"
                f" {_fmt_time(r):>{col_time}}"
                f" {segs:>{col_segs}}"
                f" {_fmt_valid(r):>{col_valid}}"
                f" {_fmt_rate(r):>{col_rate}}"
                f" {_fmt_agent(r, 'retries_total'):>{col_ret}}"
                f" {_fmt_agent(r, 'tool_calls_total'):>{col_tools}}"
            )
            print(line)


def _print_overall_summary(results: list[dict], frameworks: list[str]) -> None:
    w = 70
    print(f"\n{'═' * w}")
    print("  GESAMTÜBERSICHT (Ø über alle Domains)")
    print(f"{'═' * w}")

    col_fw   = 22
    col_time = 10
    col_rate = 8
    col_rank = 5

    header = (
        f"  {'Framework':<{col_fw}}"
        f" {'Ø Zeit':>{col_time}}"
        f" {'Ø Rate':>{col_rate}}"
        f" {'Rang':>{col_rank}}"
    )
    print(header)
    print(f"  {'─' * (col_fw + col_time + col_rate + col_rank + 3)}")

    # Berechne Durchschnittswerte pro Framework
    fw_avgs = []
    for fw in frameworks:
        fw_results = [r for r in results if r["framework"] == fw and r["success"]]
        if not fw_results:
            fw_avgs.append((fw, None, None))
            continue
        avg_time = sum(r["metrics"]["total_time"] for r in fw_results) / len(fw_results)
        avg_rate = sum(r["metrics"]["validation_rate"] for r in fw_results) / len(fw_results)
        fw_avgs.append((fw, avg_time, avg_rate))

    # Rang nach Validation-Rate (höher = besser), bei Gleichstand nach Zeit (kürzer = besser)
    ranked = sorted(
        [(fw, t, vr) for fw, t, vr in fw_avgs if vr is not None],
        key=lambda x: (-x[2], x[1]),
    )
    rank_map = {fw: i + 1 for i, (fw, _, _) in enumerate(ranked)}

    for fw, avg_time, avg_rate in fw_avgs:
        icon  = EMOJI.get(fw, "  ")
        label = f"{icon} {FRAMEWORK_LABELS.get(fw, fw)}"
        if avg_time is None:
            print(f"  {label:<{col_fw}} {'–':>{col_time}} {'–':>{col_rate}} {'–':>{col_rank}}")
        else:
            rank_str = f"#{rank_map.get(fw, '?')}"
            print(
                f"  {label:<{col_fw}}"
                f" {avg_time:.1f}s{' ':>{col_time - len(f'{avg_time:.1f}s')}}"
                f" {avg_rate * 100:.0f}%{' ':>{col_rate - len(f'{avg_rate * 100:.0f}%')}}"
                f" {rank_str:>{col_rank}}"
            )


def _print_failures(results: list[dict]) -> None:
    failures = [r for r in results if not r["success"]]
    if not failures:
        return
    print(f"\n⚠️  FEHLGESCHLAGENE RUNS ({len(failures)}):")
    for r in failures:
        fw    = FRAMEWORK_LABELS.get(r["framework"], r["framework"])
        print(f"  ❌  {fw} / {r['domain']}: {r.get('error', '?')[:100]}")


# ─── Markdown-Report ──────────────────────────────────────────────────────────

def _md_arch_table() -> str:
    lines = ["## 2. Architektur-Übersicht\n"]
    lines.append("| Framework | Phase 1 | Phase 2 | Phase 3 |")
    lines.append("|-----------|---------|---------|---------|")
    for name, p1, p2, p3 in ARCHITECTURE_TABLE:
        lines.append(f"| **{name}** | {p1} | {p2} | {p3} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def _md_summary(results: list[dict], frameworks: list[str]) -> str:
    lines = ["## 1. Zusammenfassung\n"]
    lines.append(
        "| Framework | Architektur | Ø Zeit (s) "
        "| Ø Validation-Rate | Ø Retries | Ø Tool-Calls |"
    )
    lines.append("|-----------|-------------|------------|--------------------|-----------|-------------|")

    arch_map = {
        "langchain":          "Chain → Chain → Chain",
        "langgraph":          "Node → StateGraph → Node",
        "hybrid":             "LC → LangGraph → LC",
        "hybrid_agent":       "LC → AgentExecutor → LC",
        "agent_orchestrator": "Chain → AgentExecutor → Chain",
        "agent_multi":        "Chain → 3× Agent → Chain",
    }

    for fw in frameworks:
        fw_results = [r for r in results if r["framework"] == fw and r["success"]]
        label = FRAMEWORK_LABELS.get(fw, fw)
        arch  = arch_map.get(fw, "–")
        if not fw_results:
            lines.append(f"| {label} | {arch} | – | – | – | – |")
            continue

        avg_time  = sum(r["metrics"]["total_time"] for r in fw_results) / len(fw_results)
        avg_rate  = sum(r["metrics"]["validation_rate"] for r in fw_results) / len(fw_results)
        retries   = [r["metrics"]["retries_total"] for r in fw_results if r["metrics"].get("retries_total") is not None]
        tools     = [r["metrics"]["tool_calls_total"] for r in fw_results if r["metrics"].get("tool_calls_total") is not None]
        avg_ret   = f"{sum(retries)/len(retries):.1f}" if retries else "–"
        avg_tools = f"{sum(tools)/len(tools):.1f}" if tools else "–"

        lines.append(
            f"| {label} | {arch} "
            f"| {avg_time:.1f} "
            f"| {avg_rate * 100:.0f}% "
            f"| {avg_ret} "
            f"| {avg_tools} |"
        )

    lines.append("")
    return "\n".join(lines) + "\n"


def _md_domain_section(domain: str, domain_results: list[dict]) -> str:
    cfg   = DOMAIN_CONFIG[domain]
    pdf_list = " | ".join(f"`{p}`" for p in cfg["pdfs"])
    lines = [f"---\n\n## 3.{['math', 'languages', 'economics'].index(domain) + 1} Domäne: {cfg['label']} (`{domain}`)\n",
             f"**PDFs:** {pdf_list} | **Validator:** {cfg['validator']}\n"]

    lines.append("\n### Metriken\n")
    pdf_names = list(dict.fromkeys(r["pdf_name"] for r in domain_results))
    for pdf_name in pdf_names:
        pdf_results = [r for r in domain_results if r["pdf_name"] == pdf_name]
        lines.append(f"**PDF:** `{pdf_name}`\n")
        lines.append(
            "| Framework | Segmente | Valide / Total | Rate | Zeit (s) "
            "| OCR | Tool-Calls | Retries | Halluziniert |"
        )
        lines.append(
            "|-----------|----------|----------------|------|----------|"
            "-----|------------|---------|--------------|"
        )
        for r in pdf_results:
            m  = r["metrics"]
            fw = FRAMEWORK_LABELS.get(r["framework"], r["framework"])
            if r["success"]:
                tc   = str(m.get("tool_calls_total"))  if m.get("tool_calls_total")  is not None else "–"
                ret  = str(m.get("retries_total"))      if m.get("retries_total")      is not None else "–"
                hall = str(m.get("hallucinated_calls")) if m.get("hallucinated_calls") is not None else "–"
                lines.append(
                    f"| {fw} | {m['num_segments']} "
                    f"| {m['valid_variants']} / {m['total_variants']} "
                    f"| {m['validation_rate'] * 100:.0f}% "
                    f"| {m['total_time']:.1f} "
                    f"| {m['ocr_tool']} "
                    f"| {tc} | {ret} | {hall} |"
                )
            else:
                lines.append(f"| {fw} | – | – | – | – | – | – | – | – |")
        lines.append("")

    lines.append("\n### Segment-Vergleich (Volltext)\n")
    first_pdf = pdf_names[0] if pdf_names else None
    first_pdf_results = [r for r in domain_results if r["pdf_name"] == first_pdf] if first_pdf else domain_results
    max_segs = max((len(r["segments"]) for r in first_pdf_results if r["success"]), default=0)

    if first_pdf:
        lines.append(f"_Segmentvergleich für erstes PDF: `{first_pdf}`_\n")

    for seg_idx in range(max_segs):
        original_text = ""
        original_type = ""
        for r in first_pdf_results:
            if r["success"] and seg_idx < len(r["segments"]):
                original_text = r["segments"][seg_idx]["original_segment"]["text"]
                original_type = r["segments"][seg_idx]["original_segment"].get("type", "?")
                break

        preview = original_text[:80].replace("\n", " ")
        if len(original_text) > 80:
            preview += "…"

        lines.append(f"#### Segment {seg_idx + 1} — `{original_type}` — _{preview}_\n")
        lines.append("**Original:**")
        lines.append("```")
        lines.append(original_text)
        lines.append("```\n")

        for r in first_pdf_results:
            fw   = r["framework"]
            icon = EMOJI.get(fw, "")
            label = FRAMEWORK_LABELS.get(fw, fw)
            if not r["success"]:
                lines.append(
                    f"**{icon} {label}:** ❌ Pipeline fehlgeschlagen "
                    f"— `{r.get('error','?')[:80]}`\n"
                )
                continue
            if seg_idx >= len(r["segments"]):
                lines.append(f"**{icon} {label}:** _(kein Segment #{seg_idx+1})_\n")
                continue

            seg   = r["segments"][seg_idx]
            cls   = seg.get("classification", {})
            cls_str = f"{cls.get('domain','?')} / {cls.get('content_type','?')}"
            stats   = seg["validation_statistics"]
            lines.append(
                f"**{icon} {label}** — Klassifiziert als `{cls_str}` "
                f"— {stats['valid']}/{stats['total']} valide\n"
            )

            variants = seg["validated_variants"]
            if not variants:
                lines.append("_Keine Varianten generiert (Segment übersprungen)_\n")
            else:
                for v in variants:
                    ok_str   = "✅ VALIDE" if v["is_valid"] else "❌ INVALID"
                    issues   = v.get("validation_issues", [])
                    issue_md = "\n> **Issues:** " + " | ".join(str(i) for i in issues) if issues else ""
                    lines.append("<details>")
                    lines.append(f"<summary>Variante {v['variant_id']} — {ok_str}</summary>\n")
                    lines.append("```")
                    lines.append(v["text"] if v["text"] else "(leer)")
                    lines.append("```")
                    if issue_md:
                        lines.append(issue_md)
                    lines.append("</details>\n")
            lines.append("")

    return "\n".join(lines)


def _md_agent_analysis(results: list[dict]) -> str:
    agent_results = [r for r in results if r["framework"] in IS_AGENT and r["success"]]
    if not agent_results:
        return ""

    lines = ["---\n\n## 4. Agent-spezifische Analyse\n"]
    lines.append(
        "_Diese Metriken sind nur für Frameworks mit AgentExecutor verfügbar._\n"
    )

    lines.append("### Tool-Call-Verteilung\n")
    lines.append("| Framework | Domain | Tool-Calls | Retries | Halluziniert | Valid-Rate |")
    lines.append("|-----------|--------|------------|---------|--------------|------------|")
    for r in agent_results:
        m     = r["metrics"]
        fw    = FRAMEWORK_LABELS.get(r["framework"], r["framework"])
        tc    = str(m.get("tool_calls_total", "–"))
        ret   = str(m.get("retries_total", "–"))
        hall  = str(m.get("hallucinated_calls", "–"))
        rate  = f"{m['validation_rate'] * 100:.0f}%"
        lines.append(f"| {fw} | {r['domain']} | {tc} | {ret} | {hall} | {rate} |")
    lines.append("")

    hall_data = [
        (r["framework"], r["domain"], r["metrics"].get("hallucinated_calls", 0))
        for r in agent_results
        if r["metrics"].get("hallucinated_calls") is not None
    ]
    if hall_data:
        total_hall = sum(h for _, _, h in hall_data)
        total_calls = sum(
            r["metrics"].get("tool_calls_total", 0) or 0
            for r in agent_results
        )
        if total_calls > 0:
            hall_rate = total_hall / total_calls * 100
            lines.append(
                f"**Halluzinations-Rate gesamt:** "
                f"{total_hall} / {total_calls} Tool-Events = {hall_rate:.1f}%\n"
            )

    lines.append("### Vergleich Retry-Effizienz: Agent vs. LangGraph\n")
    lines.append("| Domain | LangGraph (Retries) | Hybrid+Agent (Retries) | Agent Orch. (Retries) |")
    lines.append("|--------|---------------------|------------------------|----------------------|")
    for domain in ALL_DOMAINS:
        lg = next((r for r in results if r["framework"] == "langgraph" and r["domain"] == domain), None)
        ha = next((r for r in results if r["framework"] == "hybrid_agent" and r["domain"] == domain), None)
        ao = next((r for r in results if r["framework"] == "agent_orchestrator" and r["domain"] == domain), None)

        def _ret(r):
            if r is None or not r.get("success"):
                return "–"
            v = r["metrics"].get("retries_total")
            return str(v) if v is not None else "–"

        lines.append(f"| {domain} | {_ret(lg)} | {_ret(ha)} | {_ret(ao)} |")
    lines.append("")

    return "\n".join(lines) + "\n"


def _md_thesis_observations(results: list[dict], frameworks: list[str]) -> str:
    """Generiert automatische Beobachtungen für Thesis Kapitel 6."""
    lines = ["---\n\n## 5. Thesis-Erkenntnisse (auto-generiert)\n",
             "_Diese Beobachtungen basieren auf den gemessenen Werten und können "
             "direkt als Rohmaterial für Kapitel 6 (Evaluation) verwendet werden._\n"]

    observations = []

    successful = [r for r in results if r["success"]]
    if not successful:
        lines.append("_Keine erfolgreichen Runs – keine Beobachtungen möglich._\n")
        return "\n".join(lines)

    for domain in ALL_DOMAINS:
        dom_results = [r for r in successful if r["domain"] == domain]
        if not dom_results:
            continue
        best = max(dom_results, key=lambda r: r["metrics"]["validation_rate"])
        best_rate = best["metrics"]["validation_rate"]
        best_label = FRAMEWORK_LABELS.get(best["framework"], best["framework"])
        tied = [r for r in dom_results if abs(r["metrics"]["validation_rate"] - best_rate) < 0.01]
        if len(tied) == 1:
            observations.append(
                f"**{best_label}** erzielte in der Domain *{domain}* die höchste "
                f"Validation-Rate ({best_rate * 100:.0f}%)."
            )

    for domain in ALL_DOMAINS:
        lc = next((r for r in successful if r["framework"] == "langchain" and r["domain"] == domain), None)
        ao = next((r for r in successful if r["framework"] == "agent_orchestrator" and r["domain"] == domain), None)
        if lc and ao:
            diff_pct = (ao["metrics"]["total_time"] - lc["metrics"]["total_time"]) / max(lc["metrics"]["total_time"], 1) * 100
            if abs(diff_pct) > 10:
                direction = "mehr" if diff_pct > 0 else "weniger"
                observations.append(
                    f"**Agent Orchestrator** benötigte in Domain *{domain}* "
                    f"Ø {abs(diff_pct):.0f}% {direction} Zeit als **LangChain Pipeline** "
                    f"({ao['metrics']['total_time']:.1f}s vs. {lc['metrics']['total_time']:.1f}s)."
                )
            break

    ha_results = [r for r in successful if r["framework"] == "hybrid_agent"]
    h_results  = [r for r in successful if r["framework"] == "hybrid"]
    if ha_results and h_results:
        for domain in ALL_DOMAINS:
            ha = next((r for r in ha_results if r["domain"] == domain), None)
            h  = next((r for r in h_results  if r["domain"] == domain), None)
            if ha and h:
                time_diff = ha["metrics"]["total_time"] - h["metrics"]["total_time"]
                rate_diff = (ha["metrics"]["validation_rate"] - h["metrics"]["validation_rate"]) * 100
                sign_t = "+" if time_diff > 0 else ""
                sign_r = "+" if rate_diff > 0 else ""
                observations.append(
                    f"**Hybrid+Agent vs. Hybrid** ({domain}): "
                    f"Zeit {sign_t}{time_diff:.1f}s, "
                    f"Validation-Rate {sign_r}{rate_diff:.0f}%. "
                    f"Identisches Pre/Postprocessing – Unterschied ausschliesslich Phase 2 "
                    f"(AgentExecutor vs. LangGraph StateGraph)."
                )
                break

    am_results = [r for r in successful if r["framework"] == "agent_multi"]
    lc_results = [r for r in successful if r["framework"] == "langchain"]
    if am_results and lc_results:
        am_rates = [r["metrics"]["validation_rate"] for r in am_results]
        lc_rates = [r["metrics"]["validation_rate"] for r in lc_results]
        if am_rates and lc_rates:
            avg_am = sum(am_rates) / len(am_rates)
            avg_lc = sum(lc_rates) / len(lc_rates)
            diff   = (avg_am - avg_lc) * 100
            if abs(diff) < 5:
                observations.append(
                    f"**Agent Multi-Step** erzielte mit Ø {avg_am * 100:.0f}% Validation-Rate "
                    f"keine signifikant höhere Rate als **LangChain Pipeline** "
                    f"({avg_lc * 100:.0f}%, Differenz: {diff:+.0f}%). "
                    f"Dies unterstützt die These, dass ein Agent mit einem einzigen Tool "
                    f"zur deterministischen Pipeline degeneriert."
                )

    lg_retries = [
        sum(dict(r["metrics"].get("retries_total") or {}).values()
            if isinstance(r["metrics"].get("retries_total"), dict)
            else [r["metrics"].get("retries_total") or 0])
        for r in successful if r["framework"] == "langgraph"
    ]
    ao_retries = [
        r["metrics"].get("retries_total") or 0
        for r in successful if r["framework"] == "agent_orchestrator"
    ]
    if lg_retries and ao_retries:
        avg_lg_ret = sum(lg_retries) / len(lg_retries)
        avg_ao_ret = sum(ao_retries) / len(ao_retries)
        observations.append(
            f"**LangGraph** (Conditional Edges): Ø {avg_lg_ret:.1f} Retries/Run — "
            f"**Agent Orchestrator** (LLM-Scratchpad): Ø {avg_ao_ret:.1f} Retries/Run. "
            f"LangGraph-Retries sind explizit im Graphen definiert; "
            f"Agent-Retries entstehen implizit durch LLM-Entscheidung."
        )

    if not observations:
        observations.append(
            "Keine automatischen Beobachtungen generierbar "
            "(zu wenige erfolgreiche Runs oder unzureichende Datenbasis)."
        )

    for i, obs in enumerate(observations, 1):
        lines.append(f"{i}. {obs}\n")

    return "\n".join(lines)


def _md_quality_flags(results: list[dict]) -> str:
    """Qualitäts-Flags analog zu evaluate_all_domains.py."""
    lines = ["---\n\n## 6. Qualitäts-Auffälligkeiten\n"]
    found = False

    leaks = []
    for r in results:
        for seg in r.get("segments", []):
            for v in seg.get("validated_variants", []):
                text = v.get("text", "")
                if ("Erstelle eine inhaltlich äquivalente" in text or
                        "DEUTLICH anders formulierte Variante" in text):
                    leaks.append(
                        f"- **{FRAMEWORK_LABELS.get(r['framework'], r['framework'])}** / "
                        f"{r['domain']} / V{v['variant_id']}: Prompt-Text im Output erkannt"
                    )
    if leaks:
        found = True
        lines.append("**⚠️ Prompt-Leaks:**")
        lines.extend(leaks)
        lines.append("")

    length_issues = []
    for r in results:
        for si, seg in enumerate(r.get("segments", [])):
            orig_len = len(seg["original_segment"]["text"])
            for v in seg.get("validated_variants", []):
                if orig_len > 0:
                    ratio = len(v.get("text", "")) / orig_len
                    if ratio > 3.0:
                        length_issues.append(
                            f"- **{FRAMEWORK_LABELS.get(r['framework'], r['framework'])}** / "
                            f"{r['domain']} / Seg {si+1} / V{v['variant_id']}: "
                            f"Ratio {ratio:.1f}×"
                        )
    if length_issues:
        found = True
        lines.append("**⚠️ Extreme Längenabweichungen (> 3× Original):**")
        lines.extend(length_issues[:20])
        if len(length_issues) > 20:
            lines.append(f"  … und {len(length_issues) - 20} weitere")
        lines.append("")

    if not found:
        lines.append("_Keine automatisch erkannten Auffälligkeiten._\n")

    return "\n".join(lines)


# ─── JSON-Report ──────────────────────────────────────────────────────────────

def _build_json_report(results: list[dict], ts: str, cfg: dict) -> dict:
    return {
        "timestamp": ts,
        "config": {
            "variants":   cfg["num_variants"],
            "domains":    cfg["domains"],
            "frameworks": cfg["frameworks"],
            "ocr_mode":   "mistral_all_domains",
            "generator":  "evaluate_all_frameworks_mistral_ocr.py",
        },
        "summary": [
            {
                "framework":       r["framework"],
                "domain":          r["domain"],
                "success":         r["success"],
                "validation_rate": r["metrics"]["validation_rate"],
                "valid_variants":  r["metrics"]["valid_variants"],
                "total_variants":  r["metrics"]["total_variants"],
                "total_time_s":    r["metrics"]["total_time"],
                "ocr_tool":        r["metrics"]["ocr_tool"],
                "tool_calls_total": r["metrics"].get("tool_calls_total"),
                "retries_total":    r["metrics"].get("retries_total"),
                "hallucinated_calls": r["metrics"].get("hallucinated_calls"),
            }
            for r in results
        ],
        "results": results,
    }


# ─── Runner-Registry ──────────────────────────────────────────────────────────

_RUNNERS: dict[str, Any] = {
    "langchain":          _run_langchain,
    "langgraph":          _run_langgraph,
    "hybrid":             _run_hybrid,
    "hybrid_agent":       _run_hybrid_agent,
    "agent_orchestrator": _run_agent_orchestrator,
    "agent_multi":        _run_agent_multi,
}


# ─── Hauptprogramm ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Thesis-Evaluation mit Mistral OCR für alle Domains."
    )
    parser.add_argument("--variants",    type=int,  default=1,
                        help="Varianten pro Segment (Standard: 1)")
    parser.add_argument("--frameworks",  nargs="+", default=None,
                        choices=ALL_FRAMEWORKS,
                        help="Frameworks (Standard: alle 6)")
    parser.add_argument("--domains",     nargs="+", default=None,
                        choices=ALL_DOMAINS,
                        help="Domains (Standard: alle 3)")
    parser.add_argument("--fast",        action="store_true",
                        help="Nur math, 1 Variante, ohne Agent-Frameworks (~5–10 Min)")
    parser.add_argument("--agents-only", action="store_true",
                        help="Nur Agent-Frameworks (hybrid_agent, agent_orchestrator, agent_multi)")
    parser.add_argument("--no-agents",   action="store_true",
                        help="Agent-Frameworks ausschliessen")
    parser.add_argument("--output-dir",  type=Path, default=None,
                        help="Output-Verzeichnis (Standard: data/output/comparison_mistral_ocr/)")
    parser.add_argument("--no-markdown", action="store_true",
                        help="Kein Markdown-Report (nur Konsolen-Output + JSON)")
    parser.add_argument("--no-multiprocessing", action="store_true",
                        help="Kein Timeout-Isolation (einfacher, aber kein Timeout möglich)")
    args = parser.parse_args()

    # ── Framework/Domain-Auswahl ──────────────────────────────────────────────
    if args.fast:
        frameworks = ["langchain", "langgraph", "hybrid"]
        domains    = ["math"]
        args.variants = 1
    elif args.agents_only:
        frameworks = ["hybrid_agent", "agent_orchestrator", "agent_multi"]
        domains    = args.domains or ALL_DOMAINS
    else:
        frameworks = args.frameworks or ALL_FRAMEWORKS
        domains    = args.domains    or ALL_DOMAINS

    if args.no_agents:
        frameworks = [fw for fw in frameworks if fw not in IS_AGENT]

    ts      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")

    out_dir: Path = args.output_dir or (
        Config.DATA_OUTPUT_PATH / "comparison_mistral_ocr"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    total_runs = len(frameworks) * sum(len(DOMAIN_CONFIG[d]["pdfs"]) for d in domains)
    has_agents = any(fw in IS_AGENT for fw in frameworks)

    # ── Laufzeit-Warnung ─────────────────────────────────────────────────────
    print("=" * 70)
    print("  FRAMEWORK-VERGLEICH: Alle Prototypen (Mistral OCR für alle Domains)")
    print("=" * 70)
    print(f"  OCR-Modus:   Mistral für alle Domains (OCR_FORCE_MISTRAL=1)")
    print(f"  Frameworks:  {', '.join(FRAMEWORK_LABELS.get(f, f) for f in frameworks)}")
    print(f"  Domains:     {', '.join(domains)}")
    print(f"  Varianten:   {args.variants}/Segment")
    print(f"  Gesamt Runs: {total_runs}")
    print()
    print("  ⏱  Geschätzte Laufzeit:")
    if args.fast:
        print("     ~5–10 Min (--fast: nur math, ohne Agents)")
    elif not has_agents:
        print("     ~15–30 Min (3 Frameworks × Domains, ohne Agents)")
    else:
        all_6 = len(frameworks) == 6 and len(domains) == 3
        print(f"     {'~60–120 Min (6 Frameworks × 3 Domains, inkl. Agents)' if all_6 else '~30–90 Min (mit Agent-Frameworks)'}")
    print(f"  ⏱  Timeout pro Run: {TIMEOUT_SECONDS}s")
    print("=" * 70)

    # ── Runs ──────────────────────────────────────────────────────────────────
    run_num  = 0
    results: list[dict] = []

    for domain in domains:
        cfg_dom = DOMAIN_CONFIG[domain]

        for pdf_rel in cfg_dom["pdfs"]:
            pdf_path = Config.DATA_INPUT_PATH / pdf_rel

            if not pdf_path.exists():
                print(f"\n⚠️  PDF nicht gefunden: {pdf_path} — überspringe '{pdf_rel}'")
                for fw in frameworks:
                    results.append(_error_result(
                        fw, domain, pdf_rel.split("/")[-1],
                        f"PDF not found: {pdf_path}"
                    ))
                continue

            for framework in frameworks:
                run_num += 1
                icon  = EMOJI.get(framework, "")
                label = FRAMEWORK_LABELS.get(framework, framework)
                print(f"\n[{run_num}/{total_runs}] {icon} {label.upper()} — {cfg_dom['label'].upper()}")
                print(f"  PDF: {pdf_path.name}")

                t0 = time.time()
                try:
                    if args.no_multiprocessing:
                        runner = _RUNNERS[framework]
                        result = runner(pdf_path, domain, args.variants)
                    else:
                        result = _run_with_timeout(
                            framework, pdf_path, domain, args.variants,
                            timeout=TIMEOUT_SECONDS,
                        )
                except Exception as exc:
                    print(f"  ❌ Exception: {exc}")
                    result = _error_result(framework, domain, pdf_path.name, str(exc))

                elapsed = time.time() - t0
                results.append(result)

                if result["success"]:
                    m = result["metrics"]
                    tc_str   = f" | Tools: {m['tool_calls_total']}" if m.get("tool_calls_total") is not None else ""
                    ret_str  = f" | Retries: {m['retries_total']}" if m.get("retries_total") is not None else ""
                    print(
                        f"  ✅ {m['valid_variants']}/{m['total_variants']} valide "
                        f"({m['validation_rate'] * 100:.0f}%) | {elapsed:.1f}s | "
                        f"OCR: {m['ocr_tool']}{tc_str}{ret_str}"
                    )
                else:
                    print(f"  ❌ {result.get('error', '?')[:120]}")

    # ── Konsolen-Zusammenfassung ───────────────────────────────────────────────
    for domain in domains:
        domain_results = [r for r in results if r["domain"] == domain]
        _print_domain_table(domain, domain_results)

    _print_overall_summary(results, frameworks)
    _print_failures(results)

    # ── Reports schreiben ─────────────────────────────────────────────────────
    run_cfg = {"num_variants": args.variants, "domains": domains, "frameworks": frameworks}

    # JSON
    json_report = _build_json_report(results, ts, run_cfg)
    json_path   = out_dir / f"results_mistral_ocr_{ts_file}.json"
    json_path.write_text(
        json.dumps(json_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Markdown
    if not args.no_markdown:
        md_parts = [
            f"# Framework-Vergleich: Alle Prototypen (Mistral OCR)\n\n"
            f"**Datum:** {ts}  |  **OCR:** Mistral für alle Domains  |  "
            f"**Varianten/Segment:** {args.variants}  |  "
            f"**Frameworks:** {len(frameworks)}  |  **Domains:** {len(domains)}\n\n"
            f"---\n\n"
        ]
        md_parts.append(_md_summary(results, frameworks))
        md_parts.append(_md_arch_table())
        md_parts.append("\n---\n\n## 3. Ergebnisse pro Domain\n")
        for domain in domains:
            domain_results = [r for r in results if r["domain"] == domain]
            md_parts.append(_md_domain_section(domain, domain_results))
        md_parts.append(_md_agent_analysis(results))
        md_parts.append(_md_thesis_observations(results, frameworks))
        md_parts.append(_md_quality_flags(results))

        md_report = "\n".join(md_parts)
        md_path   = out_dir / "full_comparison_report_mistral_ocr.md"
        md_path.write_text(md_report, encoding="utf-8")
    else:
        md_path = None

    # ── Abschluss ─────────────────────────────────────────────────────────────
    failed_count  = sum(1 for r in results if not r["success"])
    success_count = len(results) - failed_count

    print(f"\n{'═' * 70}")
    print(f"  EVALUATION ABGESCHLOSSEN")
    print(f"  ✅ Erfolgreich: {success_count}/{len(results)}")
    if failed_count:
        print(f"  ❌ Fehlgeschlagen: {failed_count}/{len(results)}")
    print(f"\n  📁 Reports gespeichert in: {out_dir}")
    print(f"     JSON: {json_path.name}")
    if md_path:
        print(f"     MD:   {md_path.name}")
    print(f"\n  💡 Tipp: Das Markdown-File direkt zu Claude hochladen für Kapitel-6-Analyse.")
    print(f"{'═' * 70}\n")


if __name__ == "__main__":
    main()
