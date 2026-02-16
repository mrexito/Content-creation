"""
Zentrale Konfiguration für das Projekt
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env.dev laden
load_dotenv('.env.dev')

class Config:
    """Projekt-Konfiguration"""
    
    # API Keys
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    BFH_LLM_API_KEY = os.getenv('BFH_LLM_API_KEY')
    BFH_LLM_ENDPOINT = os.getenv('BFH_LLM_ENDPOINT')
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_INPUT_PATH = PROJECT_ROOT / 'data' / 'input'
    DATA_OUTPUT_PATH = PROJECT_ROOT / 'data' / 'output'
    DATA_PARSED_PATH = PROJECT_ROOT / 'data' / 'parsed'
    
    # OCR Settings
    OCR_TOOL = 'mistral'  # 'mistral' oder 'nougat'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Prüft ob alle notwendigen Configs vorhanden sind"""
        if not cls.MISTRAL_API_KEY:
            print("⚠️  MISTRAL_API_KEY fehlt in .env.dev")
        
        # Erstelle Ordner falls nicht vorhanden
        cls.DATA_INPUT_PATH.mkdir(parents=True, exist_ok=True)
        cls.DATA_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        cls.DATA_PARSED_PATH.mkdir(parents=True, exist_ok=True)

# Beim Import direkt validieren
Config.validate()