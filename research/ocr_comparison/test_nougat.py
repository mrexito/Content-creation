"""
Vereinfachtes Nougat-Test mit direkter CLI-Nutzung
"""
import json
import time
from pathlib import Path
import subprocess
import tempfile
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)

def test_nougat_ocr_via_cli(pdf_path: Path) -> dict:
    """
    Nutzt Nougat's CLI direkt (einfachste Methode)
    """
    logger.info(f"Teste Nougat OCR mit: {pdf_path.name}")
    
    start_time = time.time()
    
    try:
        # Temporäres Output-Verzeichnis
        with tempfile.TemporaryDirectory() as tmpdir:
            
            # Forciere CPU (verhindert CUDA-Fehler)
            env = os.environ.copy()
            env['CUDA_VISIBLE_DEVICES'] = ''
            
            # Finde nougat CLI - zuerst in venv, dann in PATH
            venv_nougat = Path(__file__).parent.parent.parent / 'venv' / 'bin' / 'nougat'
            nougat_cmd = str(venv_nougat) if venv_nougat.exists() else 'nougat'
            
            # Nougat CLI aufrufen
            cmd = [
                nougat_cmd,
                str(pdf_path),
                '-o', tmpdir,
                '--no-skipping',
                '--batchsize', '1'  # Kleinere Batch-Größe für schnellere Verarbeitung
            ]
            
            logger.info(f"  Führe aus: {' '.join(cmd)}")
            logger.info(f"  ⏳ Bitte warten, Nougat ist langsam (kann 30-60s pro Seite dauern)...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 Minuten Timeout
                env=env
            )
            
            processing_time = time.time() - start_time
            
            # Debug: Zeige stdout/stderr
            if result.stdout:
                logger.debug(f"  stdout: {result.stdout}")
            if result.stderr:
                logger.warning(f"  stderr: {result.stderr}")
            
            # Return code prüfen
            if result.returncode != 0:
                logger.error(f"  Nougat returncode: {result.returncode}")
            
            # Lese Output - kann .mmd oder .txt sein
            output_files = list(Path(tmpdir).glob('*.mmd')) + list(Path(tmpdir).glob('*.txt'))
            
            if output_files:
                text = output_files[0].read_text(encoding='utf-8')
                logger.info(f"✓ Erfolgreich in {processing_time:.2f}s")
                logger.info(f"  Output-Datei: {output_files[0].name}")
                logger.info(f"  Text-Länge: {len(text)} Zeichen")
                
                return {
                    'extracted_text': text,
                    'processing_time': processing_time,
                    'model': 'nougat-base-cli',
                    'output_file': output_files[0].name,
                    'text_length': len(text),
                    'success': True
                }
            else:
                # Liste alle Dateien im tmpdir
                all_files = list(Path(tmpdir).iterdir())
                logger.error(f"✗ Keine Output-Datei gefunden")
                logger.error(f"  Gefundene Dateien: {[f.name for f in all_files]}")
                
                return {
                    'extracted_text': None,
                    'processing_time': processing_time,
                    'error': f'Keine Output-Datei. Gefunden: {[f.name for f in all_files]}',
                    'stderr': result.stderr,
                    'success': False
                }
                
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Timeout nach 5 Minuten")
        return {
            'extracted_text': None,
            'processing_time': 300.0,
            'error': 'Timeout nach 5 Minuten',
            'success': False
        }
    except FileNotFoundError as e:
        logger.error(f"✗ Nougat CLI nicht gefunden: {str(e)}")
        logger.error("  Installiere mit: pip install nougat-ocr")
        return {
            'extracted_text': None,
            'processing_time': time.time() - start_time,
            'error': 'Nougat CLI nicht gefunden. Installiere mit: pip install nougat-ocr',
            'success': False
        }
    except Exception as e:
        logger.error(f"✗ Fehler: {str(e)}")
        return {
            'extracted_text': None,
            'processing_time': time.time() - start_time,
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
            result = test_nougat_ocr_via_cli(pdf_file)
            results[f"{domain}/{pdf_file.name}"] = result
            
            # Speichere Ergebnis
            output_path = Config.DATA_PARSED_PATH / 'nougat' / domain / f"{pdf_file.stem}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Speichere auch den reinen Text
            if result.get('extracted_text'):
                text_path = output_path.with_suffix('.txt')
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(result['extracted_text'])
                logger.info(f"Gespeichert: {output_path}")
            
            print(f"\n{'-'*50}\n")
    
    return results

if __name__ == '__main__':
    print("🚀 Starte Nougat OCR Tests (CLI)...\n")
    
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
    
    print(f"Getestete PDFs: {total}")
    print(f"Erfolgreich: {success}/{total}")
    print(f"Durchschn. Zeit: {avg_time:.2f}s")
    print(f"Gesamt-Dauer: {total_duration:.2f}s")
    
    # Zeige Fehler
    failures = [k for k, v in results.items() if not v.get('success')]
    if failures:
        print(f"\n⚠️  Fehlgeschlagen:")
        for f in failures:
            error = results[f].get('error', 'Unbekannter Fehler')
            print(f"  - {f}: {error}")