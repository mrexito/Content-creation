"""
Logging-Setup für das gesamte Projekt
"""
import logging
import sys
from pathlib import Path
from .config import Config

def setup_logger(name: str) -> logging.Logger:
    """
    Erstellt einen konfigurierten Logger
    
    Args:
        name: Name des Loggers (meist __name__)
    
    Returns:
        Konfigurierter Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Handler hinzufügen
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger

# Haupt-Logger für das Projekt
project_logger = setup_logger('langchain_langgraph_comparison')