"""LLM Service - Handles communication with Ollama or OpenAI"""
import logging
from typing import List, Dict, Any, Optional
import ollama
from openai import OpenAI

from app.utils.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Unified interface for LLM providers (Ollama or OpenAI).
    Allows switching between local and cloud LLMs via configuration.
    """
    
    def __init__(self):
        self.provider = settings.llm_provider
        
        if self.provider == "ollama":
            # Ollama client (local)
            self.ollama_client = ollama.Client(host=settings.ollama_base_url)
            self.model = settings.ollama_model
            logger.info(f"LLM Service initialized with Ollama: {self.model}")
        
        elif self.provider == "openai":
            # OpenAI client (cloud)
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            logger.info(f"LLM Service initialized with OpenAI: {self.model}")
        
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send chat messages to LLM and get response.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            temperature: Creativity (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum response length
        
        Returns:
            LLM response text
        """
        try:
            if self.provider == "ollama":
                return self._chat_ollama(messages, temperature)
            else:
                return self._chat_openai(messages, temperature, max_tokens)
        
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            raise
    
    def _chat_ollama(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Call Ollama API"""
        response = self.ollama_client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": temperature,
            }
        )
        return response['message']['content']
    
    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Call OpenAI API"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        response = self.openai_client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


# Singleton instance
llm_service = LLMService()
