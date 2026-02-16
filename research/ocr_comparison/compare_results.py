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

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)

# Global für Report-Capture
_report_buffer = StringIO()

def log_and_print(text: str):
    """Schreibt sowohl in Console als auch in Report-Buffer"""
    print(text)
    _report_buffer.write(text + '\n')

def load_results(tool: str, domain: str, filename: str) -> dict:
    """Lädt Ergebnisse eines OCR-Tools"""
    path = Config.DATA_PARSED_PATH / tool / domain / f"{filename}.json"
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_ground_truth(domain: str, filename: str) -> str:
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

def calculate_accuracy(ocr_text: str, ground_truth: str) -> dict:
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

def generate_markdown_report(output_path: Path, comparison: dict, detailed_results: list):
    """Generiert einen Markdown-Report"""
    
    md = []
    md.append("# OCR-Vergleich: Mistral vs. Tesseract\n")
    md.append(f"**Datum:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    md.append("---\n")
    
    # Zusammenfassung
    md.append("## 📊 Zusammenfassung\n")
    
    for tool in ['mistral', 'tesseract']:
        data = comparison[tool]
        md.append(f"### {tool.upper()}\n")
        
        # Safe Division
        if data['total'] > 0:
            success_rate = (data['success'] / data['total']) * 100
            avg_time = data['total_time'] / data['total']
            
            md.append(f"- **Erfolgsrate:** {data['success']}/{data['total']} ({success_rate:.1f}%)\n")
            md.append(f"- **Ø Zeit:** {avg_time:.2f}s/PDF\n")
            md.append(f"- **Gesamt-Zeit:** {data['total_time']:.2f}s\n")
            
            if data['similarities']:
                avg_sim = sum(data['similarities']) / len(data['similarities'])
                avg_word = sum(data['word_accuracies']) / len(data['word_accuracies'])
                md.append(f"- **Ø Ähnlichkeit:** {avg_sim*100:.1f}%\n")
                md.append(f"- **Ø Wort-Genauigkeit:** {avg_word*100:.1f}%\n")
        else:
            md.append(f"- **Keine Daten vorhanden**\n")
            md.append(f"- Führe zuerst den Test aus: `python research/ocr_comparison/test_{tool}_ocr.py`\n")
        
        md.append("\n")
    
    # Detaillierte Ergebnisse
    if detailed_results:
        md.append("## 📋 Detaillierte Ergebnisse\n")
        
        for result in detailed_results:
            md.append(f"### {result['file']} ({result['domain']})\n")
            
            if result['has_ground_truth']:
                md.append("✓ Ground Truth vorhanden\n\n")
                
                if result.get('mistral') and result['mistral'].get('accuracy'):
                    acc = result['mistral']['accuracy']
                    md.append(f"**Mistral:**\n")
                    md.append(f"- Zeit: {result['mistral']['time']:.2f}s\n")
                    md.append(f"- Ähnlichkeit: {acc['similarity']*100:.1f}%\n")
                    md.append(f"- Wort-Genauigkeit: {acc['word_accuracy']*100:.1f}%\n\n")
                
                if result.get('tesseract') and result['tesseract'].get('accuracy'):
                    acc = result['tesseract']['accuracy']
                    md.append(f"**Tesseract:**\n")
                    md.append(f"- Zeit: {result['tesseract']['time']:.2f}s\n")
                    md.append(f"- Ähnlichkeit: {acc['similarity']*100:.1f}%\n")
                    md.append(f"- Wort-Genauigkeit: {acc['word_accuracy']*100:.1f}%\n\n")
            else:
                md.append("⚠️ Keine Ground Truth\n\n")
    else:
        md.append("## ⚠️ Keine Ergebnisse\n")
        md.append("Führe zuerst die OCR-Tests aus:\n")
        md.append("```bash\n")
        md.append("python research/ocr_comparison/test_mistral_ocr.py\n")
        md.append("python research/ocr_comparison/test_tesseract.py\n")
        md.append("```\n")
    
    # Vergleich (nur wenn Daten vorhanden)
    mistral_data = comparison['mistral']
    tesseract_data = comparison['tesseract']
    
    if mistral_data['total'] > 0 and tesseract_data['total'] > 0:
        md.append("## 🔍 Vergleich\n")
        
        mistral_avg_time = mistral_data['total_time'] / mistral_data['total']
        tesseract_avg_time = tesseract_data['total_time'] / tesseract_data['total']
        
        md.append("### ⚡ Geschwindigkeit\n")
        if tesseract_avg_time < mistral_avg_time:
            speedup = mistral_avg_time / tesseract_avg_time
            md.append(f"Tesseract ist **{speedup:.1f}x schneller** ({tesseract_avg_time:.2f}s vs {mistral_avg_time:.2f}s)\n\n")
        else:
            speedup = tesseract_avg_time / mistral_avg_time
            md.append(f"Mistral ist **{speedup:.1f}x schneller** ({mistral_avg_time:.2f}s vs {tesseract_avg_time:.2f}s)\n\n")
        
        if mistral_data['similarities'] and tesseract_data['similarities']:
            md.append("### 📏 Genauigkeit\n")
            mistral_avg_acc = sum(mistral_data['similarities']) / len(mistral_data['similarities'])
            tesseract_avg_acc = sum(tesseract_data['similarities']) / len(tesseract_data['similarities'])
            
            md.append(f"- Mistral: {mistral_avg_acc*100:.1f}%\n")
            md.append(f"- Tesseract: {tesseract_avg_acc*100:.1f}%\n")
            
            if mistral_avg_acc > tesseract_avg_acc:
                diff = mistral_avg_acc - tesseract_avg_acc
                md.append(f"\nMistral ist **{diff*100:.1f} Prozentpunkte genauer**\n\n")
            else:
                diff = tesseract_avg_acc - mistral_avg_acc
                md.append(f"\nTesseract ist **{diff*100:.1f} Prozentpunkte genauer**\n\n")
        
        # Fazit
        md.append("## 📋 Fazit\n")
        md.append("| Kriterium | Mistral | Tesseract |\n")
        md.append("|-----------|---------|----------|\n")
        md.append(f"| Geschwindigkeit | {mistral_avg_time:.2f}s | {tesseract_avg_time:.2f}s |\n")
        
        if mistral_data['similarities'] and tesseract_data['similarities']:
            mistral_avg_acc = sum(mistral_data['similarities']) / len(mistral_data['similarities'])
            tesseract_avg_acc = sum(tesseract_data['similarities']) / len(tesseract_data['similarities'])
            md.append(f"| Genauigkeit | {mistral_avg_acc*100:.1f}% | {tesseract_avg_acc*100:.1f}% |\n")
        
        md.append("| Kosten | Kostenpflichtig | Kostenlos |\n")
        md.append("| Offline | Nein | Ja |\n")
        md.append("| Self-hosted | Nein | Ja |\n")
    
    # Schreibe Datei
    output_path.write_text(''.join(md), encoding='utf-8')

def compare_all():
    """Vergleicht alle Ergebnisse"""
    
    global _report_buffer
    _report_buffer = StringIO()
    
    # Prüfe ob überhaupt Daten vorhanden sind
    has_mistral = any((Config.DATA_PARSED_PATH / 'mistral').rglob('*.json'))
    has_tesseract = any((Config.DATA_PARSED_PATH / 'tesseract').rglob('*.json'))
    
    if not has_mistral and not has_tesseract:
        log_and_print("\n❌ FEHLER: Keine OCR-Ergebnisse gefunden!\n")
        log_and_print("Führe zuerst die Tests aus:")
        log_and_print("  python research/ocr_comparison/test_mistral_ocr.py")
        log_and_print("  python research/ocr_comparison/test_tesseract.py\n")
        return
    
    if not has_mistral:
        log_and_print("\n⚠️  WARNUNG: Keine Mistral-Ergebnisse gefunden")
        log_and_print("   Führe aus: python research/ocr_comparison/test_mistral_ocr.py\n")
    
    if not has_tesseract:
        log_and_print("\n⚠️  WARNUNG: Keine Tesseract-Ergebnisse gefunden")
        log_and_print("   Führe aus: python research/ocr_comparison/test_tesseract.py\n")
    
    log_and_print("\n" + "="*70)
    log_and_print("OCR-VERGLEICH: Mistral vs. Tesseract")
    log_and_print("Objektive Messung: Geschwindigkeit & Genauigkeit")
    log_and_print("="*70 + "\n")
    
    comparison = {
        'mistral': {
            'total_time': 0, 
            'success': 0, 
            'total': 0, 
            'total_chars': 0,
            'similarities': [],
            'char_accuracies': [],
            'word_accuracies': []
        },
        'tesseract': {
            'total_time': 0, 
            'success': 0, 
            'total': 0, 
            'total_chars': 0,
            'similarities': [],
            'char_accuracies': [],
            'word_accuracies': []
        }
    }
    
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
            stem = pdf_file.stem
            
            log_and_print(f"\n📄 {pdf_file.name}")
            log_and_print(f"   {'─'*60}")
            
            # Lade Ground Truth (falls vorhanden)
            ground_truth = load_ground_truth(domain, stem)
            if ground_truth:
                log_and_print(f"   ✓ Ground Truth vorhanden ({len(ground_truth)} Zeichen)")
            else:
                log_and_print(f"   ⚠️  Keine Ground Truth (nur Geschwindigkeit messbar)")
            
            result_entry = {
                'file': pdf_file.name,
                'domain': domain,
                'has_ground_truth': ground_truth is not None,
                'mistral': None,
                'tesseract': None
            }
            
            # Mistral
            mistral_result = load_results('mistral', domain, stem)
            if mistral_result:
                comparison['mistral']['total'] += 1
                comparison['mistral']['total_time'] += mistral_result.get('processing_time', 0)
                
                if mistral_result.get('success'):
                    comparison['mistral']['success'] += 1
                    text = mistral_result.get('extracted_text', '')
                    text_len = len(text)
                    comparison['mistral']['total_chars'] += text_len
                    
                    result_entry['mistral'] = {
                        'time': mistral_result['processing_time'],
                        'chars': text_len,
                        'success': True
                    }
                    
                    # Genauigkeit berechnen falls Ground Truth
                    if ground_truth:
                        accuracy = calculate_accuracy(text, ground_truth)
                        if accuracy:
                            result_entry['mistral']['accuracy'] = accuracy
                            comparison['mistral']['similarities'].append(accuracy['similarity'])
                            comparison['mistral']['char_accuracies'].append(accuracy['char_accuracy'])
                            comparison['mistral']['word_accuracies'].append(accuracy['word_accuracy'])
                            
                            log_and_print(f"\n   ✅ Mistral:")
                            log_and_print(f"      Zeit:            {mistral_result['processing_time']:.2f}s")
                            log_and_print(f"      Zeichen:         {text_len:,}")
                            log_and_print(f"      Ähnlichkeit:     {accuracy['similarity']*100:.1f}%")
                            log_and_print(f"      Wort-Genauigkeit: {accuracy['word_accuracy']*100:.1f}%")
                    else:
                        log_and_print(f"   ✅ Mistral:    {mistral_result['processing_time']:.2f}s ({text_len:,} Zeichen)")
                else:
                    result_entry['mistral'] = {'success': False}
                    log_and_print(f"   ❌ Mistral:    Fehler")
            else:
                log_and_print(f"   ⚠️  Mistral:    Keine Daten")
            
            # Tesseract
            tesseract_result = load_results('tesseract', domain, stem)
            if tesseract_result:
                comparison['tesseract']['total'] += 1
                comparison['tesseract']['total_time'] += tesseract_result.get('processing_time', 0)
                
                if tesseract_result.get('success'):
                    comparison['tesseract']['success'] += 1
                    text = tesseract_result.get('extracted_text', '')
                    text_len = len(text)
                    comparison['tesseract']['total_chars'] += text_len
                    
                    result_entry['tesseract'] = {
                        'time': tesseract_result['processing_time'],
                        'chars': text_len,
                        'success': True
                    }
                    
                    # Genauigkeit berechnen falls Ground Truth
                    if ground_truth:
                        accuracy = calculate_accuracy(text, ground_truth)
                        if accuracy:
                            result_entry['tesseract']['accuracy'] = accuracy
                            comparison['tesseract']['similarities'].append(accuracy['similarity'])
                            comparison['tesseract']['char_accuracies'].append(accuracy['char_accuracy'])
                            comparison['tesseract']['word_accuracies'].append(accuracy['word_accuracy'])
                            
                            log_and_print(f"\n   ✅ Tesseract:")
                            log_and_print(f"      Zeit:            {tesseract_result['processing_time']:.2f}s")
                            log_and_print(f"      Zeichen:         {text_len:,}")
                            log_and_print(f"      Ähnlichkeit:     {accuracy['similarity']*100:.1f}%")
                            log_and_print(f"      Wort-Genauigkeit: {accuracy['word_accuracy']*100:.1f}%")
                    else:
                        log_and_print(f"   ✅ Tesseract:  {tesseract_result['processing_time']:.2f}s ({text_len:,} Zeichen)")
                else:
                    result_entry['tesseract'] = {'success': False}
                    log_and_print(f"   ❌ Tesseract:  Fehler")
            else:
                log_and_print(f"   ⚠️  Tesseract:  Keine Daten")
            
            detailed_results.append(result_entry)
    
    # Gesamt-Zusammenfassung
    log_and_print("\n" + "="*70)
    log_and_print("📊 GESAMT-ZUSAMMENFASSUNG")
    log_and_print("="*70 + "\n")
    
    for tool in ['mistral', 'tesseract']:
        data = comparison[tool]
        
        log_and_print(f"{tool.upper()}:")
        if data['total'] > 0:
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
                log_and_print(f"  Genauigkeit:   Nicht messbar (keine Ground Truth)")
        else:
            log_and_print(f"  Keine Daten vorhanden")
        
        log_and_print("")
    
    # Direkter Vergleich
    log_and_print("="*70)
    log_and_print("🔍 DIREKTER VERGLEICH")
    log_and_print("="*70 + "\n")
    
    mistral_data = comparison['mistral']
    tesseract_data = comparison['tesseract']
    
    if mistral_data['total'] > 0 and tesseract_data['total'] > 0:
        # Geschwindigkeit
        mistral_avg_time = mistral_data['total_time'] / mistral_data['total']
        tesseract_avg_time = tesseract_data['total_time'] / tesseract_data['total']
        
        log_and_print("⚡ GESCHWINDIGKEIT:")
        if abs(mistral_avg_time - tesseract_avg_time) < 0.5:
            log_and_print(f"   → Vergleichbar (~{mistral_avg_time:.1f}s vs ~{tesseract_avg_time:.1f}s)")
        elif tesseract_avg_time < mistral_avg_time:
            speedup = mistral_avg_time / tesseract_avg_time
            log_and_print(f"   → Tesseract schneller: {tesseract_avg_time:.2f}s vs {mistral_avg_time:.2f}s ({speedup:.1f}x)")
        else:
            speedup = tesseract_avg_time / mistral_avg_time
            log_and_print(f"   → Mistral schneller: {mistral_avg_time:.2f}s vs {tesseract_avg_time:.2f}s ({speedup:.1f}x)")
        
        # Genauigkeit
        log_and_print("\n📏 GENAUIGKEIT:")
        if mistral_data['similarities'] and tesseract_data['similarities']:
            mistral_avg_acc = sum(mistral_data['similarities']) / len(mistral_data['similarities'])
            tesseract_avg_acc = sum(tesseract_data['similarities']) / len(tesseract_data['similarities'])
            
            diff = abs(mistral_avg_acc - tesseract_avg_acc)
            
            if diff < 0.05:
                log_and_print(f"   → Vergleichbar ({mistral_avg_acc*100:.1f}% vs {tesseract_avg_acc*100:.1f}%)")
            elif mistral_avg_acc > tesseract_avg_acc:
                log_and_print(f"   → Mistral genauer: {mistral_avg_acc*100:.1f}% vs {tesseract_avg_acc*100:.1f}%")
                log_and_print(f"   → Differenz: {diff*100:.1f} Prozentpunkte")
            else:
                log_and_print(f"   → Tesseract genauer: {tesseract_avg_acc*100:.1f}% vs {mistral_avg_acc*100:.1f}%")
                log_and_print(f"   → Differenz: {diff*100:.1f} Prozentpunkte")
        else:
            log_and_print(f"   → Nicht messbar (Ground Truth fehlt)")
            log_and_print(f"   → Tipp: Erstelle <filename>_ground_truth.txt Dateien")
        
        log_and_print("\n💰 KOSTEN:")
        log_and_print(f"   Mistral:    API-basiert (kostenpflichtig)")
        log_and_print(f"   Tesseract:  Open Source (kostenlos)")
        
        log_and_print("\n🌐 DEPLOYMENT:")
        log_and_print(f"   Mistral:    Externe API, Internet erforderlich")
        log_and_print(f"   Tesseract:  Selbst hostbar, offline nutzbar")
        
        log_and_print("\n🔧 WARTUNG:")
        log_and_print(f"   Mistral:    Managed Service, keine lokale Wartung")
        log_and_print(f"   Tesseract:  Selbst gewartet, volle Kontrolle")
        
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
        
        if mistral_data['similarities'] and tesseract_data['similarities']:
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
    
    log_and_print("\n" + "="*70 + "\n")
    
    # ===== Speichere Outputs =====
    
    # 1. JSON
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
    
    # 2. Markdown
    output_md = Config.DATA_PARSED_PATH / 'comparison_report.md'
    generate_markdown_report(output_md, comparison, detailed_results)
    log_and_print(f"📄 Markdown-Report: {output_md}")
    
    # 3. Text
    output_txt = Config.DATA_PARSED_PATH / 'comparison_report.txt'
    output_txt.write_text(_report_buffer.getvalue(), encoding='utf-8')
    log_and_print(f"📝 Text-Report: {output_txt}")
    
    log_and_print("\n✅ Alle Reports gespeichert!\n")

if __name__ == '__main__':
    compare_all()