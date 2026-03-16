"""
Test: Hybrid Agent Prototype – End-to-End mit Vergleichstabelle

Führt den Hybrid-Agent-Prototyp mit math domain aus und vergleicht
das Ergebnis mit dem Standard-Hybrid-Prototyp.

Ausführung:
    python scripts/test_hybrid_agent.py
    python scripts/test_hybrid_agent.py --domain languages
    python scripts/test_hybrid_agent.py --domain economics
"""
import sys
import argparse
import time
from pathlib import Path
sys.path.insert(0, "src")

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)

DOMAIN_PDF_MAP = {
    "math":      ("data/input/math/equations_simple.pdf",      "math"),
    "languages": ("data/input/languages/grammar_exercise.pdf", "languages"),
    "economics": ("data/input/economics/balance_sheet.pdf",    "economics"),
}


def print_separator(title: str = "", char: str = "=", width: int = 70):
    if title:
        print(f"\n{char * width}")
        print(title.center(width))
        print(f"{char * width}")
    else:
        print(f"{char * width}")


def run_hybrid(pdf_path: Path, domain: str) -> dict:
    """Führt Standard-Hybrid-Prototyp aus."""
    from hybrid_prototype.pipeline import get_pipeline
    pipeline = get_pipeline(domain=domain, num_variants=1, max_retries=2)
    start = time.time()
    result = pipeline.process_pdf(pdf_path)
    elapsed = time.time() - start
    if not result["success"]:
        return {"success": False, "error": result.get("error"), "total_time": elapsed}
    stats = result["statistics"]
    graph = stats.get("graph", {})
    return {
        "success": True,
        "total_time": stats.get("total_time", elapsed),
        "valid": graph.get("total_valid", 0),
        "invalid": graph.get("total_invalid", 0),
        "validation_rate": graph.get("validation_rate", 0.0),
        "retries": sum(graph.get("retry_counts", {}).values()),
        "tool_calls": None,  # LangGraph hat keine Tool-Calls
        "hallucinated": None,
    }


def run_hybrid_agent(pdf_path: Path, domain: str) -> dict:
    """Führt Hybrid-Agent-Prototyp aus."""
    from hybrid_agent_prototype.pipeline import get_pipeline
    pipeline = get_pipeline(domain=domain, num_variants=1, max_retries=3)
    start = time.time()
    result = pipeline.process_pdf(pdf_path)
    elapsed = time.time() - start
    if not result["success"]:
        return {"success": False, "error": result.get("error"), "total_time": elapsed}
    stats = result["statistics"]
    agent = stats.get("agent", {})
    return {
        "success": True,
        "total_time": stats.get("total_time", elapsed),
        "valid": agent.get("total_valid", 0),
        "invalid": agent.get("total_invalid", 0),
        "validation_rate": agent.get("validation_rate", 0.0),
        "retries": agent.get("total_retries", 0),
        "tool_calls": agent.get("total_tool_calls", 0),
        "hallucinated": agent.get("hallucinated_calls", 0),
    }


def print_comparison(hybrid: dict, agent: dict):
    print_separator("VERGLEICH: Hybrid vs. Hybrid + Agent")

    w_label = 25
    w_col = 14

    header = f"{'Metrik':<{w_label}} {'Hybrid (LangGraph)':>{w_col}} {'Hybrid + Agent':>{w_col}}"
    print(f"\n{header}")
    print("-" * (w_label + w_col * 2 + 2))

    def row(label, h_val, a_val):
        print(f"{label:<{w_label}} {str(h_val):>{w_col}} {str(a_val):>{w_col}}")

    h_time = f"{hybrid['total_time']:.2f}s" if hybrid.get("success") else "FEHLER"
    a_time = f"{agent['total_time']:.2f}s" if agent.get("success") else "FEHLER"
    row("Verarbeitungszeit", h_time, a_time)

    h_rate = f"{hybrid.get('validation_rate', 0) * 100:.0f}%" if hybrid.get("success") else "N/A"
    a_rate = f"{agent.get('validation_rate', 0) * 100:.0f}%" if agent.get("success") else "N/A"
    row("Validation-Rate", h_rate, a_rate)

    h_valid = hybrid.get("valid", 0) if hybrid.get("success") else "N/A"
    a_valid = agent.get("valid", 0) if agent.get("success") else "N/A"
    row("Valide Varianten", h_valid, a_valid)

    h_retries = hybrid.get("retries", 0) if hybrid.get("success") else "N/A"
    a_retries = agent.get("retries", 0) if agent.get("success") else "N/A"
    row("Retries gesamt", h_retries, a_retries)

    h_calls = "N/A (StateGraph)"
    a_calls = agent.get("tool_calls", 0) if agent.get("success") else "N/A"
    row("Tool-Calls gesamt", h_calls, a_calls)

    h_hall = "N/A"
    a_hall = agent.get("hallucinated", 0) if agent.get("success") else "N/A"
    row("Halluzinierte Calls", h_hall, a_hall)

    print(f"\n{'─' * (w_label + w_col * 2 + 2)}")
    print("\n📌 THESIS-INTERPRETATION:")
    print("   Hybrid (LangGraph): Explizite Retry-Kanten im StateGraph")
    print("   Hybrid + Agent:     Implizite Retry-Logik via LLM-Scratchpad")
    print("   → Beide Varianten nutzen identisches Pre- und Postprocessing")
    print("   → Einziger Unterschied: Phase 2 (LangGraph vs. AgentExecutor)")


def main():
    parser = argparse.ArgumentParser(description="Hybrid Agent End-to-End Test")
    parser.add_argument("--domain", choices=["math", "languages", "economics"],
                        default="math")
    parser.add_argument("--skip-hybrid", action="store_true",
                        help="Standard-Hybrid überspringen (nur Agent testen)")
    args = parser.parse_args()

    pdf_rel, domain = DOMAIN_PDF_MAP[args.domain]
    pdf_path = Config.PROJECT_ROOT / pdf_rel

    if not pdf_path.exists():
        print(f"❌ PDF nicht gefunden: {pdf_path}")
        print(f"   Führe zuerst aus: python scripts/generate_test_pdfs.py")
        sys.exit(1)

    print_separator("HYBRID AGENT PROTOTYPE – END-TO-END TEST")
    print(f"\n   Domain: {args.domain}")
    print(f"   PDF:    {pdf_path}")

    hybrid_result = {"success": False, "total_time": 0.0}
    if not args.skip_hybrid:
        print_separator("Phase A: Standard-Hybrid (LangGraph)", char="-")
        print("⚙️  Läuft...")
        try:
            hybrid_result = run_hybrid(pdf_path, domain)
            if hybrid_result["success"]:
                print(f"✅ Zeit: {hybrid_result['total_time']:.2f}s, "
                      f"Valide: {hybrid_result['valid']}, "
                      f"Rate: {hybrid_result['validation_rate'] * 100:.0f}%")
            else:
                print(f"❌ Fehler: {hybrid_result.get('error')}")
        except Exception as e:
            hybrid_result = {"success": False, "error": str(e), "total_time": 0.0}
            print(f"❌ Ausnahme: {e}")

    print_separator("Phase B: Hybrid + Agent (AgentExecutor)", char="-")
    print("⚙️  Läuft (verbose=True zeigt Tool-Calls)...\n")
    try:
        agent_result = run_hybrid_agent(pdf_path, domain)
        if agent_result["success"]:
            print(f"\n✅ Zeit: {agent_result['total_time']:.2f}s, "
                  f"Valide: {agent_result['valid']}, "
                  f"Rate: {agent_result['validation_rate'] * 100:.0f}%, "
                  f"Tool-Calls: {agent_result['tool_calls']}")
        else:
            print(f"❌ Fehler: {agent_result.get('error')}")
    except Exception as e:
        agent_result = {"success": False, "error": str(e), "total_time": 0.0}
        print(f"❌ Ausnahme: {e}")

    if not args.skip_hybrid:
        print_comparison(hybrid_result, agent_result)

    print_separator()
    print("✅ Test abgeschlossen!")


if __name__ == "__main__":
    main()
