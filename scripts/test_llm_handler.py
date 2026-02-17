"""
Testet LLM Handler (OpenAI oder BFH)
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from common.llm_handler import get_llm_handler, reset_llm_handler

def test_basic_completion():
    """Test 1: Einfache Completion"""
    print("🧪 Test 1: Einfache Completion\n")
    
    llm = get_llm_handler()
    
    result = llm.generate(
        prompt="Was ist 2+2? Antworte nur mit der Zahl.",
        system_prompt="Du bist ein hilfreicher Assistent."
    )
    
    if result['success']:
        print(f"✅ Response: {result['text']}")
        print(f"   Provider: {result['provider']}")
        print(f"   Model: {result['model']}")
        print(f"   Tokens: {result['tokens']['total']}")
        print(f"   Zeit: {result['processing_time']:.2f}s\n")
    else:
        print(f"❌ Fehler: {result['error']}\n")

def test_classification():
    """Test 2: Klassifizierung"""
    print("🧪 Test 2: Text-Klassifizierung\n")
    
    llm = get_llm_handler()
    
    result = llm.generate(
        prompt="Klassifiziere diesen Text in eine Kategorie (Mathematik, Sprachwissenschaft, Wirtschaft, Theorie): 'Eine Gleichung mit 2x + 5 = 13'",
        system_prompt="Du bist ein Experte für Text-Klassifizierung."
    )
    
    if result['success']:
        print(f"✅ Klassifizierung: {result['text']}\n")
    else:
        print(f"❌ Fehler: {result['error']}\n")

def test_structured_output():
    """Test 3: Strukturierte Ausgabe (JSON)"""
    print("🧪 Test 3: Strukturierte Ausgabe (JSON)\n")
    
    llm = get_llm_handler()
    
    result = llm.generate_structured(
        prompt="Analysiere den Satz: 'Das Haus steht auf dem Hügel.' Extrahiere Subjekt, Prädikat und Objekt.",
        response_format={
            "subjekt": "string",
            "praedikat": "string", 
            "objekt": "string"
        },
        system_prompt="Du bist ein Grammatik-Experte."
    )
    
    if result['success']:
        print(f"✅ Strukturierte Daten:")
        print(f"   {result['parsed_data']}\n")
    else:
        print(f"❌ Fehler: {result['error']}")
        if result.get('raw_text'):
            print(f"   Raw: {result['raw_text']}\n")

def test_paraphrase():
    """Test 4: Paraphrasierung"""
    print("🧪 Test 4: Paraphrasierung\n")
    
    llm = get_llm_handler()
    
    original = "Das Haus steht auf dem Hügel."
    
    result = llm.generate(
        prompt=f"Formuliere diesen Satz um, behalte aber die Bedeutung: '{original}'",
        system_prompt="Du bist ein Sprach-Experte. Antworte nur mit dem umformulierten Satz, ohne Erklärung."
    )
    
    if result['success']:
        print(f"Original:   {original}")
        print(f"Paraphrase: {result['text']}\n")
    else:
        print(f"❌ Fehler: {result['error']}\n")

def test_math_variation():
    """Test 5: Mathematik-Variation"""
    print("🧪 Test 5: Mathematik-Variation\n")
    
    llm = get_llm_handler()
    
    result = llm.generate(
        prompt="Variiere diese Gleichung (ändere die Zahlen, behalte die Struktur): '2x + 5 = 13'",
        system_prompt="Du bist ein Mathematik-Lehrer. Antworte nur mit der neuen Gleichung."
    )
    
    if result['success']:
        print(f"Original:  2x + 5 = 13")
        print(f"Variiert:  {result['text']}\n")
    else:
        print(f"❌ Fehler: {result['error']}\n")

def test_batch():
    """Test 6: Batch-Verarbeitung"""
    print("🧪 Test 6: Batch-Verarbeitung\n")
    
    llm = get_llm_handler()
    
    prompts = [
        "Was ist die Hauptstadt von Frankreich?",
        "Was ist 10 + 15?",
        "Nenne ein Synonym für 'schnell'."
    ]
    
    results = llm.batch_generate(prompts, show_progress=False)
    
    for idx, result in enumerate(results, 1):
        if result['success']:
            print(f"✅ Prompt {idx}: {result['text']}")
        else:
            print(f"❌ Prompt {idx}: {result['error']}")
    print()

if __name__ == '__main__':
    print("="*60)
    print("LLM HANDLER TESTS")
    print("="*60 + "\n")
    
    # Zeige welcher Provider aktiv ist
    llm = get_llm_handler()
    print(f"🔍 Aktiver Provider: {llm.provider.upper()}")
    print(f"📦 Model: {llm.model}")
    print(f"🌡️  Temperature: {llm.temperature}\n")
    print("="*60 + "\n")
    
    # Tests
    test_basic_completion()
    test_classification()
    test_structured_output()
    test_paraphrase()
    test_math_variation()
    test_batch()
    
    print("="*60)
    print("✅ Alle Tests abgeschlossen!")
    print("\n💡 Provider wechseln:")
    print("   - In .env.dev: LLM_PROVIDER=openai oder LLM_PROVIDER=bfh")
    print("="*60 + "\n")