"""
Assembly Chain: Validated Variants → Final Document
Baut das finale Dokument aus validierten Varianten zusammen

LCEL-Kompatibilität:
    Kein LLM-Aufruf — Assembly ist reine Dokument-Aggregation.
    Die Chain ist via RunnableLambda als formales LCEL-Runnable verpackt.
"""
from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

from langchain_core.runnables import RunnableLambda

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)


class AssemblyChain:
    """
    Chain für Dokument-Assembly aus validierten Varianten
    """
    
    def __init__(self):
        """Initialisiert die Assembly Chain"""
        # RunnableLambda-Wrapper: macht AssemblyChain formal LCEL-kompatibel.
        # Assembly macht keinen LLM-Aufruf — nur Dokument-Aggregation.
        self._runnable = RunnableLambda(self.invoke)

        logger.info("AssemblyChain (LCEL-kompatibel) initialisiert")
    
    def assemble_document(
        self,
        segments_with_variants: List[Dict],
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Baut finales Dokument zusammen
        
        Args:
            segments_with_variants: Liste von Segmenten mit ihren validierten Varianten
            metadata: Optional metadata (PDF-Info, etc.)
        
        Returns:
            Dict mit assembled_document, statistics, success
        """
        logger.info(f"Assembliere Dokument aus {len(segments_with_variants)} Segmenten")
        
        assembled_segments = []
        statistics = {
            'total_segments': len(segments_with_variants),
            'segments_with_variants': 0,
            'total_variants': 0,
            'valid_variants': 0
        }
        
        for segment_data in segments_with_variants:
            original_segment = segment_data.get('original_segment', {})
            validated_variants = segment_data.get('validated_variants', [])
            
            # Filter nur valide Varianten
            valid_variants = [
                v for v in validated_variants
                if v.get('validation', {}).get('is_valid')
            ]
            
            statistics['total_variants'] += len(validated_variants)
            statistics['valid_variants'] += len(valid_variants)
            
            if len(valid_variants) > 0:
                statistics['segments_with_variants'] += 1
            
            assembled_segments.append({
                'original': original_segment.get('text', ''),
                'segment_type': original_segment.get('type', 'unknown'),
                'classification': segment_data.get('classification', {}),
                'num_variants': len(valid_variants),
                'variants': [
                    {
                        'variant_id': v.get('variant_id'),
                        'text': v.get('text'),
                        'validation_score': self._calculate_validation_score(v.get('validation', {})),
                        'solution': v.get('solution'),  # Musterantwort (kann None sein)
                    }
                    for v in valid_variants
                ]
            })
        
        # Erstelle Text-Output
        text_output = self._generate_text_output(assembled_segments, metadata)
        
        logger.info(
            f"✓ Dokument assembliert: {statistics['segments_with_variants']} Segmente mit "
            f"{statistics['valid_variants']} validen Varianten"
        )
        
        return {
            'assembled_document': {
                'segments': assembled_segments,
                'text_output': text_output,
                'metadata': metadata or {}
            },
            'statistics': statistics,
            'success': True
        }
    
    def _calculate_validation_score(self, validation: Dict) -> float:
        """Berechnet einen einfachen Validierungs-Score"""
        if not validation.get('is_valid'):
            return 0.0
        
        # Basiere Score auf Anzahl Issues (weniger = besser)
        num_issues = len(validation.get('issues', []))
        
        if num_issues == 0:
            return 1.0
        else:
            return max(0.0, 1.0 - (num_issues * 0.2))
    
    def _generate_text_output(
        self,
        assembled_segments: List[Dict],
        metadata: Dict = None
    ) -> str:
        """Generiert Text-Output des Dokuments"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("VARIANTEN-DOKUMENT")
        if metadata:
            lines.append(f"Original: {metadata.get('pdf_path', 'N/A')}")
            lines.append(f"Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)
        lines.append("")
        
        # Segmente
        for idx, segment in enumerate(assembled_segments, 1):
            lines.append(f"## Segment {idx}: {segment['segment_type'].upper()}")
            lines.append("")
            
            # Original
            lines.append("**Original:**")
            lines.append(segment['original'])
            lines.append("")
            
            # Varianten
            if segment['num_variants'] > 0:
                lines.append(f"**Varianten ({segment['num_variants']}):**")
                lines.append("")
                
                for variant in segment['variants']:
                    score = variant['validation_score']
                    lines.append(f"Variante {variant['variant_id']} (Score: {score:.2f}):")
                    lines.append(variant['text'])
                    lines.append("")
            else:
                lines.append("*Keine validen Varianten generiert*")
                lines.append("")
            
            lines.append("-" * 70)
            lines.append("")
        
        return "\n".join(lines)
    
    def save_to_file(
        self,
        assembled_document: Dict,
        output_path: Path
    ) -> Dict[str, Any]:
        """
        Speichert das assemblierte Dokument
        
        Args:
            assembled_document: Assembliertes Dokument
            output_path: Ziel-Pfad (ohne Extension)
        
        Returns:
            Dict mit saved_files, success
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        try:
            # 1. JSON (strukturiert)
            json_path = output_path.with_suffix('.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(assembled_document, f, indent=2, ensure_ascii=False)
            saved_files.append(str(json_path))
            logger.info(f"Gespeichert: {json_path}")
            
            # 2. Text (lesbar)
            txt_path = output_path.with_suffix('.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(assembled_document.get('text_output', ''))
            saved_files.append(str(txt_path))
            logger.info(f"Gespeichert: {txt_path}")
            
            return {
                'saved_files': saved_files,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")
            return {
                'saved_files': saved_files,
                'success': False,
                'error': str(e)
            }
    
    def invoke(self, input_data: Dict) -> Dict[str, Any]:
        """
        LangChain-kompatible invoke Methode
        
        Args:
            input_data: Dict mit 'segments_with_variants' und optional 'metadata'
        
        Returns:
            Dict mit assembly results
        """
        segments = input_data.get('segments_with_variants', [])
        metadata = input_data.get('metadata', {})
        
        return self.assemble_document(segments, metadata)


def get_assembly_chain() -> AssemblyChain:
    """Factory für AssemblyChain"""
    return AssemblyChain()