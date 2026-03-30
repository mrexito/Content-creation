"""
Zentrale Konfiguration für das Projekt
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Lade .env.dev
env_path = Path(__file__).parent.parent.parent / '.env.dev'
load_dotenv(env_path)

class Config:
    """Projekt-Konfiguration"""
    
    # Projekt-Pfade
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_ROOT = PROJECT_ROOT / 'data'
    DATA_INPUT_PATH = DATA_ROOT / 'input'
    DATA_OUTPUT_PATH = DATA_ROOT / 'output'
    DATA_PARSED_PATH = DATA_ROOT / 'parsed'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # API Keys
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    
    # ===== NEU: OpenAI =====
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # ===== NEU: BFH LLM =====
    BFH_LLM_ENDPOINT = os.getenv('BFH_LLM_ENDPOINT', 'https://inference.mlmp.ti.bfh.ch/api/v1')
    BFH_LLM_API_KEY = os.getenv('BFH_LLM_API_KEY')
    BFH_LLM_MODEL = os.getenv('BFH_LLM_MODEL', 'gpt-oss:120b')
    
    # ===== NEU: LLM Settings (generisch) =====
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'auto')  # 'openai', 'bfh', 'auto'
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '2000')) if os.getenv('LLM_MAX_TOKENS') else None
    
    # ===== OCR Settings =====
    OCR_DEFAULT_TOOL = os.getenv('OCR_DEFAULT_TOOL', 'auto')  # 'tesseract', 'mistral', 'auto'
    OCR_DPI = int(os.getenv('OCR_DPI', '300'))
    OCR_TESSERACT_LANG = os.getenv('OCR_TESSERACT_LANG', 'deu+eng')
    
    # Domain-spezifische OCR-Präferenzen
    OCR_DOMAIN_MATH = os.getenv('OCR_DOMAIN_MATH', 'mistral')
    OCR_DOMAIN_LANGUAGES = os.getenv('OCR_DOMAIN_LANGUAGES', 'tesseract')
    OCR_DOMAIN_ECONOMICS = os.getenv('OCR_DOMAIN_ECONOMICS', 'tesseract')
    
    @classmethod
    def validate(cls):
        """Validiert die Konfiguration"""
        # Stelle sicher, dass kritische Pfade existieren
        cls.DATA_INPUT_PATH.mkdir(parents=True, exist_ok=True)
        cls.DATA_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        cls.DATA_PARSED_PATH.mkdir(parents=True, exist_ok=True)
        
        return True

# Validiere Config beim Import.
# HINWEIS: Config.validate() hat einen Filesystem-Seiteneffekt — es legt die
# Verzeichnisse DATA_INPUT_PATH, DATA_OUTPUT_PATH und DATA_PARSED_PATH an (mkdir).
# Dies ist absichtlich: alle Prototypen setzen diese Pfade als vorhanden voraus.
Config.validate()