"""
Diagnose: Welche Validierungschecks scheitern in der Wirtschaftsdomäne?

Liest die comparison_economics JSON und führt validate_segment() auf
alle invaliden Pipeline-Segmente aus. Gibt pro Segment die exakten
Issues aus.

Usage:
    python scripts/diagnose_economics_validation.py <path_to_comparison_economics.json>

Beispiel:
    python scripts/diagnose_economics_validation.py comparison_economics_20260412_124258.json
"""
import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.validators.segment_validator import validate_segment
from common.constants import DOMAIN_ECONOMICS


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/diagnose_economics_validation.py <comparison_economics.json>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"Datei nicht gefunden: {json_path}")
        sys.exit(1)

    with open(json_path) as f:
        data = json.load(f)

    agent = "langchain_pipeline"
    all_issues = Counter()
    invalid_count = 0
    valid_count = 0

    print("=" * 70)
    print("  ECONOMICS — Validierungs-Diagnose (Pipeline)")
    print("=" * 70)

    for seg in data["segments"]:
        a = seg["agents"].get(agent, {})
        if a.get("error"):
            continue

        original = seg["input_text"]
        variant = a.get("output_text", "")

        if not variant:
            continue

        result = validate_segment(original, variant, DOMAIN_ECONOMICS)

        if result["is_valid"]:
            valid_count += 1
            continue

        invalid_count += 1
        issues = result["issues"]

        print(f"\n  [{seg['pdf']}] Seg {seg['index']}")
        print(f"    Original:  {original[:80]}...")
        print(f"    Variante:  {variant[:80]}...")

        for issue in issues:
            print(f"    ✗ {issue}")

            # Kategorisiere
            if "BERTScore" in issue or "Semantische" in issue:
                all_issues["BERTScore"] += 1
            elif "Anzahl Zahlen" in issue:
                all_issues["Zahlen-Anzahl"] += 1
            elif "Länge" in issue:
                all_issues["Längen-Check"] += 1
            elif "Prompt-Text" in issue:
                all_issues["Prompt-Leak"] += 1
            elif "LLM-Check" in issue:
                all_issues["LLM-Plausibilität"] += 1
            elif "Zahlenvariation" in issue:
                all_issues["Zahlenvariation <30%"] += 1
            elif "Gleichungen" in issue:
                all_issues["Gleichungsanzahl"] += 1
            elif "Platzhalter" in issue:
                all_issues["Platzhalter"] += 1
            else:
                all_issues[f"Sonstiges: {issue[:40]}"] += 1

        # Zusätzliche Details
        vr = result.get("validation_results", {})
        if "bert_economics" in vr:
            score = vr["bert_economics"].get("score", 0)
            print(f"    → BERTScore F1: {score:.4f} (Threshold: 0.81)")
        if "consistency" in vr:
            orig_n = vr["consistency"].get("num_original", 0)
            var_n = vr["consistency"].get("num_variant", 0)
            print(f"    → Zahlen: {orig_n} (orig) vs {var_n} (var)")
        if "llm_plausibility" in vr:
            llm = vr["llm_plausibility"]
            if not llm.get("skipped"):
                print(f"    → LLM-Check: valid={llm.get('is_valid')}")
                if llm.get("issues"):
                    for li in llm["issues"]:
                        print(f"      {li}")
        if "length_check" in vr:
            lc = vr["length_check"]
            print(f"    → Länge: {lc['original_length']} → {lc['variant_length']} (Ratio: {lc['ratio']:.2f})")

    print(f"\n{'=' * 70}")
    print(f"  ZUSAMMENFASSUNG")
    print(f"{'=' * 70}")
    print(f"  Valide: {valid_count}, Invalide: {invalid_count}")
    print(f"\n  Häufigkeit der Ablehnungsgründe:")
    for issue, count in all_issues.most_common():
        bar = "█" * count
        print(f"    {issue:25s}: {count:3d}  {bar}")

    total_issues = sum(all_issues.values())
    print(f"\n  Total Issues: {total_issues} über {invalid_count} invalide Segmente")
    print(f"  Ø Issues pro Segment: {total_issues / invalid_count:.1f}" if invalid_count else "")


if __name__ == "__main__":
    main()