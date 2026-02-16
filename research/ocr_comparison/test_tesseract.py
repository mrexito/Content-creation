"""
Test-Script für Tesseract OCR (kostenlose Alternative)
"""
import json
import time
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)

def pdf_to_images(pdf_path: Path) -> list:
    """Konvertiert PDF zu Bildern"""
    try:
        images = convert_from_path(pdf_path, dpi=300)  # Höhere DPI für bessere Qualität
        logger.info(f"PDF hat {len(images)} Seite(n)")
        return images
    except Exception as e:
        logger.error(f"Fehler beim PDF-Konvertieren: {e}")
        return []

def test_tesseract_ocr(pdf_path: Path) -> dict:
    """
    Testet Tesseract OCR auf einem PDF
    """
    logger.info(f"Teste Tesseract OCR mit: {pdf_path.name}")
    
    # PDF zu Bildern
    images = pdf_to_images(pdf_path)
    if not images:
        return {
            'extracted_text': None,
            'processing_time': 0,
            'error': 'PDF konnte nicht in Bilder konvertiert werden',
            'success': False
        }
    
    all_text = []
    total_time = 0
    
    # Jede Seite einzeln verarbeiten
    for idx, image in enumerate(images):
        logger.info(f"  Verarbeite Seite {idx + 1}/{len(images)}")
        
        start_time = time.time()
        
        try:
            # Tesseract mit deutschen und englischen Sprachdaten
            # lang='deu+eng' für Deutsch + Englisch
            # config='--psm 1' für automatische Seiten-Segmentierung mit OSD
            text = pytesseract.image_to_string(
                image, 
                lang='deu+eng',
                config='--psm 1 --oem 3'
            )
            
            page_time = time.time() - start_time
            total_time += page_time
            
            all_text.append(f"--- Seite {idx + 1} ---\n{text}")
            
            logger.info(f"  ✓ Seite {idx + 1} in {page_time:.2f}s")
            
        except Exception as e:
            logger.error(f"  ✗ Fehler auf Seite {idx + 1}: {str(e)}")
            all_text.append(f"--- Seite {idx + 1} ---\n[FEHLER: {str(e)}]")
    
    result = {
        'extracted_text': '\n\n'.join(all_text),
        'processing_time': total_time,
        'pages': len(images),
        'model': 'tesseract-ocr',
        'success': True
    }
    
    logger.info(f"✓ Gesamt-Zeit: {total_time:.2f}s für {len(images)} Seite(n)")
    return result

def test_all_pdfs():
    """Testet alle PDFs im input Ordner"""
    results = {}
    
    for domain in ['math', 'languages', 'economics']:
        domain_path = Config.DATA_INPUT_PATH / domain
        
        if not domain_path.exists():
            logger.warning(f"Ordner nicht gefunden: {domain_path}")
            continue
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Domäne: {domain.upper()}")
        logger.info(f"{'='*50}")
        
        for pdf_file in domain_path.glob('*.pdf'):
            result = test_tesseract_ocr(pdf_file)
            results[f"{domain}/{pdf_file.name}"] = result
            
            # Speichere Ergebnis
            output_path = Config.DATA_PARSED_PATH / 'tesseract' / domain / f"{pdf_file.stem}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Speichere auch den reinen Text
            text_path = output_path.with_suffix('.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(result.get('extracted_text', ''))
            
            logger.info(f"Gespeichert: {output_path}")
            print(f"\n{'-'*50}\n")
    
    return results

if __name__ == '__main__':
    print("🚀 Starte Tesseract OCR Tests...\n")
    
    start_total = time.time()
    results = test_all_pdfs()
    total_duration = time.time() - start_total
    
    # Summary
    print("\n" + "="*50)
    print("ZUSAMMENFASSUNG")
    print("="*50)
    
    total = len(results)
    success = sum(1 for r in results.values() if r.get('success'))
    avg_time = sum(r.get('processing_time', 0) for r in results.values()) / total if total > 0 else 0
    total_pages = sum(r.get('pages', 0) for r in results.values())
    
    print(f"Getestete PDFs: {total}")
    print(f"Erfolgreich: {success}/{total}")
    print(f"Gesamt-Seiten: {total_pages}")
    print(f"Durchschn. Zeit: {avg_time:.2f}s")
    print(f"Zeit pro Seite: {avg_time/total_pages:.2f}s" if total_pages > 0 else "")
    print(f"Gesamt-Dauer: {total_duration:.2f}s")