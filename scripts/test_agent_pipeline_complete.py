"""
Test: End-to-End Agent Pipeline

Verarbeitet ein vollständiges PDF mit beiden Agenten-Varianten und
vergleicht die Ergebnisse.

Ausführung:
    python scripts/test_agent_pipeline_complete.py math
    python scripts/test_agent_pipeline_complete.py math --variant orchestrator
    python scripts/test_agent_pipeline_complete.py math --variant multi_agent
    python scripts/test_agent_pipeline_complete.py math --both
"""
import sys
import argparse
import time
from pathlib import Path
sys.path.insert(0, "src")

from common.config import Config
from common.logger import setup_logger
from langchain_agent_prototype.pipeline import get_pipeline

logger = setup_logger(__name__)

DOMAIN_PDF_MAP = {
    "math":       ("data/input/math/equations_simple.pdf",       "math"),
    "languages":  ("data/input/languages/grammar_exercise.pdf",  "languages"),
    "economics":  ("data/input/economics/balance_sheet.pdf",     "economics"),
}


def print_separator(title: str = "", char: str = "=", width: int = 70):
    if title:
        print(f"\n{char * width}")
        print(title.center(width))
        print(f"{char * width}")
    else:
        print(f"{char * width}")


def run_pipeline(pdf_path: Path, domain: str, variant: str) -> dict:
    print_separator(f"Variante: {variant.upper()}", char="-")
    print(f"   PDF:     {pdf_path.name}")
    print(f"   Domain:  {domain}")
    print(f"   Variant: {variant}")
    print()

    pipeline = get_pipeline(
        variant=variant,
        domain=domain,
        num_variants=1,
        max_retries=3,
    )

    result = pipeline.process_pdf(pdf_path)

    if result["success"]:
        stats = result["statistics"]
        agent_stats = stats.get("agent", {})
        assembly = stats.get("assembly", {})

        print(f"\n✅ Pipeline erfolgreich!")
        print(f"   Gesamt-Zeit:      {stats['total_time']:.2f}s")
        print(f"   Segmente:         {stats.get('segmentation', {}).get('num_segments', '?')}")
        print(f"   Tool-Calls:       {agent_stats.get('total_tool_calls', 0)}")
        print(f"   Rewrite-Versuche: {agent_stats.get('total_attempts', 0)}")
        print(f"   Valide Varianten: {agent_stats.get('valid_variants', 0)}")
        print(f"   Invalide:         {agent_stats.get('invalid_variants', 0)}")
        print(f"   Übersprungen:     {agent_stats.get('skipped', 0)}")
        print(f"\n   Output-Dateien:")
        for f in result.get("output_files", []):
            print(f"   → {f}")
    else:
        print(f"\n❌ Pipeline fehlgeschlagen: {result.get('error')}")

    return result


def compare_results(result_a: dict, result_b: dict):
    print_separator("VERGLEICH A vs. B", char="=")

    def stats(r, label):
        s = r.get("statistics", {})
        a = s.get("agent", {})
        return {
            "label": label,
            "time": f"{s.get('total_time', 0):.2f}s",
            "tool_calls": a.get("total_tool_calls", 0),
            "attempts": a.get("total_attempts", 0),
            "valid": a.get("valid_variants", 0),
            "invalid": a.get("invalid_variants", 0),
        }

    ra = stats(result_a, "Orchestrator (A)")
    rb = stats(result_b, "Multi-Agent (B)")

    print(f"\n{'Metrik':<25} {'Variante A':>15} {'Variante B':>15}")
    print("-" * 55)
    metrics = [
        ("Gesamt-Zeit", "time"),
        ("Tool-Calls gesamt", "tool_calls"),
        ("Rewrite-Versuche", "attempts"),
        ("Valide Varianten", "valid"),
        ("Invalide Varianten", "invalid"),
    ]
    for label, key in metrics:
        print(f"{label:<25} {str(ra[key]):>15} {str(rb[key]):>15}")

    print(f"\n📌 INTERPRETATION:")
    if ra["tool_calls"] > rb["tool_calls"]:
        diff = ra["tool_calls"] - rb["tool_calls"]
        print(f"   → Variante A nutzt {diff} Tool-Calls mehr (Retry-Aktivität)")
    elif ra["tool_calls"] == rb["tool_calls"]:
        print(f"   → Gleichviele Tool-Calls: Kein Retry bei Variante A nötig")
    else:
        print(f"   → Variante B nutzt mehr Calls (unerwartetes LLM-Verhalten)")

    if ra["attempts"] > rb["attempts"]:
        print(f"   → Variante A hat {ra['attempts'] - rb['attempts']} mehr Rewriting-Versuche")
        print(f"      (Retries bei invaliden Varianten — Mehrwert des Agenten-Patterns)")
    else:
        print(f"   → Gleiche Anzahl Versuche: Kein Retry-Unterschied messbar")

    print(f"\n   Thesis-Fazit:")
    print(f"   Variante A (Orchestrierungsagent) kann Retries autonom auslösen.")
    print(f"   Variante B (Multi-Agent) hat keine übergeordnete Retry-Logik.")
    print(f"   LangGraph hat explizite Retry-Kanten (Conditional Edges).")


def main():
    parser = argparse.ArgumentParser(description="Agent Pipeline End-to-End Test")
    parser.add_argument("domain", choices=["math", "languages", "economics"],
                        help="Test-Domain")
    parser.add_argument("--variant", choices=["orchestrator", "multi_agent"],
                        default="orchestrator",
                        help="Agenten-Variante (default: orchestrator)")
    parser.add_argument("--both", action="store_true",
                        help="Beide Varianten ausführen und vergleichen")
    args = parser.parse_args()

    pdf_rel, domain = DOMAIN_PDF_MAP[args.domain]
    pdf_path = Config.PROJECT_ROOT / pdf_rel

    if not pdf_path.exists():
        print(f"❌ PDF nicht gefunden: {pdf_path}")
        print(f"   Führe zuerst aus: python scripts/generate_test_pdfs.py")
        sys.exit(1)

    print_separator("AGENT PIPELINE — END-TO-END TEST")
    print(f"\n   Domain: {args.domain}")
    print(f"   PDF:    {pdf_path}")
    print(f"   Mode:   {'Beide Varianten' if args.both else args.variant}")

    if args.both:
        result_a = run_pipeline(pdf_path, domain, "orchestrator")
        result_b = run_pipeline(pdf_path, domain, "multi_agent")
        compare_results(result_a, result_b)
    else:
        run_pipeline(pdf_path, domain, args.variant)

    print_separator()
    print("✅ Test abgeschlossen!")


if __name__ == "__main__":
    main()
