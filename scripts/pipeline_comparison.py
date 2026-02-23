"""
Pipeline Comparison – 4 Kombinationen für automatisiertes Content-Rewriting

Testmatrix:
  1. Mistral OCR  + BFH Modell
  2. Mistral OCR  + GPT-4
  3. Tesseract OCR + BFH Modell
  4. Tesseract OCR + GPT-4

Phasen pro Kombination:
  Phase 1 – OCR / Parsing
  Phase 2 – Rewriting mit Retry-Loop (max. 3 Versuche)
  Phase 3 – Evaluierung

Usage:
    python scripts/pipeline_comparison.py                          # auto PDF
    python scripts/pipeline_comparison.py data/input/math/x.pdf
    python scripts/pipeline_comparison.py data/input/math/x.pdf --combos 1,3
"""

import sys
import time
import json
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple

# ── Pfad-Setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.config import Config
from common.ocr_handler import OCRHandler
from common.llm_handler import LLMHandler, get_llm_handler, reset_llm_handler
from langchain_prototype.chains.segmentation_chain import get_segmentation_chain
from langchain_prototype.chains.classification_chain import get_classification_chain
from langchain_prototype.chains.rewriting_chain import RewritingChain
from langchain_prototype.chains.validation_chain import ValidationChain

# ── Konfiguration ─────────────────────────────────────────────────────────────
COMBINATIONS: List[Dict[str, Any]] = [
    {'id': 1, 'label': 'Mistral OCR  + BFH',     'ocr': 'mistral',   'llm': 'bfh'},
    {'id': 2, 'label': 'Mistral OCR  + GPT-4',   'ocr': 'mistral',   'llm': 'openai'},
    {'id': 3, 'label': 'Tesseract    + BFH',      'ocr': 'tesseract', 'llm': 'bfh'},
    {'id': 4, 'label': 'Tesseract    + GPT-4',    'ocr': 'tesseract', 'llm': 'openai'},
]

MAX_RETRY_ATTEMPTS   = 3   # High-level Retries pro Segment (Phase 2)
NUM_VARIANTS         = 2   # Varianten pro Segment
MAX_SEGMENTS         = 3   # Maximale Segmente pro Kombination (für Laufzeit)
NUMBER_CHANGE_TARGET = 0.30  # ≥30 % Zahlenänderung gefordert


# ── Datenklassen ──────────────────────────────────────────────────────────────
@dataclass
class OCRResult:
    success: bool
    tool: str
    processing_time: float
    pages: int = 0
    char_count: int = 0
    word_count: int = 0
    text: str = ''
    error: str = ''


@dataclass
class VariantResult:
    variant_id: int
    text: str
    llm_attempts: int        # Versuche innerhalb RewritingChain (low-level)
    is_valid: bool = False
    validation_issues: List[str] = field(default_factory=list)
    numbers_changed_pct: float = 0.0
    diversity_score: float = 0.0


@dataclass
class SegmentResult:
    segment_index: int
    original_text: str
    domain: str
    rewriting_success: bool
    rewriting_time: float
    high_level_retries: int   # Retry-Loop Versuche (Phase 2)
    variants: List[VariantResult] = field(default_factory=list)
    rewriting_error: str = ''


@dataclass
class CombinationResult:
    id: int
    label: str
    ocr_tool: str
    llm_provider: str
    total_time: float = 0.0
    ocr: Optional[OCRResult] = None
    segments_processed: int = 0
    segment_results: List[SegmentResult] = field(default_factory=list)
    # Aggregierte Metriken (werden in Phase 3 befüllt)
    total_variants: int = 0
    valid_variants: int = 0
    validation_rate: float = 0.0
    avg_diversity_score: float = 0.0
    avg_numbers_changed_pct: float = 0.0
    avg_high_level_retries: float = 0.0
    meets_30pct_criterion: bool = False
    overall_success: bool = False
    error: str = ''


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────
def _extract_numbers(text: str) -> List[float]:
    """Extrahiert alle Zahlen aus Text (auch Dezimalzahlen mit Komma/Punkt)."""
    matches = re.findall(r'\b\d+(?:[.,]\d+)?\b', text)
    results = []
    for m in matches:
        try:
            results.append(float(m.replace(',', '.')))
        except ValueError:
            pass
    return results


def _numbers_changed_pct(original: str, variant: str) -> float:
    """
    Anteil der Zahlen, die sich um ≥30 % verändert haben (0.0–1.0).
    Basis: positionsweiser Vergleich bis min(len_orig, len_var).
    """
    orig_nums = _extract_numbers(original)
    var_nums  = _extract_numbers(variant)
    count     = min(len(orig_nums), len(var_nums))
    if count == 0:
        return 0.0
    changed = 0
    for o, v in zip(orig_nums[:count], var_nums[:count]):
        if o != 0.0:
            if abs(v - o) / abs(o) >= NUMBER_CHANGE_TARGET:
                changed += 1
        elif v != 0.0:
            changed += 1   # 0 → Nicht-0 gilt als ≥100 % Änderung
    return changed / count


def _sep(char: str = '─', width: int = 72) -> str:
    return char * width


def _setup_llm_provider(provider: str) -> None:
    """
    Setzt den LLM-Provider-Singleton zurück und initialisiert ihn neu.
    Alle nachfolgend erstellten Chain-Instanzen nutzen diesen Provider.
    """
    reset_llm_handler()
    get_llm_handler(provider=provider)


# ── Phase 1: OCR ──────────────────────────────────────────────────────────────
def phase1_ocr(pdf_path: Path, ocr_tool: str) -> OCRResult:
    """
    Phase 1 – Liest das PDF mit dem gewählten OCR-Tool ein.

    Args:
        pdf_path: Pfad zur PDF-Datei.
        ocr_tool: 'mistral' oder 'tesseract'.

    Returns:
        OCRResult mit Text und Metriken.
    """
    print(f"  [Phase 1] OCR  ({ocr_tool.upper()}) ...", end='', flush=True)
    handler = OCRHandler(default_tool=ocr_tool)
    result  = handler.pdf_to_text(pdf_path, force_tool=ocr_tool)

    if result['success']:
        text = result.get('text') or ''
        ocr  = OCRResult(
            success          = True,
            tool             = result.get('tool_used', ocr_tool),
            processing_time  = result.get('processing_time', 0.0),
            pages            = result.get('pages', 0),
            char_count       = len(text),
            word_count       = len(text.split()),
            text             = text,
        )
        print(f"  {ocr.char_count:,} Zeichen | {ocr.pages} Seite(n) | {ocr.processing_time:.2f}s")
    else:
        err = result.get('error', 'Unbekannter OCR-Fehler')
        ocr = OCRResult(
            success         = False,
            tool            = ocr_tool,
            processing_time = result.get('processing_time', 0.0),
            error           = err,
        )
        print(f"  FEHLER: {err}")

    return ocr


# ── Phase 2: Rewriting mit Retry-Loop ─────────────────────────────────────────
def phase2_rewrite(
    text: str,
    llm_provider: str,
) -> Tuple[List[SegmentResult], float]:
    """
    Phase 2 – Segmentierung → Klassifizierung → Rewriting mit Retry-Loop.

    Für jedes Segment werden bis zu MAX_RETRY_ATTEMPTS Versuche unternommen,
    eine erfolgreiche Rewriting-Ausgabe zu erzeugen.

    Returns:
        (segment_results, gesamt_rewriting_zeit_in_sekunden)
    """
    print(f"  [Phase 2] Rewriting ({llm_provider.upper()}) ...")

    phase_start = time.time()

    # ── Segmentierung ──────────────────────────────────────────────────────────
    seg_chain = get_segmentation_chain()
    try:
        seg_result = seg_chain.invoke({'text': text})
        if not seg_result['success']:
            raise ValueError("Segmentierung gescheitert")
        segments = seg_result['segments'][:MAX_SEGMENTS]
    except Exception as e:
        print(f"    FEHLER Segmentierung: {e}")
        # Fallback: gesamter Text als ein Segment
        segments = [{'type': 'general', 'text': text[:3000]}]

    print(f"    {len(segments)} Segment(e) erkannt (max. {MAX_SEGMENTS})")

    # ── Klassifizierung + Rewriting pro Segment ────────────────────────────────
    cls_chain      = get_classification_chain()
    rewriting_chain = RewritingChain(
        num_variants             = NUM_VARIANTS,
        max_attempts_per_variant = MAX_RETRY_ATTEMPTS,   # low-level (pro Variante)
    )

    segment_results: List[SegmentResult] = []

    for idx, segment in enumerate(segments):
        seg_text = segment.get('text', '')
        print(f"    Segment {idx + 1}/{len(segments)}", end='', flush=True)

        # Klassifizierung
        try:
            cls_out = cls_chain.invoke({'segment': segment})
            domain  = (
                cls_out['classification'].get('domain', 'general')
                if cls_out.get('success') else 'general'
            )
        except Exception:
            domain = 'general'

        # ── Retry-Loop (Phase-2-Ebene) ─────────────────────────────────────────
        seg_start         = time.time()
        rewriting_success = False
        rewriting_error   = ''
        rewrite_out       = None
        high_level_retries = 0

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            high_level_retries = attempt
            try:
                rewrite_out = rewriting_chain.rewrite_segment(segment, domain)
                if rewrite_out['success']:
                    rewriting_success = True
                    break
                else:
                    rewriting_error = f"Kein Erfolg nach {attempt}. Versuch"
                    print(f" [Retry {attempt}]", end='', flush=True)
            except Exception as exc:
                rewriting_error = str(exc)
                print(f" [Err {attempt}]", end='', flush=True)

        seg_time = time.time() - seg_start
        print(f"  domain={domain} | {seg_time:.1f}s | retries={high_level_retries}")

        seg_obj = SegmentResult(
            segment_index      = idx,
            original_text      = seg_text,
            domain             = domain,
            rewriting_success  = rewriting_success,
            rewriting_time     = seg_time,
            high_level_retries = high_level_retries,
            rewriting_error    = rewriting_error,
        )

        if rewriting_success and rewrite_out:
            div_score = rewrite_out['metadata'].get('diversity_score') or 0.0
            for var in rewrite_out.get('variants', []):
                if not var.get('text'):
                    continue
                num_pct = _numbers_changed_pct(seg_text, var['text'])
                seg_obj.variants.append(VariantResult(
                    variant_id      = var['variant_id'],
                    text            = var['text'],
                    llm_attempts    = var.get('attempts', 1),
                    numbers_changed_pct = num_pct,
                    diversity_score = div_score,
                ))

        segment_results.append(seg_obj)

    total_time = time.time() - phase_start
    return segment_results, total_time


# ── Phase 3: Evaluierung ──────────────────────────────────────────────────────
def phase3_evaluate(segment_results: List[SegmentResult]) -> Dict[str, Any]:
    """
    Phase 3 – Validiert alle Varianten mit domain-spezifischen Validatoren.

    Metriken:
    - Validierungsrate (valid / total)
    - Ø Diversity-Score
    - Anteil Varianten mit ≥30 % Zahlenänderung

    Side-effect: Aktualisiert `is_valid` und `validation_issues` in den
    VariantResult-Objekten.
    """
    print(f"  [Phase 3] Evaluierung ...", end='', flush=True)

    val_chain      = ValidationChain()
    total_vars     = 0
    valid_vars     = 0
    diversity_vals: List[float] = []
    num_change_vals: List[float] = []
    all_issues: List[str]       = []

    for seg in segment_results:
        if not seg.rewriting_success or not seg.variants:
            continue

        variant_dicts = [
            {'variant_id': v.variant_id, 'text': v.text}
            for v in seg.variants
        ]

        try:
            val_result = val_chain.validate_variants(
                original = seg.original_text,
                variants = variant_dicts,
                domain   = seg.domain,
            )
            validated_list = val_result.get('validated_variants', [])

            for i, vd in enumerate(validated_list):
                total_vars += 1
                is_valid    = vd.get('validation', {}).get('is_valid', False)
                issues      = vd.get('validation', {}).get('issues', [])
                if is_valid:
                    valid_vars += 1
                else:
                    all_issues.extend(issues)

                # Update VariantResult in-place
                if i < len(seg.variants):
                    seg.variants[i].is_valid          = is_valid
                    seg.variants[i].validation_issues = issues

        except Exception as exc:
            # Validierung fehlgeschlagen – zähle trotzdem die Varianten
            for v in seg.variants:
                total_vars += 1
                v.validation_issues = [f"Validierungsfehler: {exc}"]

        # Metriken sammeln
        for v in seg.variants:
            if v.diversity_score > 0:
                diversity_vals.append(v.diversity_score)
            num_change_vals.append(v.numbers_changed_pct)

    avg_div     = sum(diversity_vals) / len(diversity_vals) if diversity_vals else 0.0
    avg_num_chg = sum(num_change_vals) / len(num_change_vals) if num_change_vals else 0.0
    val_rate    = valid_vars / total_vars if total_vars > 0 else 0.0

    print(f"  {valid_vars}/{total_vars} valide | Diversity={avg_div:.3f} | "
          f"Zahlenänderung={avg_num_chg*100:.0f}%")

    return {
        'total_variants'          : total_vars,
        'valid_variants'          : valid_vars,
        'validation_rate'         : val_rate,
        'avg_diversity_score'     : avg_div,
        'avg_numbers_changed_pct' : avg_num_chg,
        'sample_issues'           : all_issues[:8],
    }


# ── Gesamte Kombination durchführen ──────────────────────────────────────────
def run_combination(combo: Dict[str, Any], pdf_path: Path) -> CombinationResult:
    """Führt eine vollständige Pipeline-Kombination durch."""
    result = CombinationResult(
        id           = combo['id'],
        label        = combo['label'],
        ocr_tool     = combo['ocr'],
        llm_provider = combo['llm'],
    )

    print(f"\n{_sep('═')}")
    print(f"  Kombination {combo['id']}: {combo['label']}")
    print(_sep('─'))

    total_start = time.time()

    # LLM-Provider initialisieren
    try:
        _setup_llm_provider(combo['llm'])
    except Exception as exc:
        result.error        = f"LLM-Initialisierung fehlgeschlagen: {exc}"
        result.total_time   = time.time() - total_start
        print(f"  FEHLER: {result.error}")
        return result

    # ── Phase 1 ───────────────────────────────────────────────────────────────
    ocr_result  = phase1_ocr(pdf_path, combo['ocr'])
    result.ocr  = ocr_result

    if not ocr_result.success:
        result.error      = f"OCR fehlgeschlagen: {ocr_result.error}"
        result.total_time = time.time() - total_start
        return result

    # ── Phase 2 ───────────────────────────────────────────────────────────────
    seg_results, _rewrite_time = phase2_rewrite(
        text         = ocr_result.text,
        llm_provider = combo['llm'],
    )
    result.segment_results  = seg_results
    result.segments_processed = len(seg_results)

    if not seg_results:
        result.error      = "Keine Segmente verarbeitet"
        result.total_time = time.time() - total_start
        return result

    # ── Phase 3 ───────────────────────────────────────────────────────────────
    eval_metrics = phase3_evaluate(seg_results)

    result.total_variants          = eval_metrics['total_variants']
    result.valid_variants          = eval_metrics['valid_variants']
    result.validation_rate         = eval_metrics['validation_rate']
    result.avg_diversity_score     = eval_metrics['avg_diversity_score']
    result.avg_numbers_changed_pct = eval_metrics['avg_numbers_changed_pct']
    result.meets_30pct_criterion   = (
        eval_metrics['avg_numbers_changed_pct'] >= NUMBER_CHANGE_TARGET
    )

    successful_segs = [s for s in seg_results if s.rewriting_success]
    result.avg_high_level_retries = (
        sum(s.high_level_retries for s in successful_segs) / len(successful_segs)
        if successful_segs else 0.0
    )

    result.total_time     = time.time() - total_start
    result.overall_success = len(successful_segs) > 0

    print(_sep('─'))
    print(f"  Gesamtzeit: {result.total_time:.2f}s  |  Status: "
          f"{'OK' if result.overall_success else 'FEHLER'}")

    return result


# ── Vergleichstabelle ────────────────────────────────────────────────────────
def print_comparison_table(results: List[CombinationResult]) -> None:
    """Gibt eine strukturierte Vergleichstabelle auf der Konsole aus."""
    COL = 22
    LBL = 32

    def row(name: str, fns) -> None:
        print(f"  {name:<{LBL}}", end='')
        for r, fn in zip(results, fns):
            try:
                val = fn(r)
            except Exception:
                val = 'N/A'
            print(f"{str(val):^{COL}}", end='')
        print()

    fns_const = [lambda r, c=c: (lambda r: c)(r) for c in [r.label for r in results]]

    print(f"\n{_sep('═', 80)}")
    print("  VERGLEICHSTABELLE – Pipeline-Kombinationen")
    print(_sep('═', 80))

    # Header
    print(f"  {'Metrik':<{LBL}}", end='')
    for r in results:
        print(f"{r.label[:COL]:^{COL}}", end='')
    print()
    print(_sep('─', 80))

    # ── Phase 1: OCR ──────────────────────────────────────────────────────────
    print(f"\n  {'── Phase 1: OCR'}")
    for name, fn in [
        ('Tool',            lambda r: r.ocr_tool),
        ('Zeit (s)',         lambda r: f"{r.ocr.processing_time:.2f}" if r.ocr else 'N/A'),
        ('Seiten',           lambda r: str(r.ocr.pages) if r.ocr else 'N/A'),
        ('Zeichen',          lambda r: f"{r.ocr.char_count:,}" if r.ocr else 'N/A'),
        ('Wörter',           lambda r: f"{r.ocr.word_count:,}" if r.ocr else 'N/A'),
    ]:
        row(name, [fn] * len(results))

    # ── Phase 2: Rewriting ────────────────────────────────────────────────────
    print(f"\n  {'── Phase 2: Rewriting'}")
    for name, fn in [
        ('LLM-Provider',         lambda r: r.llm_provider),
        ('Segmente verarbeitet', lambda r: str(r.segments_processed)),
        ('Varianten generiert',  lambda r: str(r.total_variants)),
        ('Ø Retries/Segment',    lambda r: f"{r.avg_high_level_retries:.1f}"),
    ]:
        row(name, [fn] * len(results))

    # ── Phase 3: Evaluierung ──────────────────────────────────────────────────
    print(f"\n  {'── Phase 3: Evaluierung'}")
    for name, fn in [
        ('Valide / Gesamt',      lambda r: f"{r.valid_variants}/{r.total_variants}"),
        ('Validierungsrate',     lambda r: f"{r.validation_rate*100:.0f}%"),
        ('Ø Diversity-Score',    lambda r: f"{r.avg_diversity_score:.3f}"),
        ('Ø Zahlenänderung',     lambda r: f"{r.avg_numbers_changed_pct*100:.0f}%"),
        ('≥30 % Ziel erfüllt',   lambda r: '✓ JA' if r.meets_30pct_criterion else '✗ NEIN'),
    ]:
        row(name, [fn] * len(results))

    # ── Gesamt ────────────────────────────────────────────────────────────────
    print(f"\n  {'── Gesamt'}")
    for name, fn in [
        ('Gesamtzeit (s)',  lambda r: f"{r.total_time:.2f}"),
        ('Status',          lambda r: '✓ OK' if r.overall_success else '✗ FEHLER'),
    ]:
        row(name, [fn] * len(results))

    print(_sep('─', 80))

    # ── Siegeranalyse ─────────────────────────────────────────────────────────
    ok = [r for r in results if r.overall_success]
    if ok:
        print("\n  AUSWERTUNG:")

        best_val = max(ok, key=lambda r: r.validation_rate)
        print(f"    Beste Validierungsrate : {best_val.label}  "
              f"({best_val.validation_rate * 100:.0f}%)")

        best_div = max(ok, key=lambda r: r.avg_diversity_score)
        print(f"    Beste Diversity-Score  : {best_div.label}  "
              f"({best_div.avg_diversity_score:.3f})")

        fastest = min(ok, key=lambda r: r.total_time)
        print(f"    Schnellste Pipeline    : {fastest.label}  "
              f"({fastest.total_time:.2f}s)")

        meets = [r for r in ok if r.meets_30pct_criterion]
        if meets:
            labels = ', '.join(r.label for r in meets)
            print(f"    ≥30 % Zahlenänderung   : {labels}")
        else:
            print("    ≥30 % Zahlenänderung   : Kein Treffer – ggf. Prompt anpassen")
    else:
        print("\n  Keine Kombination erfolgreich abgeschlossen.")

    print(_sep('═', 80))


# ── JSON-Report speichern ────────────────────────────────────────────────────
def save_report(results: List[CombinationResult], pdf_path: Path) -> Path:
    """Speichert alle Ergebnisse als JSON-Datei."""
    ts          = time.strftime('%Y%m%d_%H%M%S')
    out_dir     = Config.DATA_OUTPUT_PATH / 'comparison'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file    = out_dir / f"pipeline_comparison_{pdf_path.stem}_{ts}.json"

    report: Dict[str, Any] = {
        'timestamp'  : time.strftime('%Y-%m-%d %H:%M:%S'),
        'input_pdf'  : str(pdf_path),
        'config'     : {
            'max_retry_attempts'   : MAX_RETRY_ATTEMPTS,
            'num_variants'         : NUM_VARIANTS,
            'max_segments'         : MAX_SEGMENTS,
            'number_change_target' : NUMBER_CHANGE_TARGET,
        },
        'combinations': [],
    }

    for r in results:
        entry: Dict[str, Any] = {
            'id'           : r.id,
            'label'        : r.label,
            'ocr_tool'     : r.ocr_tool,
            'llm_provider' : r.llm_provider,
            'total_time_s' : round(r.total_time, 3),
            'overall_success': r.overall_success,
            'error'        : r.error,
            'phase1_ocr': {
                'success'         : r.ocr.success if r.ocr else False,
                'tool'            : r.ocr.tool if r.ocr else '',
                'processing_time' : round(r.ocr.processing_time, 3) if r.ocr else 0,
                'pages'           : r.ocr.pages if r.ocr else 0,
                'char_count'      : r.ocr.char_count if r.ocr else 0,
                'word_count'      : r.ocr.word_count if r.ocr else 0,
                'error'           : r.ocr.error if r.ocr else '',
            },
            'phase2_rewriting': {
                'segments_processed'   : r.segments_processed,
                'total_variants'       : r.total_variants,
                'avg_high_level_retries': round(r.avg_high_level_retries, 2),
                'segments': [
                    {
                        'index'            : s.segment_index,
                        'domain'           : s.domain,
                        'success'          : s.rewriting_success,
                        'rewriting_time_s' : round(s.rewriting_time, 3),
                        'high_level_retries': s.high_level_retries,
                        'num_variants'     : len(s.variants),
                        'variants': [
                            {
                                'id'                  : v.variant_id,
                                'llm_attempts'        : v.llm_attempts,
                                'is_valid'            : v.is_valid,
                                'numbers_changed_pct' : round(v.numbers_changed_pct, 3),
                                'diversity_score'     : round(v.diversity_score, 3),
                                'validation_issues'   : v.validation_issues,
                                'text_preview'        : v.text[:200] if v.text else '',
                            }
                            for v in s.variants
                        ],
                    }
                    for s in r.segment_results
                ],
            },
            'phase3_evaluation': {
                'total_variants'          : r.total_variants,
                'valid_variants'          : r.valid_variants,
                'validation_rate'         : round(r.validation_rate, 4),
                'avg_diversity_score'     : round(r.avg_diversity_score, 4),
                'avg_numbers_changed_pct' : round(r.avg_numbers_changed_pct, 4),
                'meets_30pct_criterion'   : r.meets_30pct_criterion,
            },
        }
        report['combinations'].append(entry)

    with open(out_file, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    print(f"\n  JSON-Report gespeichert: {out_file}")
    return out_file


# ── CLI-Einstiegspunkt ───────────────────────────────────────────────────────
def _find_default_pdf() -> Optional[Path]:
    """Sucht das erste vorhandene Standard-Test-PDF."""
    candidates = [
        Config.DATA_INPUT_PATH / 'math'      / 'equations_simple.pdf',
        Config.DATA_INPUT_PATH / 'economics'  / 'balance_sheet.pdf',
        Config.DATA_INPUT_PATH / 'languages'  / 'grammar_exercise.pdf',
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Pipeline-Vergleich: 4 OCR × LLM Kombinationen'
    )
    parser.add_argument(
        'pdf', nargs='?', type=Path,
        help='Pfad zur Input-PDF (optional; nutzt sonst erstes Standard-PDF)',
    )
    parser.add_argument(
        '--combos', type=str, default='1,2,3,4',
        help='Komma-separierte Kombinations-IDs (z.B. --combos 1,3)',
    )
    args = parser.parse_args()

    # PDF bestimmen
    if args.pdf:
        pdf_path = args.pdf
        if not pdf_path.exists():
            print(f"FEHLER: PDF nicht gefunden: {pdf_path}")
            sys.exit(1)
    else:
        pdf_path = _find_default_pdf()
        if pdf_path is None:
            print("FEHLER: Kein Standard-Test-PDF gefunden.")
            print("Bitte PDF als Argument angeben oder Test-PDFs generieren:")
            print("  python scripts/generate_test_pdfs.py")
            sys.exit(1)

    # Kombinations-Filter
    try:
        selected_ids = {int(x.strip()) for x in args.combos.split(',')}
    except ValueError:
        print("FEHLER: --combos muss komma-separierte Zahlen enthalten, z.B. '1,3'")
        sys.exit(1)

    combos_to_run = [c for c in COMBINATIONS if c['id'] in selected_ids]
    if not combos_to_run:
        print("FEHLER: Keine gültigen Kombinations-IDs ausgewählt.")
        sys.exit(1)

    # Header
    print(_sep('═', 80))
    print("  PIPELINE COMPARISON  –  Content-Rewriting für Lernmaterialien")
    print(_sep('═', 80))
    print(f"  Input-PDF  : {pdf_path}")
    print(f"  Segmente   : max. {MAX_SEGMENTS} pro Kombination")
    print(f"  Varianten  : {NUM_VARIANTS} pro Segment")
    print(f"  Retries    : max. {MAX_RETRY_ATTEMPTS} Versuche (Phase 2, high-level)")
    print(f"  Ziel       : ≥{int(NUMBER_CHANGE_TARGET * 100)} % Zahlenänderung")
    print("\n  Testmatrix:")
    for c in combos_to_run:
        print(f"    {c['id']}. {c['label']}")

    # Alle Kombinationen durchführen
    results: List[CombinationResult] = []
    for combo in combos_to_run:
        result = run_combination(combo, pdf_path)
        results.append(result)

    # Vergleichstabelle
    print_comparison_table(results)

    # Report speichern
    save_report(results, pdf_path)

    print("\n  Vergleich abgeschlossen.")


if __name__ == '__main__':
    main()
