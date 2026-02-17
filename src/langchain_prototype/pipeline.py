"""
Complete LangChain Pipeline
End-to-End Workflow: PDF → Varianten-Dokument
"""
from pathlib import Path
from typing import Dict, Any
import time

from common.config import Config
from common.logger import setup_logger
from langchain_prototype.chains.parsing_chain import get_parsing_chain
from langchain_prototype.chains.segmentation_chain import get_segmentation_chain
from langchain_prototype.chains.classification_chain import get_classification_chain
from langchain_prototype.chains.rewriting_chain import get_rewriting_chain
from langchain_prototype.chains.validation_chain import get_validation_chain
from langchain_prototype.chains.assembly_chain import get_assembly_chain

logger = setup_logger(__name__)


class LangChainPipeline:
    """
    Komplette Pipeline für Content-Variation
    """
    
    def __init__(
        self,
        domain: str = None,
        num_variants: int = 3
    ):
        """
        Args:
            domain: Optional domain (math, languages, economics)
            num_variants: Anzahl Varianten pro Segment
        """
        self.domain = domain
        self.num_variants = num_variants
        
        # Initialisiere alle Chains
        self.parsing_chain = get_parsing_chain(domain=domain)
        self.segmentation_chain = get_segmentation_chain()
        self.classification_chain = get_classification_chain()
        self.rewriting_chain = get_rewriting_chain(num_variants=num_variants)
        self.validation_chain = get_validation_chain()
        self.assembly_chain = get_assembly_chain()
        
        logger.info(f"LangChain Pipeline initialisiert (Domain: {domain or 'auto'}, Varianten: {num_variants})")
    
    def process_pdf(
        self,
        pdf_path: Path,
        output_path: Path = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet ein PDF komplett
        
        Args:
            pdf_path: Pfad zum Input-PDF
            output_path: Optional output path (default: data/output/langchain/)
        
        Returns:
            Dict mit results, statistics, output_files
        """
        logger.info(f"Starte Pipeline für: {pdf_path.name}")
        start_time = time.time()
        
        # Default output path
        if output_path is None:
            output_path = Config.DATA_OUTPUT_PATH / 'langchain' / pdf_path.stem
        
        pipeline_results = {}
        
        try:
            # ===== 1. PARSING =====
            logger.info("Step 1/6: Parsing PDF...")
            parse_result = self.parsing_chain.invoke({'pdf_path': str(pdf_path)})
            
            if not parse_result['success']:
                raise Exception(f"Parsing failed: {parse_result['metadata'].get('error')}")
            
            pipeline_results['parsing'] = parse_result['metadata']
            text = parse_result['text']
            
            # ===== 2. SEGMENTATION =====
            logger.info("Step 2/6: Segmentiere Text...")
            segment_result = self.segmentation_chain.invoke({'text': text})
            
            if not segment_result['success']:
                raise Exception(f"Segmentation failed: {segment_result['metadata'].get('error')}")
            
            pipeline_results['segmentation'] = segment_result['metadata']
            segments = segment_result['segments']
            
            # ===== 3. CLASSIFICATION + 4. REWRITING + 5. VALIDATION =====
            logger.info(f"Step 3-5/6: Verarbeite {len(segments)} Segmente...")
            
            segments_with_variants = []
            
            for idx, segment in enumerate(segments, 1):
                logger.info(f"  Segment {idx}/{len(segments)}")
                
                # 3. Klassifizierung
                classify_result = self.classification_chain.invoke({'segment': segment})
                
                if not classify_result['success']:
                    logger.warning(f"    Klassifizierung fehlgeschlagen, überspringe Segment")
                    continue
                
                classification = classify_result['classification']
                domain = classification.get('domain', 'general')
                
                # 4. Rewriting
                rewrite_result = self.rewriting_chain.invoke({
                    'segment': segment,
                    'domain': domain
                })
                
                if not rewrite_result['success']:
                    logger.warning(f"    Rewriting fehlgeschlagen, überspringe Segment")
                    continue
                
                # 5. Validation
                validation_result = self.validation_chain.invoke({
                    'original': rewrite_result['original'],
                    'variants': rewrite_result['variants'],
                    'domain': domain
                })
                
                segments_with_variants.append({
                    'original_segment': segment,
                    'classification': classification,
                    'validated_variants': validation_result['validated_variants'],
                    'validation_statistics': validation_result['statistics']
                })
            
            # ===== 6. ASSEMBLY =====
            logger.info("Step 6/6: Assembliere Dokument...")
            
            assembly_result = self.assembly_chain.invoke({
                'segments_with_variants': segments_with_variants,
                'metadata': {
                    'pdf_path': str(pdf_path),
                    'domain': self.domain,
                    'num_variants_requested': self.num_variants,
                    **pipeline_results['parsing']
                }
            })
            
            pipeline_results['assembly'] = assembly_result['statistics']
            
            # Speichere Output
            save_result = self.assembly_chain.save_to_file(
                assembly_result['assembled_document'],
                output_path
            )
            
            total_time = time.time() - start_time
            
            logger.info(f"✅ Pipeline abgeschlossen in {total_time:.2f}s")
            
            return {
                'success': True,
                'output_files': save_result['saved_files'],
                'statistics': {
                    **pipeline_results,
                    'total_time': total_time
                },
                'assembled_document': assembly_result['assembled_document']
            }
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Pipeline fehlgeschlagen: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'statistics': {
                    **pipeline_results,
                    'total_time': total_time
                }
            }


def get_pipeline(domain: str = None, num_variants: int = 3) -> LangChainPipeline:
    """Factory für Pipeline"""
    return LangChainPipeline(domain=domain, num_variants=num_variants)