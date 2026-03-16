"""
Test: Variante B — Multi-Agent Pipeline

Testet die Multi-Agent-Pipeline mit demselben Segment wie test_agent_orchestrator.
Zeigt dass ohne Retry-Koordinator die Pipeline bei invalider Variante
das Ergebnis trotzdem zurückgibt — und dokumentiert die strukturelle Degenerierung
zur Pipeline.

Ausführung:
    python scripts/test_agent_multi.py
"""
import sys
import json
sys.path.insert(0, "src")

from common.logger import setup_logger
from langchain_agent_prototype.multi_agent.pipeline import run_multi_agent_pipeline

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
    print_separator("VARIANTE B: MULTI-AGENT PIPELINE TEST")

    print(f"\n📝 Test-Segment:")
    print(f"   Type: {TEST_SEGMENT['type']}")
    print(f"   Text: {TEST_SEGMENT['text']}")

    print(f"\n⚠️  THESIS-HINWEIS:")
    print(f"   Variante B verwendet 3 Agenten mit je genau 1 Tool.")
    print(f"   Ein Agent mit 1 Tool hat keine Wahlfreiheit → degeneriert zur Pipeline.")
    print(f"   Kein Retry-Koordinator → invalide Variante wird nicht automatisch wiederholt.")

    print_separator("Agenten-Ausführung (3 sequenzielle Agenten)", char="-")
    print("⚙️  Classifier → Rewriter → Validator (verbose=True)...\n")

    result = run_multi_agent_pipeline(
        segment=TEST_SEGMENT,
        max_retries=3,  # wird ignoriert — kein Retry-Koordinator
    )

    print_separator("Ergebnis", char="-")

    print(f"\n📊 ZUSAMMENFASSUNG:")
    print(f"   Original:  {result['original']}")
    print(f"   Variante:  {result['variant'] or '(keine)'}")
    print(f"   Domain:    {result['domain']}")
    print(f"   Valide:    {'✅ JA' if result['is_valid'] else '❌ NEIN'}")
    print(f"   Versuche:  {result['attempts']} (immer 1 — kein Retry)")
    print(f"   Erfolg:    {'✅ JA' if result['success'] else '❌ NEIN'}")

    print(f"\n🔧 TOOL-CALL-SEQUENZ ({len(result['tool_calls'])} Aufrufe):")
    for i, call in enumerate(result["tool_calls"], 1):
        agent_label = f"[{call.get('agent', '?')}]"
        print(f"   {i}. {agent_label} {call['tool']}")
        print(f"      Input-Länge: {call['input_len']} Zeichen")
        print(f"      Output:      {call['output_preview']!r}")

    print(f"\n📌 STRUKTURELLE ANALYSE:")
    tools_used = [c["tool"] for c in result["tool_calls"]]
    rewrite_count = tools_used.count("rewrite_segment")
    print(f"   classify_segment aufgerufen: {tools_used.count('classify_segment')}x")
    print(f"   rewrite_segment aufgerufen:  {rewrite_count}x")
    print(f"   validate_variant aufgerufen: {tools_used.count('validate_variant')}x")

    print(f"\n   → Immer genau 1 Rewriting-Versuch, unabhängig vom Validierungsergebnis")
    if not result["is_valid"]:
        print(f"   → Variante NICHT valide — trotzdem kein Retry (kein Koordinator)")
        print(f"   → Dies illustriert die Einschränkung von Variante B:")
        print(f"      3 Einzelagenten ohne übergeordnete Steuerung ≠ intelligente Pipeline")
    else:
        print(f"   → Variante valide — Retry nicht nötig")

    print(f"\n🔄 VERGLEICH VARIANTE A vs. B:")
    print(f"   Variante A (Orchestrator): LLM kann Retry auslösen, Domain adaptieren")
    print(f"   Variante B (Multi-Agent):  Feste 3-Schritt-Sequenz, kein Retry möglich")
    print(f"   → Variante B ist strukturell äquivalent zu langchain_prototype/pipeline.py")

    print_separator()
    print("✅ Test abgeschlossen — Multi-Agent-Pipeline funktionsfähig!")
    print("   (Strukturelle Einschränkungen sind beabsichtigt — siehe ARCHITECTURE.md)")


if __name__ == "__main__":
    main()
