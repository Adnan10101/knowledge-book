"""
LLM Integration module for summarization and question answering.
Supports multiple LLM providers:
1. Ollama (local) - completely free, runs locally
2. OpenRouter (API) - access 100+ models through unified interface
3. OpenAI (API) - with free credits or paid API key
4. Hugging Face Inference API (free tier) - requires API key
"""

import os
import requests
from typing import List, Dict, Optional
import streamlit as st


class LLMProvider:
    """Base class for LLM providers."""
    
    def summarize_and_answer(self, query: str, chunks: List[Dict]) -> str:
        """Return a summarized answer based on query and chunks."""
        raise NotImplementedError


class HuggingFaceInferenceAPI(LLMProvider):
    """
    Hugging Face Inference API provider.
    Free tier available at https://huggingface.co/inference-api
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_id = "meta-llama/Llama-2-7b-chat-hf"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
    
    def summarize_and_answer(self, query: str, chunks: List[Dict], max_tokens: int = 500) -> str:
        """
        Generate answer using Hugging Face Inference API.
        """
        try:
            # Prepare context from chunks
            context = self._prepare_context(chunks)
            
            # Build prompt
            prompt = f"""Based on the following context, answer the question concisely and accurately.

Context:
{context}

Question: {query}

Answer:"""
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.95,
                }
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
            else:
                return f"Error: {response.status_code} - {response.text}"
        
        except Exception as e:
            return f"Error calling HuggingFace API: {str(e)}"
    
    @staticmethod
    def _prepare_context(chunks: List[Dict]) -> str:
        """Prepare context from chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("metadata", {}).get("embedding_text", "")
            chapter = chunk.get("metadata", {}).get("chapter_name", "Unknown")
            context_parts.append(f"[Chunk {i}] (Chapter: {chapter})\n{text}\n")
        return "\n".join(context_parts)


class OllamaProvider(LLMProvider):
    """
    Ollama provider for local LLM inference.
    Download from https://ollama.ai
    Example: ollama pull mistral
    """
    
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def summarize_and_answer(self, query: str, chunks: List[Dict], max_tokens: int = 500) -> str:
        """
        Generate answer using local Ollama instance.
        """
        try:
            # Prepare context from chunks
            context = self._prepare_context(chunks)
            
            # Build prompt
            prompt = f"""Based on the following context, answer the question concisely and accurately.

Context:
{context}

Question: {query}

Answer:"""
            
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                return f"Error: {response.status_code}"
        
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Make sure Ollama is running on http://localhost:11434"
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    @staticmethod
    def _prepare_context(chunks: List[Dict]) -> str:
        """Prepare context from chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("metadata", {}).get("embedding_text", "")
            chapter = chunk.get("metadata", {}).get("chapter_name", "Unknown")
            context_parts.append(f"[Chunk {i}] (Chapter: {chapter})\n{text}\n")
        return "\n".join(context_parts)


class OpenRouterProvider(LLMProvider):
    """
    OpenRouter API provider for accessing 100+ LLM models.
    Unified interface to swap between different models easily.
    Requires API key from https://openrouter.io/keys
    """
    
    def __init__(self, api_key: str, model: str = "mistralai/mistral-7b-instruct:free"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def summarize_and_answer(self, query: str, chunks: List[Dict], max_tokens: int = 500) -> str:
        """
        Generate answer using OpenRouter API.
        """
        try:
            # Prepare context from chunks
            context = self._prepare_context(chunks)
            
            # Build messages
            messages = [
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Be concise and accurate."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            # OpenRouter requires these headers (they're strict about it)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost",
                "X-OpenRouter-Title": "Book RAG System",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                
                return f"Error: {response.status_code} - {response.text}"
        
        except Exception as e:
            return f"Error calling OpenRouter API: {str(e)}"
    
    @staticmethod
    def _prepare_context(chunks: List[Dict]) -> str:
        """Prepare context from chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("metadata", {}).get("embedding_text", "")
            chapter = chunk.get("metadata", {}).get("chapter_name", "Unknown")
            context_parts.append(f"[Chunk {i}] (Chapter: {chapter})\n{text}\n")
        return "\n".join(context_parts)


class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider.
    Requires API key from https://platform.openai.com/account/api-keys
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
    
    def summarize_and_answer(self, query: str, chunks: List[Dict], max_tokens: int = 500) -> str:
        """
        Generate answer using OpenAI API.
        """
        try:
            import openai
            
            openai.api_key = self.api_key
            
            # Prepare context from chunks
            context = self._prepare_context(chunks)
            
            # Build messages
            messages = [
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Be concise and accurate."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except ImportError:
            return "Error: OpenAI library not installed. Install with: pip install openai"
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
    
    @staticmethod
    def _prepare_context(chunks: List[Dict]) -> str:
        """Prepare context from chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("metadata", {}).get("embedding_text", "")
            chapter = chunk.get("metadata", {}).get("chapter_name", "Unknown")
            context_parts.append(f"[Chunk {i}] (Chapter: {chapter})\n{text}\n")
        return "\n".join(context_parts)


def get_llm_provider(provider_type: str, **kwargs) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Args:
        provider_type (str): "ollama", "openrouter", "openai", or "huggingface"
        **kwargs: Provider-specific arguments
    
    Returns:
        LLMProvider: Instance of the selected provider
    """
    
    # doesnt work
    if provider_type.lower() == "ollama":
        model = kwargs.get("model", "mistral")
        base_url = kwargs.get("base_url", "http://localhost:11434")
        return OllamaProvider(model, base_url)
    
    elif provider_type.lower() == "openrouter":
        api_key = kwargs.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OpenRouter API key required. Get one at https://openrouter.io/keys")
        model = kwargs.get("model", "mistralai/mistral-7b-instruct:free")
        return OpenRouterProvider(api_key, model)
    
    elif provider_type.lower() == "openai":
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        model = kwargs.get("model", "gpt-3.5-turbo")
        return OpenAIProvider(api_key, model)
    
    # doesnt work
    elif provider_type.lower() == "huggingface":
        api_key = kwargs.get("api_key") or os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("HuggingFace API key required. Set HUGGINGFACE_API_KEY environment variable.")
        return HuggingFaceInferenceAPI(api_key)
    
    else:
        raise ValueError(f"Unknown provider: {provider_type}. Supported: ollama, openrouter, openai, huggingface")


def generate_answer(
    query: str,
    chunks: List[Dict],
    provider_type: str = "ollama",
    max_tokens: int = 500,
    **provider_kwargs
) -> str:
    """
    Convenience function to generate an answer.
    
    Args:
        query (str): User's question
        chunks (List[Dict]): Retrieved context chunks
        provider_type (str): LLM provider to use
        max_tokens (int): Maximum tokens in response
        **provider_kwargs: Provider-specific arguments
    
    Returns:
        str: Generated answer
    """
    provider = get_llm_provider(provider_type, **provider_kwargs)
    return provider.summarize_and_answer(query, chunks, max_tokens)
