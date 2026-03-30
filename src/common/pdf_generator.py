"""
PDF Generator: Erzeugt Aufgaben-PDF und Lösungs-PDF aus assemblierten Varianten.
LaTeX-Ausdrücke werden via matplotlib mathtext als PNG-Bilder eingebettet.
"""
import re
import struct
import tempfile
import os
from html import escape as _html_escape
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.figure as mfigure
import matplotlib.backends.backend_agg as magg

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image as RLImage, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black

from common.logger import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Math expression detection & splitting
# ---------------------------------------------------------------------------

# Matches display math ($$...$$  or  \[...\]) and inline math ($...$  or  \(...\))
# Display patterns must come first so $$ isn't consumed by the $..$ pattern.
_MATH_SPLIT_RE = re.compile(
    r'(\$\$.+?\$\$|\\\[.+?\\\]|\$.+?\$|\\\(.+?\\\))',
    re.DOTALL
)
_DISPLAY_RE = re.compile(r'^\$\$.+\$\$$|^\\\[.+\\\]$', re.DOTALL)


def _split_text_math(text: str) -> List[Tuple[str, str]]:
    """
    Split text into alternating ('text', ...) and ('math', ...) tuples.
    Math content has delimiters stripped.
    """
    parts = _MATH_SPLIT_RE.split(text)
    result = []
    for part in parts:
        if not part:
            continue
        m = _MATH_SPLIT_RE.fullmatch(part)
        if m:
            # Strip outer delimiters to get the raw LaTeX
            inner = re.sub(
                r'^\$\$|\$\$$|^\\\[|\\\]$|^\$|\$$|^\\\(|\\\)$',
                '', part
            ).strip()
            kind = 'display' if _DISPLAY_RE.match(part) else 'inline'
            result.append((kind, inner))
        else:
            result.append(('text', part))
    return result


# ---------------------------------------------------------------------------
# Math → PNG rendering via matplotlib mathtext
# ---------------------------------------------------------------------------

_MATH_DPI = 150


def _png_dimensions(path: str) -> Tuple[int, int]:
    """Read width/height from a PNG's IHDR chunk without extra dependencies."""
    with open(path, 'rb') as f:
        f.read(8)   # signature
        f.read(4)   # chunk length
        f.read(4)   # 'IHDR'
        w = struct.unpack('>I', f.read(4))[0]
        h = struct.unpack('>I', f.read(4))[0]
    return w, h


def _render_math(latex: str, fontsize_pt: float = 11.0) -> Optional[Tuple[str, float, float]]:
    """
    Render a LaTeX math string to a transparent PNG temp file using
    matplotlib's mathtext engine (no external LaTeX installation needed).

    Returns (filepath, width_pt, height_pt) on success, None on failure.
    """
    expr = f'${latex}$'
    # Use a standalone Figure to avoid global pyplot state
    fig = mfigure.Figure()
    canvas = magg.FigureCanvasAgg(fig)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    fig.patch.set_alpha(0)

    # Render at a generous initial figure size
    fig.set_size_inches(8, 1)
    render_fontsize = fontsize_pt

    try:
        t = ax.text(
            0.0, 0.5, expr,
            fontsize=render_fontsize,
            va='center', ha='left',
            transform=ax.transAxes,
            usetex=False,           # matplotlib mathtext, no LaTeX install needed
        )
        canvas.draw()
        bbox = t.get_window_extent(renderer=canvas.get_renderer())
    except Exception as e:
        logger.warning(f"Mathtext parse error for '{latex[:50]}': {e}")
        return None

    pad_px = 4
    w_inch = (bbox.width + 2 * pad_px) / _MATH_DPI
    h_inch = (bbox.height + 2 * pad_px) / _MATH_DPI
    fig.set_size_inches(max(w_inch, 0.05), max(h_inch, 0.1))

    try:
        fd, tmppath = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        fig.savefig(tmppath, format='png', dpi=_MATH_DPI,
                    transparent=True, bbox_inches='tight',
                    pad_inches=pad_px / _MATH_DPI)
    except Exception as e:
        logger.warning(f"Math PNG save failed: {e}")
        return None

    w_px, h_px = _png_dimensions(tmppath)
    w_pt = w_px / _MATH_DPI * 72
    h_pt = h_px / _MATH_DPI * 72
    return tmppath, w_pt, h_pt


# ---------------------------------------------------------------------------
# ReportLab helpers
# ---------------------------------------------------------------------------

def _xml_escape(text: str) -> str:
    """Escape XML special characters for ReportLab Paragraph content."""
    return _html_escape(text, quote=True)


def _make_styles() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        'doc_title': ParagraphStyle(
            'DocTitle', parent=base['Heading1'],
            fontSize=18, leading=22, spaceAfter=18,
            textColor=black, fontName='Helvetica-Bold',
        ),
        'section': ParagraphStyle(
            'Section', parent=base['Normal'],
            fontSize=11, leading=14, spaceBefore=14, spaceAfter=4,
            textColor=HexColor('#2563EB'), fontName='Helvetica-Bold',
        ),
        'solution_section': ParagraphStyle(
            'SolutionSection', parent=base['Normal'],
            fontSize=11, leading=14, spaceBefore=14, spaceAfter=4,
            textColor=HexColor('#059669'), fontName='Helvetica-Bold',
        ),
        'body': ParagraphStyle(
            'Body', parent=base['Normal'],
            fontSize=11, leading=16, spaceAfter=4, fontName='Helvetica',
        ),
    }


LABEL_MAP = {
    'title':    'Titel',
    'theory':   'Theorie',
    'task':     'Aufgabe',
    'example':  'Beispiel',
    'solution': 'Lösung',
    'unknown':  'Abschnitt',
}


def strip_latex_preamble(text: str) -> str:
    """
    Remove LaTeX document-structure commands from a text string.

    Strips \\documentclass, \\usepackage, \\begin{document}/\\end{document},
    \\begin{enumerate}/\\end{enumerate}, \\begin{itemize}/\\end{itemize},
    and \\section*{...} (replaced by its content).
    Replaces \\item with '- ' to preserve list structure as plain text.
    Does NOT strip inline math commands (\\frac, \\cdot, \\text, etc.).
    """
    # Remove \documentclass{...}
    text = re.sub(r'\\documentclass\{[^}]*\}', '', text)
    # Remove \usepackage[...]{...} or \usepackage{...}
    text = re.sub(r'\\usepackage(?:\[[^\]]*\])?\{[^}]*\}', '', text)
    # Remove \begin{document} and \end{document}
    text = re.sub(r'\\(?:begin|end)\{document\}', '', text)
    # Remove \begin{enumerate}, \end{enumerate}, \begin{itemize}, \end{itemize}
    text = re.sub(r'\\(?:begin|end)\{(?:enumerate|itemize)\}', '', text)
    # Replace \section*{content} with just content
    text = re.sub(r'\\section\*\{([^}]*)\}', r'\1', text)
    # Replace \item with '- '
    text = re.sub(r'\\item\s*', '- ', text)
    # Normalize doubled backslashes before LaTeX commands (\\cmd → \cmd)
    text = re.sub(r'\\{2,}([a-zA-Z])', r'\\\1', text)
    # Remove spurious \ext{ commands (OCR artefact), keeping the brace
    text = re.sub(r'\\ext\{', '{', text)
    return text.strip()


def _best_text(segment: Dict) -> str:
    """Return the text of the best valid variant, or the original."""
    variants = segment.get('variants', [])
    if variants:
        best = max(variants, key=lambda v: v.get('validation_score', 0.0))
        if best.get('text'):
            return strip_latex_preamble(best['text'])
    return strip_latex_preamble(segment.get('original', ''))


PROMPT_LEAK_MARKERS = [
    "Erstelle eine inhaltlich",
    "Erstelle ein inhaltlich",
    "DEUTLICH anders",
    "inhaltlich äquivalentes",
    "inhaltlich gleichwertige",
]


def _is_prompt_leak(text: str) -> bool:
    """Return True if the segment text contains prompt template fragments."""
    return any(marker in text for marker in PROMPT_LEAK_MARKERS)


# ---------------------------------------------------------------------------
# Mixed text → ReportLab flowables
# ---------------------------------------------------------------------------

def _text_to_flowables(
    text: str,
    style: ParagraphStyle,
    tmpfiles: List[str],
    body_fontsize: float = 11.0,
) -> List:
    """
    Convert a text string (possibly containing LaTeX math) into a list of
    ReportLab flowables.

    Inline math ($...$  or  \\(...\\)) → <img/> embedded in a Paragraph.
    Display math ($$...$$  or  \\[...\\]) → a centred RLImage flowable.
    Plain text → Paragraph.
    """
    parts = _split_text_math(text)

    # Check if there is any math at all
    has_math = any(k in ('inline', 'display') for k, _ in parts)

    if not has_math:
        # Fast path: plain text paragraph
        safe = _xml_escape(text).replace('\n', '<br/>')
        return [Paragraph(safe, style)]

    flowables: List = []
    inline_buf: List[str] = []   # accumulate inline parts into one Paragraph

    def flush_inline():
        content = ''.join(inline_buf).strip()
        if content:
            flowables.append(Paragraph(content, style))
        inline_buf.clear()

    for kind, content in parts:
        if kind == 'text':
            safe = _xml_escape(content).replace('\n', '<br/>')
            inline_buf.append(safe)

        elif kind == 'inline':
            rendered = _render_math(content, body_fontsize)
            if rendered:
                tmppath, w_pt, h_pt = rendered
                tmpfiles.append(tmppath)
                # Scale down if too wide (max ~72% of A4 text width ≈ 395pt)
                max_w = 395
                if w_pt > max_w:
                    scale = max_w / w_pt
                    w_pt = int(max_w)
                    h_pt = int(h_pt * scale)
                inline_buf.append(
                    f'<img src="{tmppath}" width="{w_pt:.0f}" '
                    f'height="{h_pt:.0f}" valign="middle"/>'
                )
            else:
                # Fallback: monospace plain text
                inline_buf.append(
                    f'<font name="Courier">{_xml_escape(content)}</font>'
                )

        elif kind == 'display':
            # Flush any pending inline content first
            flush_inline()
            rendered = _render_math(content, body_fontsize * 1.3)
            if rendered:
                tmppath, w_pt, h_pt = rendered
                tmpfiles.append(tmppath)
                max_w = 395
                if w_pt > max_w:
                    scale = max_w / w_pt
                    w_pt = int(max_w)
                    h_pt = int(h_pt * scale)
                img = RLImage(tmppath, width=w_pt, height=h_pt)
                img.hAlign = 'CENTER'
                flowables.append(Spacer(1, 4))
                flowables.append(img)
                flowables.append(Spacer(1, 4))
            else:
                inline_buf.append(
                    f'<font name="Courier">{_xml_escape(content)}</font>'
                )

    flush_inline()
    return flowables


# ---------------------------------------------------------------------------
# Core PDF builder
# ---------------------------------------------------------------------------

def _build_pdf(
    segments: List[Dict],
    output_path: Path,
    doc_title: str,
    include_solutions: bool,
) -> bool:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    styles = _make_styles()
    tmpfiles: List[str] = []   # temp PNG files to clean up afterwards

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2.5 * cm,  bottomMargin=2.5 * cm,
    )

    story = []
    story.append(Paragraph(_xml_escape(doc_title), styles['doc_title']))
    story.append(HRFlowable(width='100%', thickness=1,
                             color=HexColor('#E5E7EB'), spaceAfter=12))

    task_counter = 0
    solution_counter = 0

    for idx, segment in enumerate(segments):
        seg_type = segment.get('segment_type', 'unknown').lower()
        if seg_type == 'solution' and not include_solutions:
            continue

        text = _best_text(segment)
        if _is_prompt_leak(text):
            logger.warning(f"Prompt-Leak erkannt in Segment {idx}, Segment wird übersprungen.")
            continue

        if seg_type == 'task':
            task_counter += 1
            label = f"Aufgabe {task_counter}"
            header_style = styles['section']
        elif seg_type == 'solution':
            solution_counter += 1
            label = f"Lösung {solution_counter}"
            header_style = styles['solution_section']
        else:
            label = LABEL_MAP.get(seg_type, 'Abschnitt')
            header_style = styles['section']

        story.append(Paragraph(_xml_escape(label), header_style))

        if text:
            story.extend(
                _text_to_flowables(text, styles['body'], tmpfiles,
                                   body_fontsize=11.0)
            )
        else:
            story.append(Paragraph('<i>Kein Inhalt verfügbar.</i>', styles['body']))

        # Musterantwort der besten Variante ausgeben (nur im Lösungs-PDF)
        if include_solutions and seg_type != 'solution':
            variants = segment.get('variants', [])
            if variants:
                best_variant = max(variants, key=lambda v: v.get('validation_score', 0.0))
                solution_text = best_variant.get('solution')
                if solution_text and solution_text.strip() and solution_text.strip() != '–':
                    story.append(Paragraph(
                        _xml_escape('Musterantwort:'),
                        styles['solution_section']
                    ))
                    story.extend(
                        _text_to_flowables(solution_text.strip(), styles['body'], tmpfiles,
                                           body_fontsize=11.0)
                    )

        story.append(Spacer(1, 4))

    if len(story) <= 2:
        story.append(Paragraph(
            '<i>Keine Inhalte in dieser Kategorie vorhanden.</i>',
            styles['body']
        ))

    try:
        doc.build(story)
        logger.info(f"PDF gespeichert: {output_path}")
        return True
    except Exception as e:
        logger.error(f"PDF build fehlgeschlagen: {e}")
        return False
    finally:
        # Clean up temporary PNG files
        for f in tmpfiles:
            try:
                os.unlink(f)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class PdfGenerator:
    """Erzeugt Aufgaben- und Lösungs-PDFs aus dem assemblierten Dokument."""

    def generate_tasks_pdf(
        self,
        assembled_document: Dict[str, Any],
        output_path: Path,
    ) -> bool:
        """
        Erzeugt ein PDF mit Aufgaben (ohne Lösungen).
        Segment-Typen 'solution' werden herausgefiltert.
        """
        segments = assembled_document.get('segments', [])
        metadata = assembled_document.get('metadata', {})
        pdf_name = Path(metadata.get('pdf_path', 'Dokument')).stem
        logger.info(f"Generiere Aufgaben-PDF: {output_path}")
        try:
            return _build_pdf(segments, output_path,
                              f"Aufgaben – {pdf_name}",
                              include_solutions=False)
        except Exception as e:
            logger.error(f"Aufgaben-PDF fehlgeschlagen: {e}")
            return False

    def generate_solutions_pdf(
        self,
        assembled_document: Dict[str, Any],
        output_path: Path,
    ) -> bool:
        """
        Erzeugt ein PDF mit Aufgaben UND Lösungen.
        Alle Segment-Typen werden eingeschlossen.
        """
        segments = assembled_document.get('segments', [])
        metadata = assembled_document.get('metadata', {})
        pdf_name = Path(metadata.get('pdf_path', 'Dokument')).stem
        logger.info(f"Generiere Lösungs-PDF: {output_path}")
        try:
            return _build_pdf(segments, output_path,
                              f"Aufgaben & Lösungen – {pdf_name}",
                              include_solutions=True)
        except Exception as e:
            logger.error(f"Lösungs-PDF fehlgeschlagen: {e}")
            return False
