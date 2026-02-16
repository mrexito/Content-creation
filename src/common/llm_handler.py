"""
LLM Handler für BFH-TI Inference Service
OpenAI-kompatible Schnittstelle zu Ollama
"""
from openai import OpenAI
from typing import Dict, List, Any, Optional
import time

from .config import Config
from .logger import setup_logger

logger = setup_logger(__name__)

class BFH_LLM_Handler:
    """
    Handler für BFH-LLM (OpenAI-kompatible API via Ollama)
    """
    
    def __init__(
        self,
        model: str = 'gpt-oss:120b',
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        Args:
            model: 'gpt-oss:120b', 'gemma3:4b', 'qwen3-vl:30b'
            temperature: 0.0 - 1.0
            max_tokens: Optional max tokens
        """
        if not Config.BFH_LLM_API_KEY:
            raise ValueError("BFH_LLM_API_KEY nicht in .env.dev gesetzt!")
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # OpenAI Client mit BFH Endpoint
        self.client = OpenAI(
            base_url=Config.BFH_LLM_ENDPOINT,
            api_key=Config.BFH_LLM_API_KEY
        )
        
        logger.info(f"BFH LLM Handler initialisiert (Model: {model}, Temp: {temperature})")
    
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
            temperature: Override default temperature
            max_tokens: Override default max_tokens
        
        Returns:
            Dict mit text, model, tokens, processing_time
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            processing_time = time.time() - start_time
            
            result = {
                'text': response.choices[0].message.content.strip(),
                'model': self.model,
                'tokens': {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                },
                'processing_time': processing_time,
                'success': True
            }
            
            logger.debug(
                f"LLM Response: {len(result['text'])} chars, "
                f"{result['tokens']['total']} tokens, "
                f"{processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LLM Error: {str(e)}")
            return {
                'text': None,
                'model': self.model,
                'tokens': None,
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    def generate_with_functions(
        self,
        prompt: str,
        functions: List[Dict],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generiert mit Function Calling
        
        Args:
            prompt: User prompt
            functions: Liste von Function-Definitionen
            system_prompt: Optional system prompt
        
        Returns:
            Dict mit text/function_call, model, tokens
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=[{"type": "function", "function": f} for f in functions],
                temperature=self.temperature
            )
            
            choice = response.choices[0]
            
            # Prüfe ob Function Call
            if choice.message.tool_calls:
                return {
                    'type': 'function_call',
                    'function_call': {
                        'name': choice.message.tool_calls[0].function.name,
                        'arguments': choice.message.tool_calls[0].function.arguments
                    },
                    'model': self.model,
                    'success': True
                }
            else:
                return {
                    'type': 'text',
                    'text': choice.message.content.strip(),
                    'model': self.model,
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Function calling error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Erstellt Embeddings (falls benötigt)
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model="embeddinggemma:300m",
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return []


# Singleton
_llm_handler = None

def get_llm_handler(
    model: str = 'gpt-oss:120b',
    **kwargs
) -> BFH_LLM_Handler:
    """Gibt Singleton-Instanz zurück"""
    global _llm_handler
    if _llm_handler is None:
        _llm_handler = BFH_LLM_Handler(model=model, **kwargs)
    return _llm_handler

def reset_llm_handler():
    """Reset Singleton (für Tests)"""
    global _llm_handler
    _llm_handler = None