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


def _categorize_issue(issue: str) -> str:
    """Mapt eine Issue-Beschreibung auf eine Kategorie."""
    if "BERTScore" in issue or "Semantische" in issue:
        return "BERTScore"
    if "Anzahl Zahlen" in issue:
        return "Zahlen-Anzahl"
    if "Länge" in issue:
        return "Längen-Check"
    if "Prompt-Text" in issue:
        return "Prompt-Leak"
    if "LLM-Check" in issue:
        return "LLM-Plausibilität"
    if "Zahlenvariation" in issue:
        return "Zahlenvariation <30%"
    if "Gleichungen" in issue:
        return "Gleichungsanzahl"
    if "Platzhalter" in issue:
        return "Platzhalter"
    return f"Sonstiges: {issue[:40]}"


def _print_validation_details(vr: dict):
    """Druckt zusätzliche Details aus den validation_results."""
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
            for li in llm.get("issues") or []:
                print(f"      {li}")
    if "length_check" in vr:
        lc = vr["length_check"]
        print(f"    → Länge: {lc['original_length']} → {lc['variant_length']} (Ratio: {lc['ratio']:.2f})")


def _process_segment(seg: dict, agent: str, all_issues: Counter) -> str:
    """Verarbeitet ein Segment. Gibt 'skip', 'valid' oder 'invalid' zurück."""
    a = seg["agents"].get(agent, {})
    if a.get("error"):
        return "skip"

    original = seg["input_text"]
    variant = a.get("output_text", "")

    if not variant:
        return "skip"

    result = validate_segment(original, variant, DOMAIN_ECONOMICS)
    if result["is_valid"]:
        return "valid"

    print(f"\n  [{seg['pdf']}] Seg {seg['index']}")
    print(f"    Original:  {original[:80]}...")
    print(f"    Variante:  {variant[:80]}...")

    for issue in result["issues"]:
        print(f"    ✗ {issue}")
        all_issues[_categorize_issue(issue)] += 1

    _print_validation_details(result.get("validation_results", {}))
    return "invalid"


def _print_summary(valid_count: int, invalid_count: int, all_issues: Counter):
    print(f"\n{'=' * 70}")
    print("  ZUSAMMENFASSUNG")
    print(f"{'=' * 70}")
    print(f"  Valide: {valid_count}, Invalide: {invalid_count}")
    print("\n  Häufigkeit der Ablehnungsgründe:")
    for issue, count in all_issues.most_common():
        bar = "█" * count
        print(f"    {issue:25s}: {count:3d}  {bar}")

    total_issues = sum(all_issues.values())
    print(f"\n  Total Issues: {total_issues} über {invalid_count} invalide Segmente")
    print(f"  Ø Issues pro Segment: {total_issues / invalid_count:.1f}" if invalid_count else "")


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
    all_issues: Counter = Counter()
    invalid_count = 0
    valid_count = 0

    print("=" * 70)
    print("  ECONOMICS — Validierungs-Diagnose (Pipeline)")
    print("=" * 70)

    for seg in data["segments"]:
        outcome = _process_segment(seg, agent, all_issues)
        if outcome == "valid":
            valid_count += 1
        elif outcome == "invalid":
            invalid_count += 1

    _print_summary(valid_count, invalid_count, all_issues)


if __name__ == "__main__":
    main()
