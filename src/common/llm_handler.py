"""
Multi-Provider LLM Handler
Unterstützt: OpenAI (Entwicklung) und BFH-LLM (Production)
Einfach austauschbar via Config
"""
from openai import OpenAI
from typing import Dict, List, Any, Optional, Literal
import time
import json
import re
import ast

from common.config import Config
from common.logger import setup_logger

logger = setup_logger(__name__)

LLMProvider = Literal['openai', 'bfh', 'auto']


class LLMHandler:
    """
    Universeller LLM-Handler für OpenAI und BFH-LLM
    """
    
    def __init__(
        self,
        provider: LLMProvider = 'auto',
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        Args:
            provider: 'openai', 'bfh', oder 'auto' (auto-detect)
            model: Model name (provider-spezifisch)
            temperature: 0.0 - 1.0
            max_tokens: Optional max tokens
        """
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Wenn 'auto', nutze Config.LLM_PROVIDER
        if provider == 'auto':
            if Config.LLM_PROVIDER and Config.LLM_PROVIDER != 'auto':
                provider = Config.LLM_PROVIDER
                logger.info(f"Provider explizit gesetzt in Config: {provider}")
            else:
                provider = self._auto_detect_provider()
        
        self.provider = provider
        
        # Provider-spezifische Initialisierung
        if provider == 'openai':
            if not Config.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY nicht gesetzt! "
                    "Trage deinen Key in .env.dev ein."
                )
            
            self.model = model or Config.OPENAI_MODEL or 'gpt-4o-mini'
            self._client = OpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info(f"🟢 OpenAI LLM aktiviert (Model: {self.model})")
        
        elif provider == 'bfh':
            if not Config.BFH_LLM_API_KEY:
                raise ValueError(
                    "BFH_LLM_API_KEY nicht gesetzt! "
                    "Trage deinen BFH PAT in .env.dev ein."
                )
            
            self.model = model or Config.BFH_LLM_MODEL or 'gpt-oss:120b'
            self._client = OpenAI(
                base_url=Config.BFH_LLM_ENDPOINT,
                api_key=Config.BFH_LLM_API_KEY
            )
            logger.info(f"🔵 BFH-LLM aktiviert (Model: {self.model})")
        
        else:
            raise ValueError(f"Unbekannter Provider: {provider}. Nutze 'openai' oder 'bfh'.")
    
    def _auto_detect_provider(self) -> LLMProvider:
        """Auto-detect welcher Provider verfügbar ist"""
        if Config.BFH_LLM_API_KEY:
            logger.info("Auto-detect: BFH-LLM Token gefunden → BFH")
            return 'bfh'
        elif Config.OPENAI_API_KEY:
            logger.info("Auto-detect: OpenAI Token gefunden → OpenAI")
            return 'openai'
        else:
            raise ValueError(
                "Kein LLM-Token gefunden! "
                "Setze OPENAI_API_KEY oder BFH_LLM_API_KEY in .env.dev"
            )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generiert Text-Completion
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default
            max_tokens: Override default
        
        Returns:
            Dict mit text, model, provider, tokens, processing_time, success
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            processing_time = time.time() - start_time
            
            result = {
                'text': response.choices[0].message.content.strip(),
                'model': self.model,
                'provider': self.provider,
                'tokens': {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                },
                'processing_time': processing_time,
                'success': True
            }
            
            logger.debug(
                f"[{self.provider.upper()}] {len(result['text'])} chars, "
                f"{result['tokens']['total']} tokens, {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"[{self.provider.upper()}] Error: {str(e)}")
            return {
                'text': None,
                'model': self.model,
                'provider': self.provider,
                'tokens': None,
                'processing_time': processing_time,
                'success': False,
                'error': str(e)
            }
    
    def generate_structured(
        self,
        prompt: str,
        response_format: Dict,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generiert strukturierte Outputs (JSON)
        
        Args:
            prompt: User prompt
            response_format: JSON schema (als Beispiel)
            system_prompt: Optional system prompt
        
        Returns:
            Dict mit parsed_data (JSON), raw_text, success
        """
        # Prompt anpassen für JSON
        json_instruction = (
            f"\n\nWICHTIG: Antworte NUR mit gültigem JSON. "
            f"Keine Markdown-Formatierung, keine Backticks. "
            f"Escape alle Backslashes in Strings korrekt (z.B. '\\text' wird zu '\\\\text'). "
            f"\nBeispiel-Format: {json.dumps(response_format, indent=2)}"
        )
        
        result = self.generate(
            prompt + json_instruction,
            system_prompt
        )
        
        if not result['success']:
            return {
                'parsed_data': None,
                'raw_text': None,
                'success': False,
                'error': result.get('error'),
                'provider': self.provider
            }
        
        # Parse JSON
        try:
            # Entferne mögliche Markdown-Backticks
            text = result['text'].strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            # Versuche normales Parsing
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                # Fallback: Escape Backslashes manuell
                logger.warning("JSON-Parse fehlgeschlagen, versuche mit escaped Backslashes")
                # Nur Backslashes escapen, die nicht schon escaped sind
                text_escaped = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)
                parsed = json.loads(text_escaped)
            
            return {
                'parsed_data': parsed,
                'raw_text': result['text'],
                'model': result['model'],
                'provider': result['provider'],
                'tokens': result['tokens'],
                'success': True
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Raw text: {result['text']}")
            
            # Versuche JSON zu reparieren
            try:
                # Letzte Hoffnung: ast.literal_eval als Fallback
                logger.warning("Versuche ast.literal_eval als Fallback")
                text_cleaned = text.replace('null', 'None').replace('true', 'True').replace('false', 'False')
                parsed = ast.literal_eval(text_cleaned)
                
                return {
                    'parsed_data': parsed,
                    'raw_text': result['text'],
                    'model': result['model'],
                    'provider': result['provider'],
                    'success': True,
                    'warning': 'Parsed mit Fallback-Methode'
                }
            except (ValueError, SyntaxError):
                pass
            
            # Komplett fehlgeschlagen
            return {
                'parsed_data': None,
                'raw_text': result['text'],
                'success': False,
                'error': f'Invalid JSON: {str(e)}',
                'provider': self.provider
            }
    
    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Batch-Verarbeitung mehrerer Prompts
        
        Args:
            prompts: Liste von Prompts
            system_prompt: Optional system prompt für alle
            show_progress: Zeige Fortschritt
        
        Returns:
            Liste von Result-Dicts
        """
        results = []
        total = len(prompts)
        
        for idx, prompt in enumerate(prompts, 1):
            if show_progress:
                logger.info(f"Batch Progress: {idx}/{total}")
            
            result = self.generate(prompt, system_prompt)
            results.append(result)
        
        # Summary
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"Batch Complete: {success_count}/{total} erfolgreich")
        
        return results
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Erstellt Embeddings
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            # Provider-spezifische Embedding-Modelle
            if self.provider == 'openai':
                embedding_model = 'text-embedding-3-small'
            else:  # bfh
                embedding_model = 'embeddinggemma:300m'
            
            response = self._client.embeddings.create(
                model=embedding_model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return []


# Singleton
_llm_handler = None

def get_llm_handler(
    provider: LLMProvider = 'auto',
    **kwargs
) -> LLMHandler:
    """
    Gibt Singleton-Instanz zurück
    
    Args:
        provider: 'openai', 'bfh', 'auto'
        **kwargs: Weitere Parameter (model, temperature, etc.)
    
    Returns:
        LLMHandler Instanz
    """
    global _llm_handler
    if _llm_handler is None:
        _llm_handler = LLMHandler(provider=provider, **kwargs)
    return _llm_handler

def reset_llm_handler():
    """Reset Singleton (für Tests/Provider-Wechsel)"""
    global _llm_handler
    _llm_handler = None