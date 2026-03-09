"""
Test-Script für Mistral OCR

Nutzt den dedizierten Mistral OCR-Endpunkt (client.ocr.process) mit
dem Modell 'mistral-ocr-latest' (verfügbar seit März 2025).

Option A (bevorzugt): PDF direkt als base64 hochladen — kein Umweg
über pdf2image/PIL nötig.
"""
import base64
import json
import time
from pathlib import Path
from mistralai import Mistral
import sys

# Füge src zu Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)


def test_mistral_ocr(pdf_path: Path) -> dict:
    """
    Testet Mistral OCR auf einem PDF (direkt, kein Umweg über Bilder).

    Verwendet client.ocr.process() mit model='mistral-ocr-latest'.

    Returns:
        dict mit extracted_text, processing_time, pages, model, success
    """
    logger.info(f"Teste Mistral OCR (PDF-direkt) mit: {pdf_path.name}")

    if not Config.MISTRAL_API_KEY:
        logger.error("MISTRAL_API_KEY nicht gesetzt!")
        return {
            'extracted_text': None,
            'processing_time': 0,
            'error': 'MISTRAL_API_KEY nicht gesetzt',
            'success': False
        }

    client = Mistral(api_key=Config.MISTRAL_API_KEY)
    start_time = time.time()

    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{pdf_base64}"
            }
        )

        processing_time = time.time() - start_time

        if not response.pages:
            logger.warning(f"Leere Antwort für {pdf_path.name}")
            return {
                'extracted_text': '',
                'processing_time': processing_time,
                'pages': 0,
                'model': 'mistral-ocr-latest',
                'success': True
            }

        text = "\n\n".join(page.markdown for page in response.pages)
        logger.info(
            f"  ✓ {len(response.pages)} Seite(n) in {processing_time:.2f}s, "
            f"{len(text)} Zeichen"
        )

        return {
            'extracted_text': text,
            'processing_time': processing_time,
            'pages': len(response.pages),
            'model': 'mistral-ocr-latest',
            'success': True
        }

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"  ✗ Fehler: {type(e).__name__}: {e}")
        return {
            'extracted_text': None,
            'processing_time': processing_time,
            'error': str(e),
            'success': False
        }

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
            result = test_mistral_ocr(pdf_file)
            results[f"{domain}/{pdf_file.name}"] = result
            
            # Speichere Ergebnis
            output_path = Config.DATA_PARSED_PATH / 'mistral' / domain / f"{pdf_file.stem}.json"
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
    print("🚀 Starte Mistral OCR Tests (mistral-ocr-latest)...\n")
    results = test_all_pdfs()

    # Summary
    print("\n" + "="*50)
    print("ZUSAMMENFASSUNG")
    print("="*50)

    total = len(results)
    success = sum(1 for r in results.values() if r.get('success'))
    avg_time = (
        sum(r.get('processing_time', 0) for r in results.values()) / total
        if total > 0 else 0
    )
    total_pages = sum(r.get('pages', 0) for r in results.values())

    print(f"Getestete PDFs:   {total}")
    print(f"Erfolgreich:      {success}/{total}")
    print(f"Gesamt-Seiten:    {total_pages}")
    print(f"Durchschn. Zeit:  {avg_time:.2f}s")
    if total_pages > 0:
        print(f"Zeit pro Seite:   {avg_time / total_pages:.2f}s")