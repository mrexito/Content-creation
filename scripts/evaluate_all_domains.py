"""
evaluate_all_domains.py
=======================
Systematische Evaluation: LangChain vs. LangGraph vs. Hybrid
Testet alle drei Frameworks mit allen drei Domains und erzeugt:
  - JSON-Report  (maschinenlesbar, für Archiv)
  - Markdown-Report (für Claude-Upload / manuelle Analyse)

Usage:
    python scripts/evaluate_all_domains.py
    python scripts/evaluate_all_domains.py --variants 2
    python scripts/evaluate_all_domains.py --domains math economics
    python scripts/evaluate_all_domains.py --frameworks langchain langgraph
    python scripts/evaluate_all_domains.py --no-run --input data/output/evaluation/latest/
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.config import Config
from common.llm_handler import reset_llm_handler

# ─── Konfiguration ───────────────────────────────────────────────────────────

DOMAIN_CONFIG: dict[str, dict] = {
    "math": {
        "pdf": "math/equations_simple.pdf",
        "label": "Mathematik",
        "validator": "SymPy",
    },
    "languages": {
        "pdf": "languages/grammar_exercise.pdf",
        "label": "Sprachen",
        "validator": "BERTScore",
    },
    "economics": {
        "pdf": "economics/balance_sheet.pdf",
        "label": "Wirtschaft",
        "validator": "ConsistencyCheck",
    },
}

ALL_FRAMEWORKS = ["langchain", "langgraph", "hybrid"]
ALL_DOMAINS    = ["math", "languages", "economics"]


# ─── Framework-Runner ────────────────────────────────────────────────────────

def _run_langchain(pdf_path: Path, domain: str, num_variants: int) -> dict[str, Any]:
    from langchain_prototype.pipeline import get_pipeline
    reset_llm_handler()
    pipeline = get_pipeline(domain=domain, num_variants=num_variants)
    result   = pipeline.process_pdf(pdf_path)
    return _normalise_langchain(result, domain, pdf_path.name)


def _run_langgraph(pdf_path: Path, domain: str, num_variants: int) -> dict[str, Any]:
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


def _run_hybrid(pdf_path: Path, domain: str, num_variants: int) -> dict[str, Any]:
    from hybrid_prototype.pipeline import get_pipeline as get_hybrid_pipeline
    reset_llm_handler()
    pipeline = get_hybrid_pipeline(domain=domain, num_variants=num_variants)
    result   = pipeline.process_pdf(pdf_path)
    return _normalise_hybrid(result, domain, pdf_path.name)


# ─── Normalisierung → einheitliches Schema ───────────────────────────────────
#
# Einheitliches Schema pro Framework-Run:
# {
#   "success": bool,
#   "framework": str,
#   "domain": str,
#   "pdf_name": str,
#   "error": str | None,
#   "metrics": {
#     "total_time": float,
#     "ocr_time": float,
#     "ocr_tool": str,
#     "num_segments": int,
#     "total_variants": int,
#     "valid_variants": int,
#     "validation_rate": float,
#   },
#   "segments": [
#     {
#       "original_segment": {"text": str, "type": str},
#       "classification":   {"domain": str, "content_type": str, "confidence": float},
#       "validated_variants": [
#         {
#           "variant_id": int,
#           "text": str,
#           "is_valid": bool,
#           "validation_issues": [str],
#         }
#       ],
#       "validation_statistics": {"total": int, "valid": int},
#     }
#   ]
# }


def _seg_from_assembled(seg: dict) -> dict:
    """Konvertiert AssemblyChain-Segment ins einheitliche Schema."""
    variants = []
    for v in seg.get("variants", []):
        variants.append({
            "variant_id": v.get("variant_id", 0),
            "text": v.get("text", ""),
            "is_valid": True,  # assembled → bereits gefiltert auf valid
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


def _normalise_langchain(result: dict, domain: str, pdf_name: str) -> dict:
    if not result.get("success"):
        return _error_result("langchain", domain, pdf_name, result.get("error", "unknown"))

    stats    = result.get("statistics", {})
    assembly = stats.get("assembly", {})
    parsing  = stats.get("parsing", {})

    # Segmente aus assembled_document
    segments = []
    doc = result.get("assembled_document", {})
    for seg in doc.get("segments", []):
        segments.append(_seg_from_assembled(seg))

    total_v = assembly.get("total_variants", 0)
    valid_v = assembly.get("valid_variants", 0)

    return {
        "success": True,
        "framework": "langchain",
        "domain": domain,
        "pdf_name": pdf_name,
        "error": None,
        "metrics": {
            "total_time":      round(stats.get("total_time", 0), 2),
            "ocr_time":        round(parsing.get("processing_time", 0), 2),
            "ocr_tool":        parsing.get("tool_used", "?"),
            "num_segments":    stats.get("segmentation", {}).get("num_segments", len(segments)),
            "total_variants":  total_v,
            "valid_variants":  valid_v,
            "validation_rate": round(valid_v / total_v, 4) if total_v else 0.0,
        },
        "segments": segments,
    }


def _normalise_langgraph(final: dict, elapsed: float, domain: str, pdf_name: str) -> dict:
    if final.get("errors"):
        return _error_result("langgraph", domain, pdf_name, str(final["errors"]))

    swv          = final.get("segments_with_variants") or []
    doc          = final.get("assembled_document") or {}
    segments_raw = doc.get("segments", []) if isinstance(doc, dict) else []

    # Leere Pipeline-Ausgabe abfangen (z.B. OCR-Fehler ohne Exception)
    if not swv and not segments_raw:
        phase = final.get("current_phase", "unknown")
        errs  = final.get("errors") or []
        msg   = f"Keine Segmente produziert (Phase: {phase})"
        if errs:
            msg += f" – {'; '.join(str(e) for e in errs)}"
        return _error_result("langgraph", domain, pdf_name, msg)

    # LangGraph liefert Segmente über segments_with_variants im State
    if swv:
        segments = _normalise_segments_with_variants(swv)
    else:
        segments = [_seg_from_assembled(s) for s in segments_raw]

    total_v = sum(s["validation_statistics"]["total"] for s in segments)
    valid_v = sum(s["validation_statistics"]["valid"] for s in segments)

    ocr_meta = final.get("ocr_metadata", {}) or {}

    return {
        "success": True,
        "framework": "langgraph",
        "domain": domain,
        "pdf_name": pdf_name,
        "error": None,
        "metrics": {
            "total_time":      round(elapsed, 2),
            "ocr_time":        round(ocr_meta.get("processing_time", 0), 2),
            "ocr_tool":        ocr_meta.get("tool_used", "?"),
            "num_segments":    len(segments),
            "total_variants":  total_v,
            "valid_variants":  valid_v,
            "validation_rate": round(valid_v / total_v, 4) if total_v else 0.0,
        },
        "segments": segments,
    }


def _normalise_hybrid(result: dict, domain: str, pdf_name: str) -> dict:
    """
    Normalisiert HybridPipeline.process_pdf()-Ergebnis auf einheitliches Schema.
    HybridPipeline gibt zurück: {"success", "statistics": {...}, "assembled_document": {...}}
    """
    if not result.get("success"):
        return _error_result("hybrid", domain, pdf_name, result.get("error", "unknown"))

    stats       = result.get("statistics", {})          # FIX: war "metrics"
    preproc     = stats.get("preprocessing", {})
    graph_stats = stats.get("graph", {})

    doc          = result.get("assembled_document") or {}
    segments_raw = doc.get("segments", [])              # FIX: war result.get("segments", [])
    segments     = [_seg_from_assembled(s) for s in segments_raw]

    total_valid   = graph_stats.get("total_valid", 0)
    total_invalid = graph_stats.get("total_invalid", 0)
    total_v = total_valid + total_invalid
    valid_v = total_valid

    return {
        "success": True,
        "framework": "hybrid",
        "domain": domain,
        "pdf_name": pdf_name,
        "error": None,
        "metrics": {
            "total_time":      round(stats.get("total_time", 0), 2),
            "ocr_time":        round(preproc.get("ocr_time", 0), 2),
            "ocr_tool":        preproc.get("ocr_tool", "?"),
            "num_segments":    preproc.get("segments", len(segments)),
            "total_variants":  total_v,
            "valid_variants":  valid_v,
            "validation_rate": round(valid_v / total_v, 4) if total_v else 0.0,
        },
        "segments": segments,
    }


def _normalise_segments_with_variants(swv: list) -> list:
    """Für LangGraph segments_with_variants aus dem State."""
    result = []
    for seg in swv:
        orig = seg.get("segment", {})          # LangGraph state key (not "original_segment")
        raw_variants = seg.get("variants", []) # LangGraph state key (not "validated_variants")
        variants = []
        for v in raw_variants:
            val = v.get("validation", {}) if isinstance(v.get("validation"), dict) else {}
            is_valid = val.get("is_valid", False)      # nested under "validation"
            issues   = val.get("issues", [])            # nested under "validation"
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
            "classification":   seg.get("classification", {}),
            "validated_variants": variants,
            "validation_statistics": {"total": len(variants), "valid": valid_count},
        })
    return result


def _normalise_segments_frontend(segments: list) -> list:
    """Für Hybrid (und als Fallback für LangGraph) — Frontend-JSON-Format."""
    result = []
    for seg in segments:
        orig = seg.get("original_segment", {})
        raw_variants = seg.get("validated_variants", [])
        variants = []
        for v in raw_variants:
            variants.append({
                "variant_id":        v.get("variant_id", 0),
                "text":              v.get("text", ""),
                "is_valid":          v.get("is_valid", False),
                "validation_issues": v.get("validation_issues", []),
            })
        stats = seg.get("validation_statistics", {})
        valid_count = stats.get("valid", sum(1 for v in variants if v["is_valid"]))
        result.append({
            "original_segment": {
                "text": orig.get("text", "") if isinstance(orig, dict) else str(orig),
                "type": orig.get("type", "unknown") if isinstance(orig, dict) else "unknown",
            },
            "classification":   seg.get("classification", {}),
            "validated_variants": variants,
            "validation_statistics": {"total": len(variants), "valid": valid_count},
        })
    return result


def _error_result(framework: str, domain: str, pdf_name: str, error: str) -> dict:
    return {
        "success":   False,
        "framework": framework,
        "domain":    domain,
        "pdf_name":  pdf_name,
        "error":     error,
        "metrics": {
            "total_time": 0, "ocr_time": 0, "ocr_tool": "?",
            "num_segments": 0, "total_variants": 0,
            "valid_variants": 0, "validation_rate": 0.0,
        },
        "segments": [],
    }


# ─── Markdown-Generator ──────────────────────────────────────────────────────

EMOJI = {"langchain": "🔗", "langgraph": "🕸️", "hybrid": "🔀"}
STATUS = {True: "✅", False: "❌"}


def _md_header(ts: str, frameworks: list[str], domains: list[str], num_variants: int) -> str:
    fw_str = " | ".join(f.capitalize() for f in frameworks)
    dom_str = ", ".join(d.capitalize() for d in domains)
    return f"""# Framework-Evaluation: {fw_str}
**Generiert:** {ts}
**Domänen:** {dom_str}
**Varianten pro Segment:** {num_variants}

---

"""


def _md_summary_table(results: list[dict]) -> str:
    lines = ["## Zusammenfassung\n"]
    lines.append("| Framework | Domäne | Segmente | Valide / Total | Rate | Zeit (s) | OCR |")
    lines.append("|-----------|--------|----------|----------------|------|----------|-----|")

    for r in results:
        m  = r["metrics"]
        fw = r["framework"]
        ok = STATUS[r["success"]]
        if r["success"]:
            rate_str = f"{m['validation_rate']*100:.0f}%"
            row = (f"| {EMOJI.get(fw,'')} {fw.capitalize()} "
                   f"| {r['domain'].capitalize()} "
                   f"| {m['num_segments']} "
                   f"| {m['valid_variants']} / {m['total_variants']} "
                   f"| {rate_str} "
                   f"| {m['total_time']:.1f} "
                   f"| {m['ocr_tool']} |")
        else:
            row = (f"| {ok} {fw.capitalize()} "
                   f"| {r['domain'].capitalize()} "
                   f"| – | – | – | – | – |")
        lines.append(row)

    lines.append("")
    return "\n".join(lines) + "\n"


def _md_domain_section(domain: str, domain_results: list[dict]) -> str:
    cfg   = DOMAIN_CONFIG[domain]
    lines = [f"---\n\n## Domäne: {cfg['label']} (`{domain}`)\n",
             f"**PDF:** `{cfg['pdf']}` | **Validator:** {cfg['validator']}\n"]

    # Kurze Metrik-Tabelle pro Framework
    lines.append("\n### Metriken\n")
    lines.append("| Framework | Segmente | Valide / Total | Rate | Zeit (s) | OCR |")
    lines.append("|-----------|----------|----------------|------|----------|-----|")
    for r in domain_results:
        m  = r["metrics"]
        fw = r["framework"]
        if r["success"]:
            lines.append(
                f"| {EMOJI.get(fw,'')} {fw.capitalize()} "
                f"| {m['num_segments']} "
                f"| {m['valid_variants']} / {m['total_variants']} "
                f"| {m['validation_rate']*100:.0f}% "
                f"| {m['total_time']:.1f} "
                f"| {m['ocr_tool']} |"
            )
        else:
            lines.append(f"| ❌ {fw.capitalize()} | – | – | – | – | – |")
    lines.append("")

    # Segment-für-Segment Volltext-Vergleich
    lines.append("\n### Segment-Vergleich (Volltext)\n")

    # Ermittle max Segmentanzahl über alle Frameworks
    max_segs = max((len(r["segments"]) for r in domain_results if r["success"]), default=0)

    for seg_idx in range(max_segs):
        # Hole Original aus erstem erfolgreichem Framework
        original_text = ""
        original_type = ""
        for r in domain_results:
            if r["success"] and seg_idx < len(r["segments"]):
                original_text = r["segments"][seg_idx]["original_segment"]["text"]
                original_type = r["segments"][seg_idx]["original_segment"].get("type", "?")
                break

        preview = original_text[:80].replace("\n", " ")
        if len(original_text) > 80:
            preview += "…"

        lines.append(f"#### Segment {seg_idx + 1} — `{original_type}` — _{preview}_\n")

        # Original
        lines.append("**Original:**")
        lines.append("```")
        lines.append(original_text)
        lines.append("```\n")

        # Pro Framework: alle Varianten
        for r in domain_results:
            fw = r["framework"]
            icon = EMOJI.get(fw, "")
            if not r["success"]:
                lines.append(f"**{icon} {fw.capitalize()}:** ❌ Pipeline fehlgeschlagen — `{r.get('error','?')}`\n")
                continue

            if seg_idx >= len(r["segments"]):
                lines.append(f"**{icon} {fw.capitalize()}:** _(kein Segment #{seg_idx+1})_\n")
                continue

            seg = r["segments"][seg_idx]
            cls = seg.get("classification", {})
            cls_str = f"{cls.get('domain','?')} / {cls.get('content_type','?')}"
            stats   = seg["validation_statistics"]

            lines.append(f"**{icon} {fw.capitalize()}** — Klassifiziert als `{cls_str}` — {stats['valid']}/{stats['total']} valide\n")

            variants = seg["validated_variants"]
            if not variants:
                lines.append("_Keine Varianten generiert (Segment übersprungen)_\n")
            else:
                for v in variants:
                    ok_str   = "✅ VALIDE" if v["is_valid"] else "❌ INVALID"
                    issues   = v.get("validation_issues", [])
                    issue_md = ""
                    if issues:
                        issue_md = "\n> **Issues:** " + " | ".join(str(i) for i in issues)

                    lines.append(f"<details>")
                    lines.append(f"<summary>Variante {v['variant_id']} — {ok_str}</summary>\n")
                    lines.append("```")
                    lines.append(v["text"] if v["text"] else "(leer)")
                    lines.append("```")
                    if issue_md:
                        lines.append(issue_md)
                    lines.append("</details>\n")

            lines.append("")

    return "\n".join(lines)


def _md_findings_section(results: list[dict]) -> str:
    lines = ["---\n\n## Beobachtungen & offene Fragen\n",
             "_Dieser Abschnitt ist für manuelle Ergänzung nach Claude-Upload vorgesehen._\n",
             "### Automatisch erkannte Auffälligkeiten\n"]

    # Prompt-Leaks
    leaks = []
    for r in results:
        for seg in r.get("segments", []):
            for v in seg.get("validated_variants", []):
                text = v.get("text", "")
                if "Erstelle eine inhaltlich äquivalente" in text or \
                   "DEUTLICH anders formulierte Variante" in text:
                    leaks.append(
                        f"- **{r['framework'].capitalize()}** / {r['domain']} / "
                        f"Variante {v['variant_id']}: Prompt-Text im Output erkannt"
                    )
    if leaks:
        lines.append("**⚠️ Prompt-Leaks:**")
        lines.extend(leaks)
        lines.append("")

    # Falsch-positive: Variante ist "valid" aber enthält LaTeX-Preamble
    latex_issues = []
    for r in results:
        for seg in r.get("segments", []):
            for v in seg.get("validated_variants", []):
                if v.get("is_valid") and "\\documentclass" in v.get("text", ""):
                    latex_issues.append(
                        f"- **{r['framework'].capitalize()}** / {r['domain']} / "
                        f"Variante {v['variant_id']}: LaTeX-Preamble im validierten Output"
                    )
    if latex_issues:
        lines.append("**⚠️ LaTeX-Preamble in validen Varianten (Falsch-Positive):**")
        lines.extend(latex_issues)
        lines.append("")

    # Extrem lange Varianten (Ratio > 3×)
    length_issues = []
    for r in results:
        for seg_idx, seg in enumerate(r.get("segments", [])):
            orig_len = len(seg["original_segment"]["text"])
            for v in seg.get("validated_variants", []):
                if orig_len > 0:
                    ratio = len(v.get("text", "")) / orig_len
                    if ratio > 3.0:
                        length_issues.append(
                            f"- **{r['framework'].capitalize()}** / {r['domain']} / "
                            f"Seg {seg_idx+1} / V{v['variant_id']}: "
                            f"Ratio {ratio:.1f}× (Original: {orig_len} Zeichen)"
                        )
    if length_issues:
        lines.append("**⚠️ Extreme Längenabweichungen (> 3× Original):**")
        lines.extend(length_issues[:20])  # max 20 Einträge
        if len(length_issues) > 20:
            lines.append(f"  … und {len(length_issues)-20} weitere")
        lines.append("")

    if not leaks and not latex_issues and not length_issues:
        lines.append("_Keine automatisch erkannten Auffälligkeiten._\n")

    lines.append("\n### Fragen für Claude-Analyse\n")
    lines.append("1. Welche Fehlertypen dominieren pro Domäne?\n"
                 "2. Wo bestehen Prompt-Lücken (fehlende Constraints)?\n"
                 "3. Welches Framework zeigt die konsistenteste Ausgabequalität?\n"
                 "4. Welche kurzen Segmente (< 80 Zeichen) werden systematisch überdehnt?\n"
                 "5. Gibt es Klassifikationsfehler (z.B. Economics als Mathematics)?\n")

    return "\n".join(lines)


# ─── JSON-Report ─────────────────────────────────────────────────────────────

def _build_json_report(results: list[dict], ts: str, cfg: dict) -> dict:
    return {
        "meta": {
            "timestamp":    ts,
            "frameworks":   cfg["frameworks"],
            "domains":      cfg["domains"],
            "num_variants": cfg["num_variants"],
            "generator":    "evaluate_all_domains.py",
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
            }
            for r in results
        ],
        "results": results,
    }


# ─── Hauptprogramm ───────────────────────────────────────────────────────────

RUNNERS = {
    "langchain": _run_langchain,
    "langgraph": _run_langgraph,
    "hybrid":    _run_hybrid,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluiert alle drei Frameworks über alle drei Domänen."
    )
    parser.add_argument("--variants",    type=int,  default=2,
                        help="Anzahl Varianten pro Segment (Standard: 2)")
    parser.add_argument("--frameworks",  nargs="+", default=ALL_FRAMEWORKS,
                        choices=ALL_FRAMEWORKS,
                        help="Frameworks die getestet werden sollen")
    parser.add_argument("--domains",     nargs="+", default=ALL_DOMAINS,
                        choices=ALL_DOMAINS,
                        help="Domains die getestet werden sollen")
    parser.add_argument("--output-dir",  type=Path,
                        default=None,
                        help="Output-Verzeichnis (Standard: data/output/evaluation/<timestamp>/)")
    args = parser.parse_args()

    ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")

    out_dir: Path = args.output_dir or (
        Config.DATA_OUTPUT_PATH / "evaluation" / ts_file
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    total_runs = len(args.frameworks) * len(args.domains)
    run_num    = 0
    results: list[dict] = []

    print("=" * 70)
    print(f"  MULTI-DOMAIN EVALUATION — {len(args.frameworks)} Frameworks × {len(args.domains)} Domains")
    print(f"  Gesamt: {total_runs} Runs | Varianten/Segment: {args.variants}")
    print("=" * 70)

    for domain in args.domains:
        cfg_dom = DOMAIN_CONFIG[domain]
        pdf_path = Config.DATA_INPUT_PATH / cfg_dom["pdf"]

        if not pdf_path.exists():
            print(f"\n⚠️  PDF nicht gefunden: {pdf_path} — überspringe Domain '{domain}'")
            for fw in args.frameworks:
                results.append(_error_result(fw, domain, cfg_dom["pdf"].split("/")[-1],
                                             f"PDF not found: {pdf_path}"))
            continue

        for framework in args.frameworks:
            run_num += 1
            icon = EMOJI.get(framework, "")
            print(f"\n[{run_num}/{total_runs}] {icon} {framework.upper()} — {cfg_dom['label'].upper()}")
            print(f"  PDF: {pdf_path.name}")

            runner = RUNNERS[framework]
            try:
                result = runner(pdf_path, domain, args.variants)
            except Exception as exc:
                print(f"  ❌ Exception: {exc}")
                result = _error_result(framework, domain, pdf_path.name, str(exc))

            results.append(result)

            if result["success"]:
                m = result["metrics"]
                print(f"  ✅ {m['valid_variants']}/{m['total_variants']} valide "
                      f"({m['validation_rate']*100:.0f}%) | {m['total_time']:.1f}s | "
                      f"OCR: {m['ocr_tool']}")
            else:
                print(f"  ❌ Fehler: {result.get('error','?')}")

    # ── Reports schreiben ────────────────────────────────────────────────────
    run_cfg = {
        "frameworks":   args.frameworks,
        "domains":      args.domains,
        "num_variants": args.variants,
    }

    # JSON
    json_report = _build_json_report(results, ts, run_cfg)
    json_path   = out_dir / f"evaluation_{ts_file}.json"
    json_path.write_text(
        json.dumps(json_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Markdown
    md_parts = [_md_header(ts, args.frameworks, args.domains, args.variants)]
    md_parts.append(_md_summary_table(results))

    for domain in args.domains:
        domain_results = [r for r in results if r["domain"] == domain]
        md_parts.append(_md_domain_section(domain, domain_results))

    md_parts.append(_md_findings_section(results))

    md_report = "\n".join(md_parts)
    md_path   = out_dir / f"evaluation_{ts_file}.md"
    md_path.write_text(md_report, encoding="utf-8")

    # ── Abschluss-Übersicht ──────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  ZUSAMMENFASSUNG")
    print("=" * 70)
    header = f"  {'Framework':<12} {'Domain':<12} {'Rate':>6}  {'Valide/Total':>12}  {'Zeit (s)':>8}"
    print(header)
    print("  " + "-" * 54)
    for r in results:
        m = r["metrics"]
        ok = "✅" if r["success"] else "❌"
        if r["success"]:
            print(f"  {ok} {r['framework']:<10} {r['domain']:<12} "
                  f"{m['validation_rate']*100:>5.0f}%  "
                  f"{m['valid_variants']:>5}/{m['total_variants']:<6}  "
                  f"{m['total_time']:>8.1f}")
        else:
            print(f"  {ok} {r['framework']:<10} {r['domain']:<12}  FEHLER")

    print("\n  📁 Reports gespeichert:")
    print(f"     JSON: {json_path}")
    print(f"     MD:   {md_path}")
    print("\n  💡 Tipp: Das Markdown-File direkt zu Claude hochladen für Analyse.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()