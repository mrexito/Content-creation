"""
Vereinfachtes Nougat-Test - Testet nur ein einzelnes PDF
"""
import json
import time
from pathlib import Path
import subprocess
import tempfile
import sys
import os
import threading

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)

def progress_indicator(stop_event):
    """Zeigt einen Fortschrittsindikator während Nougat läuft"""
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    while not stop_event.is_set():
        print(f'\r   {chars[idx % len(chars)]} Verarbeite... (kann 30-120s dauern)', end='', flush=True)
        idx += 1
        time.sleep(0.1)
    print('\r' + ' ' * 60 + '\r', end='', flush=True)  # Clear line

def test_nougat_single_pdf(pdf_path: Path) -> dict:
    """
    Testet Nougat OCR mit einem einzelnen PDF
    """
    logger.info(f"Teste Nougat OCR mit: {pdf_path}")
    
    if not pdf_path.exists():
        logger.error(f"PDF nicht gefunden: {pdf_path}")
        return {'success': False, 'error': 'PDF nicht gefunden'}
    
    start_time = time.time()
    
    try:
        # Temporäres Output-Verzeichnis
        with tempfile.TemporaryDirectory() as tmpdir:
            
            # Forciere CPU (verhindert CUDA-Fehler)
            env = os.environ.copy()
            env['CUDA_VISIBLE_DEVICES'] = ''
            
            # Finde nougat CLI
            venv_nougat = Path(__file__).parent.parent.parent / 'venv' / 'bin' / 'nougat'
            nougat_cmd = str(venv_nougat) if venv_nougat.exists() else 'nougat'
            
            # Nougat CLI aufrufen
            cmd = [
                nougat_cmd,
                str(pdf_path),
                '-o', tmpdir,
                '--no-skipping',
                '--batchsize', '1'
            ]
            
            logger.info(f"Führe aus: {' '.join(cmd)}")
            print(f"\n⏳ Starte Nougat (dies dauert lange...):")
            print(f"   • Beim ersten Mal: Modell-Download (~1-2 GB, 5-10 Min.)")
            print(f"   • Modell-Initialisierung: ~30-60s")
            print(f"   • Pro Seite Verarbeitung: ~30-60s\n")
            
            # Start progress indicator in thread
            stop_event = threading.Event()
            progress_thread = threading.Thread(target=progress_indicator, args=(stop_event,))
            progress_thread.start()
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 Minuten (für Modell-Download + Verarbeitung)
                    env=env
                )
            finally:
                # Stop progress indicator
                stop_event.set()
                progress_thread.join()
            
            processing_time = time.time() - start_time
            
            # Zeige stderr nur bei Fehler
            if result.returncode != 0:
                logger.error(f"  Nougat returncode: {result.returncode}")
                # Zeige nur relevante Fehler (nicht alle Warnungen)
                error_lines = [line for line in result.stderr.split('\n') 
                              if 'error' in line.lower() or 'traceback' in line.lower()]
                if error_lines:
                    logger.error(f"  Fehler: {error_lines[0][:200]}")
            
            # Lese Output
            output_files = list(Path(tmpdir).glob('*.mmd')) + list(Path(tmpdir).glob('*.txt'))
            
            if output_files:
                text = output_files[0].read_text(encoding='utf-8')
                logger.info(f"✅ Erfolgreich in {processing_time:.1f}s ({processing_time/60:.1f} Min.)")
                logger.info(f"   Output-Datei: {output_files[0].name}")
                logger.info(f"   Extrahierter Text: {len(text)} Zeichen")
                
                # Zeige ersten Teil des Texts
                preview = text[:200].replace('\n', ' ')
                logger.info(f"   Vorschau: {preview}...")
                
                return {
                    'extracted_text': text,
                    'processing_time': processing_time,
                    'model': 'nougat-base-cli',
                    'output_file': output_files[0].name,
                    'text_length': len(text),
                    'success': True,
                    'pdf_path': str(pdf_path)
                }
            else:
                all_files = list(Path(tmpdir).iterdir())
                logger.error(f"✗ Keine Output-Datei gefunden")
                logger.error(f"  Gefundene Dateien: {[f.name for f in all_files]}")
                
                return {
                    'extracted_text': None,
                    'processing_time': processing_time,
                    'error': f'Keine Output-Datei. Gefunden: {[f.name for f in all_files]}',
                    'stderr': result.stderr[:500] if result.stderr else None,
                    'success': False
                }
                
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Timeout nach 10 Minuten")
        return {
            'extracted_text': None,
            'processing_time': 600.0,
            'error': 'Timeout nach 10 Minuten',
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

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_nougat_single.py <pdf_path>")
        print("\nBeispiele:")
        print("  python test_nougat_single.py data/input/math/equations_simple.pdf")
        print("  python test_nougat_single.py data/input/languages/grammar_exercise.pdf")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    print("🚀 Starte Nougat OCR Test (Single PDF)...\n")
    
    result = test_nougat_single_pdf(pdf_path)
    
    # Zeige Ergebnis
    print("\n" + "="*60)
    print("ERGEBNIS")
    print("="*60)
    
    if result['success']:
        print(f"✅ Erfolgreich!")
        print(f"   Verarbeitungszeit: {result['processing_time']:.1f}s ({result['processing_time']/60:.1f} Min.)")
        print(f"   Text-Länge: {result['text_length']} Zeichen")
        
        # Speichere Ergebnis
        output_path = Config.DATA_PARSED_PATH / 'nougat' / 'test' / f"{pdf_path.stem}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        text_path = output_path.with_suffix('.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(result['extracted_text'])
        
        print(f"   Gespeichert: {output_path}")
        print(f"\n💡 Hinweis: Nougat ist sehr langsam (~30-60s pro Seite auf CPU)")
    else:
        print(f"❌ Fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}")