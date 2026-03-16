"""
Test: Variante A — Orchestrierungsagent

Testet den Orchestrierungsagenten mit einem einzelnen Math-Segment.
Zeigt die Tool-Call-Sequenz und den Unterschied zum deterministischen
LangChain-Prototyp.

Ausführung:
    python scripts/test_agent_orchestrator.py
"""
import sys
import json
sys.path.insert(0, "src")

from common.logger import setup_logger
from langchain_agent_prototype.orchestrator.agent import run_orchestrator

logger = setup_logger(__name__)


TEST_SEGMENT = {
    "type": "task",
    "text": "Aufgabe 1: Löse die Gleichung: 2x + 5 = 13",
}


def print_separator(title: str = "", char: str = "=", width: int = 70):
    if title:
        print(f"\n{char * width}")
        print(title.center(width))
        print(f"{char * width}")
    else:
        print(f"{char * width}")


def main():
    print_separator("VARIANTE A: ORCHESTRIERUNGSAGENT TEST")

    print(f"\n📝 Test-Segment:")
    print(f"   Type: {TEST_SEGMENT['type']}")
    print(f"   Text: {TEST_SEGMENT['text']}")

    print_separator("Agenten-Ausführung", char="-")
    print("⚙️  AgentExecutor läuft (verbose=True zeigt Tool-Calls)...\n")

    result = run_orchestrator(
        segment=TEST_SEGMENT,
        domain_hint="mathematics",
        max_retries=3,
    )

    print_separator("Ergebnis", char="-")

    print(f"\n📊 ZUSAMMENFASSUNG:")
    print(f"   Original:  {result['original']}")
    print(f"   Variante:  {result['variant'] or '(keine)'}")
    print(f"   Domain:    {result['domain']}")
    print(f"   Valide:    {'✅ JA' if result['is_valid'] else '❌ NEIN'}")
    print(f"   Versuche:  {result['attempts']}")
    print(f"   Erfolg:    {'✅ JA' if result['success'] else '❌ NEIN'}")

    print(f"\n🔧 TOOL-CALL-SEQUENZ ({len(result['tool_calls'])} Aufrufe):")
    tool_counts = {}
    for i, call in enumerate(result["tool_calls"], 1):
        tool = call["tool"]
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
        print(f"   {i}. {tool}")
        print(f"      Input-Länge: {call['input_len']} Zeichen")
        print(f"      Output:      {call['output_preview']!r}")

    print(f"\n📈 TOOL-STATISTIK:")
    for tool, count in tool_counts.items():
        print(f"   {tool}: {count}x aufgerufen")

    print(f"\n🔄 VERGLEICH MIT DETERMINISTISCHEM LANGCHAIN-PROTOTYP:")
    print(f"   LangChain (Chains): Sequenz ist immer identisch")
    print(f"                       classify → rewrite → validate")
    print(f"   Variante A (Agent): LLM entscheidet autonom die Reihenfolge")
    unique_tools = list(dict.fromkeys(c["tool"] for c in result["tool_calls"]))
    print(f"                       Tatsächliche Sequenz: {' → '.join(unique_tools)}")
    total_classify = tool_counts.get("classify_segment", 0)
    total_rewrite = tool_counts.get("rewrite_segment", 0)
    total_validate = tool_counts.get("validate_variant", 0)
    if total_rewrite > 1:
        print(f"                       ✓ Agent hat {total_rewrite}x rewritten (Retry-Verhalten)")
    else:
        print(f"                       Kein Retry nötig — erste Variante valide")

    print_separator()
    if result["success"]:
        print("✅ Test abgeschlossen — Orchestrierungsagent funktionsfähig!")
    else:
        print("⚠️  Test abgeschlossen — keine valide Variante generiert")
        print("   (Prüfe ob LLM-Provider korrekt konfiguriert)")


if __name__ == "__main__":
    main()
