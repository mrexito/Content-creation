#!/usr/bin/env python3
"""
BERTScore Threshold-Kalibrierung
================================

Berechnet BERTScore (F1) für manuell bewertete Original-Variante-Paare
und findet den optimalen Schwellwert, der gute von schlechten Varianten trennt.

Workflow:
  1. Skript extrahiert Paare aus den Vergleichs-JSONs (comparison_*.json)
  2. Du bewertest jedes Paar manuell (GUT / SCHLECHT / GRENZFALL)
  3. Skript berechnet BERTScores und empfiehlt den optimalen Threshold

Voraussetzungen:
  pip install bert-score torch

Ausführung:
  1. Kopiere die drei comparison_*.json in denselben Ordner wie dieses Skript
     ODER passe COMPARISON_DIR unten an.
  2. python calibrate_bert_threshold.py --step1    → extrahiert Paare nach calibration_pairs.json
  3. Öffne calibration_pairs.json, bewerte jedes Paar (Feld "manual_label")
  4. python calibrate_bert_threshold.py --step2    → berechnet Scores + optimalen Threshold
"""

import argparse
import json
import sys
from pathlib import Path

# ── Konfiguration ────────────────────────────────────────────────────────────
COMPARISON_DIR = Path(".")  # Ordner mit comparison_*.json
PAIRS_FILE = Path("calibration_pairs.json")
RESULTS_FILE = Path("calibration_results.json")

# Wie viele Paare pro Kategorie (valid/invalid) und Domäne samplen
SAMPLES_PER_CATEGORY = 5

# Baseline-Threshold aus Vorstudie (Anhang c, Tabelle 3)
BASELINE_THRESHOLD = 0.92


# ── Step 1: Paare extrahieren ────────────────────────────────────────────────

def extract_pairs():
    """
    Extrahiert Original-Variante-Paare aus den Vergleichs-JSONs.
    Wählt eine balancierte Stichprobe: je SAMPLES_PER_CATEGORY valide und
    invalide Paare pro Domäne, aus der langchain_pipeline-Variante.
    """
    comparison_files = sorted(COMPARISON_DIR.glob("comparison_*.json"))
    if not comparison_files:
        print(f"FEHLER: Keine comparison_*.json in {COMPARISON_DIR.resolve()} gefunden.")
        print("Kopiere die Dateien hierher oder passe COMPARISON_DIR an.")
        sys.exit(1)

    all_pairs = []

    for cfile in comparison_files:
        with open(cfile) as f:
            data = json.load(f)

        domain = data.get("domain", "unknown")
        agent_key = "langchain_pipeline"

        valid_pairs = []
        invalid_pairs = []

        for seg in data.get("segments", []):
            agent = seg.get("agents", {}).get(agent_key, {})
            if agent.get("error") or not agent.get("output_text"):
                continue

            pair = {
                "id": f"{domain}_{seg['pdf']}_{seg['index']}",
                "domain": domain,
                "pdf": seg["pdf"],
                "segment_index": seg["index"],
                "original": seg["input_text"],
                "variant": agent["output_text"],
                "was_valid_at_092": agent["is_valid"],
                "manual_label": "TODO",  # ← DU FÜLLST DAS AUS
                # Erlaubte Werte:
                #   "GUT"       = Variante ist inhaltlich korrekt, sinnvolle Paraphrase
                #   "SCHLECHT"  = Variante ist semantisch falsch, Unsinn, oder kaputt
                #   "GRENZFALL" = Variante ist unklar oder teilweise OK
            }

            if agent["is_valid"]:
                valid_pairs.append(pair)
            else:
                invalid_pairs.append(pair)

        # Balancierte Stichprobe
        selected = valid_pairs[:SAMPLES_PER_CATEGORY] + invalid_pairs[:SAMPLES_PER_CATEGORY]
        all_pairs.extend(selected)

    # Speichern
    with open(PAIRS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_pairs, f, ensure_ascii=False, indent=2)

    n_valid = sum(1 for p in all_pairs if p["was_valid_at_092"])
    n_invalid = sum(1 for p in all_pairs if not p["was_valid_at_092"])

    print(f"✓ {len(all_pairs)} Paare extrahiert nach {PAIRS_FILE}")
    print(f"  Davon valid@0.92: {n_valid}, invalid@0.92: {n_invalid}")
    print(f"  Domänen: {sorted({p['domain'] for p in all_pairs})}")
    print()
    print("NÄCHSTER SCHRITT:")
    print(f"  1. Öffne {PAIRS_FILE}")
    print('  2. Setze "manual_label" auf "GUT", "SCHLECHT" oder "GRENZFALL"')
    print(f"  3. Führe aus: python {sys.argv[0]} --step2")


# ── Step 2: BERTScore berechnen + Threshold finden ───────────────────────────

def _validate_pairs_labeled(pairs):
    """Beendet das Skript mit Fehler, wenn nicht alle Paare bewertet sind."""
    todos = [p for p in pairs if p["manual_label"] == "TODO"]
    if not todos:
        return
    print(f"FEHLER: {len(todos)} Paare haben noch manual_label='TODO'.")
    print(f"Bitte alle Paare in {PAIRS_FILE} bewerten.")
    for t in todos[:3]:
        print(f"  → {t['id']}")
    sys.exit(1)


def _compute_bert_scores(pairs):
    """Berechnet BERTScore für alle Paare und annotiert sie in-place."""
    print("BERTScore wird berechnet (kann 30-60s dauern)...")
    try:
        from bert_score import score as bert_score_fn
        import torch
    except ImportError:
        print("FEHLER: bert-score nicht installiert.")
        print("  pip install bert-score torch")
        sys.exit(1)

    originals = [p["original"] for p in pairs]
    variants = [p["variant"] for p in pairs]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    P, R, F1 = bert_score_fn(
        variants,
        originals,
        model_type="bert-base-multilingual-cased",
        lang="de",
        device=device,
        verbose=True,
    )

    for i, pair in enumerate(pairs):
        pair["bertscore_f1"] = round(float(F1[i]), 4)
        pair["bertscore_precision"] = round(float(P[i]), 4)
        pair["bertscore_recall"] = round(float(R[i]), 4)


def _print_score_stats(label, scores):
    """Druckt min/max/mean/median für eine Score-Liste."""
    if not scores:
        return
    median = sorted(scores)[len(scores) // 2]
    print(f"  {label} — F1: min={min(scores):.4f}  max={max(scores):.4f}  "
          f"mean={sum(scores)/len(scores):.4f}  median={median:.4f}")


def _print_label_stats(gut, schlecht, grenzfall):
    print(f"\n{'='*70}")
    print("  KALIBRIERUNGSERGEBNISSE")
    print(f"{'='*70}")
    print(f"  Bewertungen: {len(gut)} GUT, {len(schlecht)} SCHLECHT, {len(grenzfall)} GRENZFALL")
    if gut:
        print()  # Leerzeile vor erstem Stat-Block (wie im Original)
    _print_score_stats("GUT     ", [p["bertscore_f1"] for p in gut])
    _print_score_stats("SCHLECHT", [p["bertscore_f1"] for p in schlecht])
    _print_score_stats("GRENZFALL", [p["bertscore_f1"] for p in grenzfall])


def _classification_metrics(gut, schlecht, threshold):
    """Berechnet TP/FP/FN/TN + Precision/Recall/F1 für gegebenen Threshold."""
    tp = sum(1 for p in gut if p["bertscore_f1"] >= threshold)
    fp = sum(1 for p in schlecht if p["bertscore_f1"] >= threshold)
    fn = sum(1 for p in gut if p["bertscore_f1"] < threshold)
    tn = sum(1 for p in schlecht if p["bertscore_f1"] < threshold)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision, "recall": recall, "f1": f1,
    }


def _find_optimal_threshold(gut, schlecht):
    """Sucht Threshold mit maximalem F1 zwischen 0.70 und 0.95.
    Druckt Tabelle, gibt (best_threshold, best_f1, best_details) zurück.
    """
    print(f"\n  {'Threshold':>10s} | {'TP':>3s} {'FP':>3s} {'FN':>3s} {'TN':>3s} | "
          f"{'Precision':>9s} {'Recall':>6s} {'F1':>6s}")
    print(f"  {'-'*10} | {'-'*3} {'-'*3} {'-'*3} {'-'*3} | {'-'*9} {'-'*6} {'-'*6}")

    best_threshold = 0.80
    best_f1 = 0.0
    best_details = {}

    for t_int in range(70, 96):
        threshold = t_int / 100.0
        m = _classification_metrics(gut, schlecht, threshold)

        marker = ""
        if m["f1"] > best_f1:
            best_f1 = m["f1"]
            best_threshold = threshold
            best_details = m
            marker = " ← best"

        print(f"  {threshold:>10.2f} | {m['tp']:>3d} {m['fp']:>3d} {m['fn']:>3d} {m['tn']:>3d} | "
              f"{m['precision']:>9.3f} {m['recall']:>6.3f} {m['f1']:>6.3f}{marker}")

    return best_threshold, best_f1, best_details


def _print_threshold_summary(best_threshold, best_f1, best_details):
    print(f"\n{'='*70}")
    print(f"  EMPFOHLENER THRESHOLD: {best_threshold:.2f}")
    print(f"{'='*70}")
    print(f"  F1-Score der Klassifikation: {best_f1:.3f}")
    print(f"  True Positives:  {best_details['tp']} (gute Varianten korrekt akzeptiert)")
    print(f"  False Positives: {best_details['fp']} (schlechte Varianten fälschlich akzeptiert)")
    print(f"  False Negatives: {best_details['fn']} (gute Varianten fälschlich abgelehnt)")
    print(f"  True Negatives:  {best_details['tn']} (schlechte Varianten korrekt abgelehnt)")


def _print_baseline_comparison(gut, schlecht, best_threshold, best_f1):
    """Vergleicht den besten Threshold mit dem Baseline-Threshold (0.92)."""
    m = _classification_metrics(gut, schlecht, BASELINE_THRESHOLD)
    print(f"\n  Vergleich mit aktuellem Threshold ({BASELINE_THRESHOLD}):")
    print(f"    F1@{BASELINE_THRESHOLD} = {m['f1']:.3f} vs F1@{best_threshold:.2f} = {best_f1:.3f}")
    if best_f1 > m["f1"]:
        print(f"    → Verbesserung um {(best_f1 - m['f1'])*100:.1f} Prozentpunkte")
    return m


def _classify_marker(score, threshold):
    return "✓" if score >= threshold else "✗"


def _correctness_note(label, marker):
    if label == "GUT" and marker == "✗":
        return "  ← FALSE NEGATIVE"
    if label == "SCHLECHT" and marker == "✓":
        return "  ← FALSE POSITIVE"
    return ""


def _print_individual_results(pairs, best_threshold):
    print(f"\n{'='*70}")
    print("  EINZELERGEBNISSE (sortiert nach BERTScore F1)")
    print(f"{'='*70}")

    for p in sorted(pairs, key=lambda x: x["bertscore_f1"]):
        score = p["bertscore_f1"]
        marker = _classify_marker(score, best_threshold)
        match_baseline = _classify_marker(score, BASELINE_THRESHOLD)
        correct = _correctness_note(p["manual_label"], marker)
        print(f"  {score:.4f} [{marker}@{best_threshold:.2f}|{match_baseline}@{BASELINE_THRESHOLD}] "
              f"{p['manual_label']:>10s}  {p['domain']:>10s}  {p['pdf'][:25]}{correct}")


def _print_claude_prompt(best_threshold, gut_count, schlecht_count):
    print(f"\n{'='*70}")
    print("  CLAUDE CODE PROMPT (zum Anwenden des neuen Thresholds)")
    print(f"{'='*70}")
    print(f"""
Ändere in src/common/constants.py:

    BERT_THRESHOLD: float = {best_threshold}

Aktualisiere den Kommentar darüber:

    # Wert {best_threshold} empirisch kalibriert mit {gut_count + schlecht_count} manuell
    # bewerteten Paaren (Sprache + Wirtschaft). Optimiert auf maximalen
    # F1-Score der Klassifikation GUT vs. SCHLECHT.
    # Vorstudie (Anhang c, Tabelle 3) schlug 0.92 vor — empirische
    # Kalibrierung zeigt, dass dieser Wert zu restriktiv ist für
    # bert-base-multilingual-cased mit deutschen Paraphrasen.
    BERT_THRESHOLD: float = {best_threshold}
""")


def compute_and_calibrate():
    """Berechnet BERTScore für alle Paare und findet den optimalen Threshold."""
    if not PAIRS_FILE.exists():
        print(f"FEHLER: {PAIRS_FILE} nicht gefunden. Zuerst --step1 ausführen.")
        sys.exit(1)

    with open(PAIRS_FILE) as f:
        pairs = json.load(f)

    _validate_pairs_labeled(pairs)
    _compute_bert_scores(pairs)

    gut = [p for p in pairs if p["manual_label"] == "GUT"]
    schlecht = [p for p in pairs if p["manual_label"] == "SCHLECHT"]
    grenzfall = [p for p in pairs if p["manual_label"] == "GRENZFALL"]

    _print_label_stats(gut, schlecht, grenzfall)

    # Nur GUT vs. SCHLECHT für die Optimierung (GRENZFALL wird ignoriert)
    if not gut or not schlecht:
        print("\nFEHLER: Brauche mindestens 1 GUT und 1 SCHLECHT für Optimierung.")
        _save_results(pairs, None)
        return

    best_threshold, best_f1, best_details = _find_optimal_threshold(gut, schlecht)
    _print_threshold_summary(best_threshold, best_f1, best_details)
    baseline = _print_baseline_comparison(gut, schlecht, best_threshold, best_f1)
    _print_individual_results(pairs, best_threshold)
    _print_claude_prompt(best_threshold, len(gut), len(schlecht))

    _save_results(pairs, {
        "optimal_threshold": best_threshold,
        "classification_f1": best_f1,
        "details": best_details,
        "comparison_092": {
            "precision": baseline["precision"],
            "recall": baseline["recall"],
            "f1": baseline["f1"],
        },
        "sample_size": {
            "gut": len(gut),
            "schlecht": len(schlecht),
            "grenzfall": len(grenzfall),
        },
    })


def _save_results(pairs, analysis):
    """Speichert Ergebnisse als JSON."""
    output = {
        "analysis": analysis,
        "pairs": pairs,
    }
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Vollständige Ergebnisse gespeichert in {RESULTS_FILE}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="BERTScore Threshold-Kalibrierung für die Thesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow:
  python calibrate_bert_threshold.py --step1
  → Editiere calibration_pairs.json (manual_label setzen)
  python calibrate_bert_threshold.py --step2
        """,
    )
    parser.add_argument("--step1", action="store_true", help="Paare aus JSONs extrahieren")
    parser.add_argument("--step2", action="store_true", help="BERTScore berechnen + Threshold finden")
    parser.add_argument("--dir", type=str, default=".", help="Ordner mit comparison_*.json")

    args = parser.parse_args()

    global COMPARISON_DIR
    COMPARISON_DIR = Path(args.dir)

    if args.step1:
        extract_pairs()
    elif args.step2:
        compute_and_calibrate()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
