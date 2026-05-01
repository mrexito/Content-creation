"""
Objektiver Vergleich der OCR-Ergebnisse von Mistral und Tesseract
Misst Geschwindigkeit UND Genauigkeit durch Vergleich mit Ground Truth
"""
import json
import time
from pathlib import Path
import sys
from difflib import SequenceMatcher
from io import StringIO
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)

# Global für Report-Capture
_report_buffer = StringIO()

# Auf 11 Zeichen rechtsgepolsterte Tool-Labels (für ausgerichtete Konsolenausgabe)
_TOOL_LABEL = {
    'mistral': 'Mistral:   ',
    'tesseract': 'Tesseract: ',
}

def log_and_print(text: str):
    """Schreibt sowohl in Console als auch in Report-Buffer"""
    print(text)
    _report_buffer.write(text + '\n')

def load_results(tool: str, domain: str, filename: str) -> Optional[dict]:
    """Lädt Ergebnisse eines OCR-Tools"""
    path = Config.DATA_PARSED_PATH / tool / domain / f"{filename}.json"
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_ground_truth(domain: str, filename: str) -> Optional[str]:
    """Lädt Ground Truth Text (falls vorhanden)"""
    path = Config.DATA_INPUT_PATH / domain / f"{filename}_ground_truth.txt"
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def calculate_similarity(text1: str, text2: str) -> float:
    """Berechnet Textähnlichkeit (0-1)"""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1, text2).ratio()

def normalize_text(text: str) -> str:
    """Normalisiert Text für Vergleich (lowercase, whitespace)"""
    import re
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def calculate_accuracy(ocr_text: str, ground_truth: str) -> Optional[dict]:
    """Berechnet verschiedene Genauigkeitsmetriken"""
    if not ground_truth:
        return None

    ocr_norm = normalize_text(ocr_text)
    gt_norm = normalize_text(ground_truth)

    similarity = calculate_similarity(ocr_norm, gt_norm)

    gt_chars = len(gt_norm)
    ocr_chars = len(ocr_norm)
    char_diff = abs(gt_chars - ocr_chars)
    char_accuracy = 1 - (char_diff / gt_chars) if gt_chars > 0 else 0

    gt_words = set(gt_norm.split())
    ocr_words = set(ocr_norm.split())
    common_words = gt_words.intersection(ocr_words)
    word_accuracy = len(common_words) / len(gt_words) if len(gt_words) > 0 else 0

    return {
        'similarity': similarity,
        'char_accuracy': char_accuracy,
        'word_accuracy': word_accuracy,
        'gt_chars': gt_chars,
        'ocr_chars': ocr_chars,
        'gt_words': len(gt_words),
        'ocr_words': len(ocr_words),
        'common_words': len(common_words)
    }


# ===== Markdown-Report-Helper =====

def _md_tool_stats(data: dict) -> list:
    success_rate = (data['success'] / data['total']) * 100
    avg_time = data['total_time'] / data['total']
    md = [
        f"- **Erfolgsrate:** {data['success']}/{data['total']} ({success_rate:.1f}%)\n",
        f"- **Ø Zeit:** {avg_time:.2f}s/PDF\n",
        f"- **Gesamt-Zeit:** {data['total_time']:.2f}s\n",
    ]
    if data['similarities']:
        avg_sim = sum(data['similarities']) / len(data['similarities'])
        avg_word = sum(data['word_accuracies']) / len(data['word_accuracies'])
        md.append(f"- **Ø Ähnlichkeit:** {avg_sim*100:.1f}%\n")
        md.append(f"- **Ø Wort-Genauigkeit:** {avg_word*100:.1f}%\n")
    return md


def _md_summary_section(comparison: dict) -> list:
    md = ["## 📊 Zusammenfassung\n"]
    for tool in ['mistral', 'tesseract']:
        data = comparison[tool]
        md.append(f"### {tool.upper()}\n")
        if data['total'] > 0:
            md.extend(_md_tool_stats(data))
        else:
            md.append("- **Keine Daten vorhanden**\n")
            md.append(f"- Führe zuerst den Test aus: `python research/ocr_comparison/test_{tool}_ocr.py`\n")
        md.append("\n")
    return md


def _md_tool_detail(result: dict, key: str, label: str) -> list:
    tool_data = result.get(key)
    if not tool_data or not tool_data.get('accuracy'):
        return []
    acc = tool_data['accuracy']
    return [
        f"**{label}:**\n",
        f"- Zeit: {tool_data['time']:.2f}s\n",
        f"- Ähnlichkeit: {acc['similarity']*100:.1f}%\n",
        f"- Wort-Genauigkeit: {acc['word_accuracy']*100:.1f}%\n\n",
    ]


def _md_detailed_section(detailed_results: list) -> list:
    if not detailed_results:
        return [
            "## ⚠️ Keine Ergebnisse\n",
            "Führe zuerst die OCR-Tests aus:\n",
            "```bash\n",
            "python research/ocr_comparison/test_mistral_ocr.py\n",
            "python research/ocr_comparison/test_tesseract.py\n",
            "```\n",
        ]
    md = ["## 📋 Detaillierte Ergebnisse\n"]
    for result in detailed_results:
        md.append(f"### {result['file']} ({result['domain']})\n")
        if not result['has_ground_truth']:
            md.append("⚠️ Keine Ground Truth\n\n")
            continue
        md.append("✓ Ground Truth vorhanden\n\n")
        md.extend(_md_tool_detail(result, 'mistral', 'Mistral'))
        md.extend(_md_tool_detail(result, 'tesseract', 'Tesseract'))
    return md


def _md_speed_block(mistral_avg_time: float, tesseract_avg_time: float) -> list:
    if tesseract_avg_time < mistral_avg_time:
        speedup = mistral_avg_time / tesseract_avg_time
        return [
            "### ⚡ Geschwindigkeit\n",
            f"Tesseract ist **{speedup:.1f}x schneller** ({tesseract_avg_time:.2f}s vs {mistral_avg_time:.2f}s)\n\n",
        ]
    speedup = tesseract_avg_time / mistral_avg_time
    return [
        "### ⚡ Geschwindigkeit\n",
        f"Mistral ist **{speedup:.1f}x schneller** ({mistral_avg_time:.2f}s vs {tesseract_avg_time:.2f}s)\n\n",
    ]


def _md_accuracy_block(mistral_data: dict, tesseract_data: dict) -> list:
    if not (mistral_data['similarities'] and tesseract_data['similarities']):
        return []
    mistral_avg = sum(mistral_data['similarities']) / len(mistral_data['similarities'])
    tesseract_avg = sum(tesseract_data['similarities']) / len(tesseract_data['similarities'])
    md = [
        "### 📏 Genauigkeit\n",
        f"- Mistral: {mistral_avg*100:.1f}%\n",
        f"- Tesseract: {tesseract_avg*100:.1f}%\n",
    ]
    if mistral_avg > tesseract_avg:
        diff = mistral_avg - tesseract_avg
        md.append(f"\nMistral ist **{diff*100:.1f} Prozentpunkte genauer**\n\n")
    else:
        diff = tesseract_avg - mistral_avg
        md.append(f"\nTesseract ist **{diff*100:.1f} Prozentpunkte genauer**\n\n")
    return md


def _md_fazit_table(mistral_avg_time: float, tesseract_avg_time: float,
                    mistral_data: dict, tesseract_data: dict) -> list:
    md = [
        "## 📋 Fazit\n",
        "| Kriterium | Mistral | Tesseract |\n",
        "|-----------|---------|----------|\n",
        f"| Geschwindigkeit | {mistral_avg_time:.2f}s | {tesseract_avg_time:.2f}s |\n",
    ]
    if mistral_data['similarities'] and tesseract_data['similarities']:
        mistral_avg = sum(mistral_data['similarities']) / len(mistral_data['similarities'])
        tesseract_avg = sum(tesseract_data['similarities']) / len(tesseract_data['similarities'])
        md.append(f"| Genauigkeit | {mistral_avg*100:.1f}% | {tesseract_avg*100:.1f}% |\n")
    md.extend([
        "| Kosten | Kostenpflichtig | Kostenlos |\n",
        "| Offline | Nein | Ja |\n",
        "| Self-hosted | Nein | Ja |\n",
    ])
    return md


def _md_comparison_section(comparison: dict) -> list:
    mistral_data = comparison['mistral']
    tesseract_data = comparison['tesseract']
    if mistral_data['total'] == 0 or tesseract_data['total'] == 0:
        return []

    mistral_avg_time = mistral_data['total_time'] / mistral_data['total']
    tesseract_avg_time = tesseract_data['total_time'] / tesseract_data['total']

    md = ["## 🔍 Vergleich\n"]
    md.extend(_md_speed_block(mistral_avg_time, tesseract_avg_time))
    md.extend(_md_accuracy_block(mistral_data, tesseract_data))
    md.extend(_md_fazit_table(mistral_avg_time, tesseract_avg_time, mistral_data, tesseract_data))
    return md


def generate_markdown_report(output_path: Path, comparison: dict, detailed_results: list):
    """Generiert einen Markdown-Report"""
    md = [
        "# OCR-Vergleich: Mistral vs. Tesseract\n",
        f"**Datum:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n",
    ]
    md.extend(_md_summary_section(comparison))
    md.extend(_md_detailed_section(detailed_results))
    md.extend(_md_comparison_section(comparison))
    output_path.write_text(''.join(md), encoding='utf-8')


# ===== compare_all-Helper =====

def _check_data_availability() -> bool:
    """Prüft, ob OCR-Ergebnisse existieren. Gibt False zurück, wenn nichts da ist."""
    has_mistral = any((Config.DATA_PARSED_PATH / 'mistral').rglob('*.json'))
    has_tesseract = any((Config.DATA_PARSED_PATH / 'tesseract').rglob('*.json'))

    if not has_mistral and not has_tesseract:
        log_and_print("\n❌ FEHLER: Keine OCR-Ergebnisse gefunden!\n")
        log_and_print("Führe zuerst die Tests aus:")
        log_and_print("  python research/ocr_comparison/test_mistral_ocr.py")
        log_and_print("  python research/ocr_comparison/test_tesseract.py\n")
        return False

    if not has_mistral:
        log_and_print("\n⚠️  WARNUNG: Keine Mistral-Ergebnisse gefunden")
        log_and_print("   Führe aus: python research/ocr_comparison/test_mistral_ocr.py\n")

    if not has_tesseract:
        log_and_print("\n⚠️  WARNUNG: Keine Tesseract-Ergebnisse gefunden")
        log_and_print("   Führe aus: python research/ocr_comparison/test_tesseract.py\n")

    return True


def _new_tool_stats() -> dict:
    return {
        'total_time': 0,
        'success': 0,
        'total': 0,
        'total_chars': 0,
        'similarities': [],
        'char_accuracies': [],
        'word_accuracies': [],
    }


def _log_accuracy_block(label: str, processing_time: float, text_len: int, accuracy: dict):
    log_and_print(f"\n   ✅ {label.rstrip()}")
    log_and_print(f"      Zeit:            {processing_time:.2f}s")
    log_and_print(f"      Zeichen:         {text_len:,}")
    log_and_print(f"      Ähnlichkeit:     {accuracy['similarity']*100:.1f}%")
    log_and_print(f"      Wort-Genauigkeit: {accuracy['word_accuracy']*100:.1f}%")


def _process_tool_for_pdf(tool: str, domain: str, stem: str,
                           ground_truth: Optional[str],
                           comparison: dict, result_entry: dict):
    """Lädt und verarbeitet das OCR-Ergebnis eines Tools für eine PDF."""
    label = _TOOL_LABEL[tool]
    raw = load_results(tool, domain, stem)
    if not raw:
        log_and_print(f"   ⚠️  {label} Keine Daten")
        return

    stats = comparison[tool]
    stats['total'] += 1
    stats['total_time'] += raw.get('processing_time', 0)

    if not raw.get('success'):
        result_entry[tool] = {'success': False}
        log_and_print(f"   ❌ {label} Fehler")
        return

    stats['success'] += 1
    text = raw.get('extracted_text', '')
    text_len = len(text)
    stats['total_chars'] += text_len
    processing_time = raw['processing_time']

    result_entry[tool] = {'time': processing_time, 'chars': text_len, 'success': True}

    if not ground_truth:
        log_and_print(f"   ✅ {label} {processing_time:.2f}s ({text_len:,} Zeichen)")
        return

    accuracy = calculate_accuracy(text, ground_truth)
    if not accuracy:
        return

    result_entry[tool]['accuracy'] = accuracy
    stats['similarities'].append(accuracy['similarity'])
    stats['char_accuracies'].append(accuracy['char_accuracy'])
    stats['word_accuracies'].append(accuracy['word_accuracy'])
    _log_accuracy_block(label, processing_time, text_len, accuracy)


def _process_pdf(domain: str, pdf_file: Path, comparison: dict, detailed_results: list):
    stem = pdf_file.stem
    log_and_print(f"\n📄 {pdf_file.name}")
    log_and_print(f"   {'─'*60}")

    ground_truth = load_ground_truth(domain, stem)
    if ground_truth:
        log_and_print(f"   ✓ Ground Truth vorhanden ({len(ground_truth)} Zeichen)")
    else:
        log_and_print("   ⚠️  Keine Ground Truth (nur Geschwindigkeit messbar)")

    result_entry = {
        'file': pdf_file.name,
        'domain': domain,
        'has_ground_truth': ground_truth is not None,
        'mistral': None,
        'tesseract': None,
    }

    _process_tool_for_pdf('mistral', domain, stem, ground_truth, comparison, result_entry)
    _process_tool_for_pdf('tesseract', domain, stem, ground_truth, comparison, result_entry)

    detailed_results.append(result_entry)


def _print_tool_summary(tool: str, data: dict):
    log_and_print(f"{tool.upper()}:")
    if data['total'] == 0:
        log_and_print("  Keine Daten vorhanden")
        log_and_print("")
        return

    log_and_print(f"  Erfolgsrate:   {data['success']}/{data['total']} ({data['success']/data['total']*100:.1f}%)")
    avg_time = data['total_time'] / data['total']
    log_and_print(f"  Ø Zeit:        {avg_time:.2f}s/PDF")
    log_and_print(f"  Gesamt-Zeit:   {data['total_time']:.2f}s")

    if data['similarities']:
        avg_sim = sum(data['similarities']) / len(data['similarities'])
        avg_word = sum(data['word_accuracies']) / len(data['word_accuracies'])
        log_and_print(f"  Ø Ähnlichkeit: {avg_sim*100:.1f}% (n={len(data['similarities'])})")
        log_and_print(f"  Ø Wort-Acc:    {avg_word*100:.1f}%")
    else:
        log_and_print("  Genauigkeit:   Nicht messbar (keine Ground Truth)")

    log_and_print("")


def _print_speed_comparison(mistral_avg: float, tesseract_avg: float):
    log_and_print("⚡ GESCHWINDIGKEIT:")
    if abs(mistral_avg - tesseract_avg) < 0.5:
        log_and_print(f"   → Vergleichbar (~{mistral_avg:.1f}s vs ~{tesseract_avg:.1f}s)")
    elif tesseract_avg < mistral_avg:
        speedup = mistral_avg / tesseract_avg
        log_and_print(f"   → Tesseract schneller: {tesseract_avg:.2f}s vs {mistral_avg:.2f}s ({speedup:.1f}x)")
    else:
        speedup = tesseract_avg / mistral_avg
        log_and_print(f"   → Mistral schneller: {mistral_avg:.2f}s vs {tesseract_avg:.2f}s ({speedup:.1f}x)")


def _print_accuracy_comparison(mistral_data: dict, tesseract_data: dict) -> Optional[tuple]:
    """Gibt (mistral_avg_acc, tesseract_avg_acc) zurück oder None, falls nicht messbar."""
    log_and_print("\n📏 GENAUIGKEIT:")
    if not (mistral_data['similarities'] and tesseract_data['similarities']):
        log_and_print("   → Nicht messbar (Ground Truth fehlt)")
        log_and_print("   → Tipp: Erstelle <filename>_ground_truth.txt Dateien")
        return None

    mistral_avg = sum(mistral_data['similarities']) / len(mistral_data['similarities'])
    tesseract_avg = sum(tesseract_data['similarities']) / len(tesseract_data['similarities'])
    diff = abs(mistral_avg - tesseract_avg)

    if diff < 0.05:
        log_and_print(f"   → Vergleichbar ({mistral_avg*100:.1f}% vs {tesseract_avg*100:.1f}%)")
    elif mistral_avg > tesseract_avg:
        log_and_print(f"   → Mistral genauer: {mistral_avg*100:.1f}% vs {tesseract_avg*100:.1f}%")
        log_and_print(f"   → Differenz: {diff*100:.1f} Prozentpunkte")
    else:
        log_and_print(f"   → Tesseract genauer: {tesseract_avg*100:.1f}% vs {mistral_avg*100:.1f}%")
        log_and_print(f"   → Differenz: {diff*100:.1f} Prozentpunkte")

    return mistral_avg, tesseract_avg


def _print_static_comparison_blocks():
    log_and_print("\n💰 KOSTEN:")
    log_and_print("   Mistral:    API-basiert (kostenpflichtig)")
    log_and_print("   Tesseract:  Open Source (kostenlos)")

    log_and_print("\n🌐 DEPLOYMENT:")
    log_and_print("   Mistral:    Externe API, Internet erforderlich")
    log_and_print("   Tesseract:  Selbst hostbar, offline nutzbar")

    log_and_print("\n🔧 WARTUNG:")
    log_and_print("   Mistral:    Managed Service, keine lokale Wartung")
    log_and_print("   Tesseract:  Selbst gewartet, volle Kontrolle")


def _print_fazit(mistral_avg_time: float, tesseract_avg_time: float,
                 accuracy_pair: Optional[tuple]):
    log_and_print("\n" + "="*70)
    log_and_print("📋 FAZIT")
    log_and_print("="*70 + "\n")
    log_and_print("Die Wahl des OCR-Tools hängt von den Prioritäten ab:\n")

    if tesseract_avg_time < mistral_avg_time * 0.5:
        log_and_print("• Tesseract ist deutlich schneller")
    elif mistral_avg_time < tesseract_avg_time * 0.5:
        log_and_print("• Mistral ist deutlich schneller")
    else:
        log_and_print("• Geschwindigkeit ist vergleichbar")

    if accuracy_pair:
        mistral_avg_acc, tesseract_avg_acc = accuracy_pair
        if abs(mistral_avg_acc - tesseract_avg_acc) < 0.05:
            log_and_print("• Genauigkeit ist vergleichbar")
        elif mistral_avg_acc > tesseract_avg_acc:
            log_and_print("• Mistral ist genauer")
        else:
            log_and_print("• Tesseract ist genauer")

    log_and_print("• Tesseract ist kostenlos, Mistral kostenpflichtig")
    log_and_print("• Tesseract ist offline nutzbar, Mistral benötigt Internet")

    log_and_print("\nFür Produktivsysteme mit Kostenrestriktionen → Tesseract")
    log_and_print("Für höchste Qualität bei verfügbarem Budget → Mistral")


def _print_direct_comparison(comparison: dict):
    log_and_print("="*70)
    log_and_print("🔍 DIREKTER VERGLEICH")
    log_and_print("="*70 + "\n")

    mistral_data = comparison['mistral']
    tesseract_data = comparison['tesseract']

    if mistral_data['total'] == 0 or tesseract_data['total'] == 0:
        return

    mistral_avg_time = mistral_data['total_time'] / mistral_data['total']
    tesseract_avg_time = tesseract_data['total_time'] / tesseract_data['total']

    _print_speed_comparison(mistral_avg_time, tesseract_avg_time)
    accuracy_pair = _print_accuracy_comparison(mistral_data, tesseract_data)
    _print_static_comparison_blocks()
    _print_fazit(mistral_avg_time, tesseract_avg_time, accuracy_pair)


def _save_outputs(comparison: dict, detailed_results: list):
    output_json = Config.DATA_PARSED_PATH / 'comparison_results.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': comparison,
            'detailed': detailed_results,
            'metadata': {
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'tools_compared': ['mistral', 'tesseract'],
                'domains': ['math', 'languages', 'economics']
            }
        }, f, indent=2, ensure_ascii=False)
    log_and_print(f"📊 JSON-Daten gespeichert: {output_json}")

    output_md = Config.DATA_PARSED_PATH / 'comparison_report.md'
    generate_markdown_report(output_md, comparison, detailed_results)
    log_and_print(f"📄 Markdown-Report: {output_md}")

    output_txt = Config.DATA_PARSED_PATH / 'comparison_report.txt'
    output_txt.write_text(_report_buffer.getvalue(), encoding='utf-8')
    log_and_print(f"📝 Text-Report: {output_txt}")


def compare_all():
    """Vergleicht alle Ergebnisse"""
    global _report_buffer
    _report_buffer = StringIO()

    if not _check_data_availability():
        return

    log_and_print("\n" + "="*70)
    log_and_print("OCR-VERGLEICH: Mistral vs. Tesseract")
    log_and_print("Objektive Messung: Geschwindigkeit & Genauigkeit")
    log_and_print("="*70 + "\n")

    comparison = {'mistral': _new_tool_stats(), 'tesseract': _new_tool_stats()}
    detailed_results = []

    log_and_print("ℹ️  Ground Truth:")
    log_and_print("   Um Genauigkeit zu messen, können Ground Truth Dateien erstellt werden:")
    log_and_print("   Format: <filename>_ground_truth.txt im gleichen Ordner wie das PDF")
    log_and_print("   Beispiel: equations_simple_ground_truth.txt\n")

    for domain in ['math', 'languages', 'economics']:
        log_and_print(f"\n{'─'*70}")
        log_and_print(f"📁 Domäne: {domain.upper()}")
        log_and_print(f"{'─'*70}")

        domain_path = Config.DATA_INPUT_PATH / domain
        if not domain_path.exists():
            continue

        for pdf_file in domain_path.glob('*.pdf'):
            _process_pdf(domain, pdf_file, comparison, detailed_results)

    log_and_print("\n" + "="*70)
    log_and_print("📊 GESAMT-ZUSAMMENFASSUNG")
    log_and_print("="*70 + "\n")
    for tool in ['mistral', 'tesseract']:
        _print_tool_summary(tool, comparison[tool])

    _print_direct_comparison(comparison)

    log_and_print("\n" + "="*70 + "\n")

    _save_outputs(comparison, detailed_results)
    log_and_print("\n✅ Alle Reports gespeichert!\n")


if __name__ == '__main__':
    compare_all()
