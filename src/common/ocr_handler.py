"""
Zentraler OCR-Handler für alle Prototypen
Unterstützt mehrere OCR-Tools mit domain-spezifischer Auswahl
"""
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path
from typing import List, Dict, Literal
import time
import base64
import io
from PIL import Image

from .config import Config
from .constants import normalize_domain, DOMAIN_MATH, DOMAIN_LANGUAGES, DOMAIN_ECONOMICS
from .logger import setup_logger

logger = setup_logger(__name__)

# Verfügbare OCR-Tools
OCRTool = Literal['tesseract', 'mistral', 'auto']

TESSERACT_CONFIG = '--psm 1 --oem 3'
MISTRAL_OCR_MODEL = 'mistral-ocr-latest'


class OCRHandler:
    """
    Zentrale Klasse für OCR-Verarbeitung mit Multi-Tool-Support
    """

    def __init__(
        self,
        default_tool: OCRTool = 'auto',
        dpi: int = 300,
        tesseract_lang: str = 'deu+eng'
    ):
        """
        Args:
            default_tool: Standard-Tool ('tesseract', 'mistral', 'auto')
            dpi: Auflösung für PDF-zu-Bild Konvertierung
            tesseract_lang: Sprachen für Tesseract
        """
        self.default_tool = default_tool
        self.dpi = dpi
        self.tesseract_lang = tesseract_lang

        # Domain-spezifische Präferenzen (kanonische Domain-Namen)
        self.domain_preferences = {
            DOMAIN_MATH:       'mistral',    # Formeln → Mistral besser
            DOMAIN_LANGUAGES:  'tesseract',  # Text → Tesseract ausreichend
            DOMAIN_ECONOMICS:  'tesseract'   # Tabellen/Text → Tesseract ausreichend
        }

        # OCR_FORCE_MISTRAL=1 erzwingt Mistral für alle Domains (z.B. für Mistral-OCR-Evaluationen)
        import os
        if os.environ.get('OCR_FORCE_MISTRAL') == '1':
            self.domain_preferences = {
                DOMAIN_MATH:       'mistral',
                DOMAIN_LANGUAGES:  'mistral',
                DOMAIN_ECONOMICS:  'mistral',
            }

        # Mistral API verfügbar?
        self.mistral_available = bool(Config.MISTRAL_API_KEY)

        if not self.mistral_available and default_tool == 'mistral':
            logger.warning("Mistral API Key nicht gefunden, falle zurück auf Tesseract")
            self.default_tool = 'tesseract'

        logger.info(
            f"OCRHandler initialisiert (Default: {self.default_tool}, "
            f"DPI: {dpi}, Mistral: {self.mistral_available})"
        )

    def set_domain_preference(self, domain: str, tool: OCRTool):
        """
        Setzt die Tool-Präferenz für eine Domain

        Args:
            domain: z.B. 'math', 'mathematics', 'languages', 'economics'
            tool: 'tesseract', 'mistral', oder 'auto'
        """
        canonical = normalize_domain(domain)
        self.domain_preferences[canonical] = tool
        logger.info(f"Domain-Präferenz gesetzt: {canonical} → {tool}")

    def get_domain_preferences(self) -> Dict[str, str]:
        """Gibt aktuelle Domain-Präferenzen zurück"""
        return self.domain_preferences.copy()

    def _choose_tool(self, domain: str = None, force_tool: OCRTool = None) -> str:
        """
        Wählt das passende OCR-Tool basierend auf Domain und Einstellungen.

        Normalisiert Domain-Strings ('math' und 'mathematics' werden gleich behandelt).

        Args:
            domain: Optional, z.B. 'math', 'mathematics', 'languages', 'economics'
            force_tool: Optional, erzwingt ein bestimmtes Tool

        Returns:
            'tesseract' oder 'mistral'
        """
        # 1. Force-Tool hat höchste Priorität
        if force_tool and force_tool != 'auto':
            if force_tool == 'mistral' and not self.mistral_available:
                logger.warning("Mistral nicht verfügbar, nutze Tesseract")
                return 'tesseract'
            return force_tool

        # 2. Domain-spezifische Präferenz (normalisieren für konsistentes Lookup)
        if domain:
            canonical_domain = normalize_domain(domain)
            if canonical_domain in self.domain_preferences:
                preferred = self.domain_preferences[canonical_domain]
                if preferred == 'mistral' and not self.mistral_available:
                    logger.warning(
                        f"Mistral für {canonical_domain} bevorzugt, aber nicht verfügbar → Tesseract"
                    )
                    return 'tesseract'
                if preferred != 'auto':
                    return preferred

        # 3. Default-Tool
        if self.default_tool != 'auto':
            return self.default_tool

        # 4. Auto-Fallback
        return 'mistral' if self.mistral_available else 'tesseract'

    def _pdf_to_images(self, pdf_path: Path) -> List[Image.Image]:
        """Konvertiert PDF zu Bildern"""
        try:
            images = convert_from_path(pdf_path, dpi=self.dpi)
            logger.debug(f"PDF hat {len(images)} Seite(n)")
            return images
        except Exception as e:
            logger.error(f"Fehler beim PDF-Konvertieren: {e}")
            return []

    def _ocr_tesseract(self, image: Image.Image) -> str:
        """OCR mit Tesseract"""
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.tesseract_lang,
                config=TESSERACT_CONFIG
            )
            return text
        except Exception as e:
            logger.error(f"Tesseract OCR Fehler: {e}")
            return ""

    def _ocr_mistral(self, image: Image.Image) -> str:
        """
        OCR mit Mistral OCR API (mistral-ocr-latest).

        Sendet die Seite als base64-kodiertes PNG-Bild an den dedizierten
        Mistral OCR-Endpunkt (client.ocr.process).
        """
        try:
            from mistralai import Mistral

            # Bild zu Base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            img_size_kb = len(buffered.getvalue()) / 1024

            logger.debug(f"Mistral OCR Request: {img_size_kb:.1f} KB")

            api_key = Config.MISTRAL_API_KEY
            client = Mistral(api_key=api_key)

            response = client.ocr.process(
                model=MISTRAL_OCR_MODEL,
                document={
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{img_base64}"
                }
            )

            if not response.pages:
                logger.warning("Mistral OCR: Leere Antwort (0 Seiten)")
                return ""

            content = "\n\n".join(page.markdown for page in response.pages)

            logger.debug(
                f"Mistral OCR Response: {len(response.pages)} Seite(n), "
                f"{len(content)} Zeichen"
            )

            return content

        except Exception as e:
            logger.error(f"Mistral OCR Fehler: {type(e).__name__}: {e}")
            return ""

    def pdf_to_text(
        self,
        pdf_path: Path,
        domain: str = None,
        force_tool: OCRTool = None
    ) -> Dict:
        """
        Konvertiert ein PDF zu Text

        Args:
            pdf_path: Pfad zum PDF
            domain: Optional, z.B. 'math', 'mathematics', 'languages', 'economics'
            force_tool: Optional, erzwingt ein bestimmtes Tool

        Returns:
            Dict mit:
            - text: Extrahierter Text
            - pages: Anzahl Seiten
            - processing_time: Verarbeitungszeit
            - tool_used: Verwendetes OCR-Tool
            - success: Boolean
        """
        logger.info(f"Verarbeite PDF: {pdf_path.name}")

        if not pdf_path.exists():
            logger.error(f"PDF nicht gefunden: {pdf_path}")
            return {
                'text': None,
                'pages': 0,
                'processing_time': 0,
                'tool_used': None,
                'success': False,
                'error': 'PDF nicht gefunden'
            }

        # Wähle Tool
        tool = self._choose_tool(domain, force_tool)
        logger.info(
            f"  Gewähltes Tool: {tool}" + (f" (Domain: {domain})" if domain else "")
        )
        logger.debug(
            f"  Mistral verfügbar: {self.mistral_available}, "
            f"force_tool={force_tool}"
        )

        start_time = time.time()

        try:
            # PDF zu Bildern
            images = self._pdf_to_images(pdf_path)
            if not images:
                return {
                    'text': None,
                    'pages': 0,
                    'processing_time': time.time() - start_time,
                    'tool_used': tool,
                    'success': False,
                    'error': 'PDF-Konvertierung fehlgeschlagen'
                }

            # Jede Seite mit gewähltem Tool verarbeiten
            all_text = []

            for idx, image in enumerate(images):
                logger.debug(f"  Verarbeite Seite {idx + 1}/{len(images)} mit {tool}")

                if tool == 'mistral':
                    page_text = self._ocr_mistral(image)
                else:  # tesseract
                    page_text = self._ocr_tesseract(image)

                all_text.append(page_text)

            processing_time = time.time() - start_time
            full_text = '\n\n'.join(all_text)

            logger.info(f"  ✓ Erfolgreich in {processing_time:.2f}s mit {tool}")
            logger.info(f"  Extrahiert: {len(full_text)} Zeichen")

            return {
                'text': full_text,
                'pages': len(images),
                'processing_time': processing_time,
                'tool_used': tool,
                'success': True
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"  ✗ Fehler: {str(e)}")

            return {
                'text': None,
                'pages': 0,
                'processing_time': processing_time,
                'tool_used': tool,
                'success': False,
                'error': str(e)
            }

    def pdf_to_text_by_page(
        self,
        pdf_path: Path,
        domain: str = None,
        force_tool: OCRTool = None
    ) -> Dict:
        """
        Konvertiert ein PDF zu Text, gibt einzelne Seiten zurück

        Returns:
            Dict mit:
            - pages: List[str] - Text pro Seite
            - num_pages: int
            - processing_time: float
            - tool_used: str
            - success: bool
        """
        logger.info(f"Verarbeite PDF (seitenweise): {pdf_path.name}")

        if not pdf_path.exists():
            return {
                'pages': [],
                'num_pages': 0,
                'processing_time': 0,
                'tool_used': None,
                'success': False,
                'error': 'PDF nicht gefunden'
            }

        # Wähle Tool
        tool = self._choose_tool(domain, force_tool)
        logger.info(f"  Gewähltes Tool: {tool}" + (f" (Domain: {domain})" if domain else ""))

        start_time = time.time()

        try:
            images = self._pdf_to_images(pdf_path)
            if not images:
                return {
                    'pages': [],
                    'num_pages': 0,
                    'processing_time': time.time() - start_time,
                    'tool_used': tool,
                    'success': False,
                    'error': 'PDF-Konvertierung fehlgeschlagen'
                }

            page_texts = []

            for idx, image in enumerate(images):
                logger.debug(f"  Verarbeite Seite {idx + 1}/{len(images)}")

                if tool == 'mistral':
                    text = self._ocr_mistral(image)
                else:
                    text = self._ocr_tesseract(image)

                page_texts.append(text)

            processing_time = time.time() - start_time

            logger.info(f"  ✓ Erfolgreich in {processing_time:.2f}s")

            return {
                'pages': page_texts,
                'num_pages': len(page_texts),
                'processing_time': processing_time,
                'tool_used': tool,
                'success': True
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"  ✗ Fehler: {str(e)}")

            return {
                'pages': [],
                'num_pages': 0,
                'processing_time': processing_time,
                'tool_used': tool,
                'success': False,
                'error': str(e)
            }


# Singleton-Instanz
_ocr_handler = None


def get_ocr_handler(
    default_tool: OCRTool = 'auto',
    **kwargs
) -> OCRHandler:
    """
    Gibt eine Singleton-Instanz des OCRHandlers zurück

    Args:
        default_tool: 'tesseract', 'mistral', oder 'auto'
        **kwargs: Weitere Parameter für OCRHandler
    """
    global _ocr_handler
    if _ocr_handler is None:
        _ocr_handler = OCRHandler(default_tool=default_tool, **kwargs)
    return _ocr_handler


def reset_ocr_handler():
    """Setzt den Singleton zurück (nützlich für Tests)"""
    global _ocr_handler
    _ocr_handler = None
