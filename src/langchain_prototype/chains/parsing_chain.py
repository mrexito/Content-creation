"""
Parsing Chain: PDF → Text
Nutzt OCR-Handler (Tesseract/Mistral)

LCEL-Kompatibilität:
    OCR ist kein LLM-Schritt — kein LCEL-Chain-Aufruf nötig.
    Die Chain ist via RunnableLambda als formales LCEL-Runnable verpackt.
"""
from pathlib import Path
from typing import Dict, Any

from langchain_core.runnables import RunnableLambda

from common.ocr_handler import get_ocr_handler
from common.logger import setup_logger

logger = setup_logger(__name__)


class ParsingChain:
    """
    Chain für PDF-Parsing mit OCR
    """
    
    def __init__(self, domain: str = None):
        """
        Args:
            domain: Optional domain für domain-spezifisches OCR
        """
        self.domain = domain
        self.ocr = get_ocr_handler()

        # RunnableLambda-Wrapper: macht ParsingChain formal LCEL-kompatibel.
        # OCR ist kein LLM-Schritt und wird nicht auf ChatPromptTemplate umgestellt.
        self._runnable = RunnableLambda(self.invoke)

        logger.info(f"ParsingChain (LCEL-kompatibel) initialisiert (Domain: {domain or 'any'})")
    
    def parse_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Parsed ein PDF zu Text
        
        Args:
            pdf_path: Pfad zum PDF
        
        Returns:
            Dict mit text, metadata, success
        """
        logger.info(f"Parse PDF: {pdf_path.name}")
        
        # OCR-Handler aufrufen
        result = self.ocr.pdf_to_text(pdf_path, domain=self.domain)
        
        if not result['success']:
            logger.error(f"Parsing fehlgeschlagen: {result.get('error')}")
            return {
                'text': None,
                'metadata': {
                    'pdf_path': str(pdf_path),
                    'domain': self.domain,
                    'success': False,
                    'error': result.get('error')
                },
                'success': False
            }
        
        # Erfolgreicher Parse
        return {
            'text': result['text'],
            'metadata': {
                'pdf_path': str(pdf_path),
                'domain': self.domain,
                'pages': result['pages'],
                'processing_time': result['processing_time'],
                'tool_used': result['tool_used'],
                'success': True
            },
            'success': True
        }
    
    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke Methode
        
        Args:
            input_data: Dict mit 'pdf_path' key
        
        Returns:
            Dict mit parsing results
        """
        pdf_path = Path(input_data['pdf_path'])
        return self.parse_pdf(pdf_path)


def get_parsing_chain(domain: str = None) -> ParsingChain:
    """Factory für ParsingChain"""
    return ParsingChain(domain=domain)