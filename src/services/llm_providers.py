"""
LLM Provider service for SystemMonitor.
Handles communication with various LLM providers (Ollama, OpenAI, etc.)
"""
import requests
from typing import List, Dict, Optional, Callable
import json


class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def chat(self, messages: List[Dict], model: str, **kwargs) -> str:
        """Send chat request and return response."""
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    BASE_URL = "http://localhost:11434"
    
    def __init__(self, base_url: str = None):
        super().__init__()
        self.base_url = base_url or self.BASE_URL
    
    def get_models(self) -> List[str]:
        """Get available models from Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m['name'] for m in models]
        except:
            pass
        return []
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def chat(self, messages: List[Dict], model: str, **kwargs) -> str:
        """Send chat request to Ollama."""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            'model': model,
            'messages': messages,
            'stream': False,
            'options': {
                'temperature': kwargs.get('temperature', 0.7),
                'num_predict': kwargs.get('max_tokens', 2000)
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('message', {}).get('content', '')
        
        raise Exception(f"Ollama error: {response.status_code}")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
    
    def chat(self, messages: List[Dict], model: str = "gpt-4", **kwargs) -> str:
        """Send chat request to OpenAI."""
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 2000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        
        raise Exception(f"OpenAI error: {response.status_code}")


class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider."""
    
    BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
    
    def chat(self, messages: List[Dict], model: str = "deepseek-chat", **kwargs) -> str:
        """Send chat request to DeepSeek."""
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 2000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        
        raise Exception(f"DeepSeek error: {response.status_code}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    BASE_URL = "https://api.anthropic.com/v1"
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
    
    def chat(self, messages: List[Dict], model: str = "claude-3-sonnet-20240229", **kwargs) -> str:
        """Send chat request to Anthropic."""
        url = f"{self.BASE_URL}/messages"
        
        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 2000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        
        raise Exception(f"Anthropic error: {response.status_code}")


class LLMService:
    """Service to manage multiple LLM providers."""
    
    PROVIDERS = {
        'ollama': OllamaProvider,
        'openai': OpenAIProvider,
        'deepseek': DeepSeekProvider,
        'anthropic': AnthropicProvider,
    }
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.current_provider: Optional[str] = None
        self.models: List[str] = []
        self.current_model: Optional[str] = None
    
    def initialize_provider(self, provider_name: str, api_key: str = None, **kwargs) -> bool:
        """Initialize a specific provider."""
        if provider_name not in self.PROVIDERS:
            return False
        
        try:
            provider_class = self.PROVIDERS[provider_name]
            
            if provider_name == 'ollama':
                provider = OllamaProvider(base_url=kwargs.get('base_url'))
                if provider.is_available():
                    self.providers[provider_name] = provider
                    self.current_provider = provider_name
                    self.models = provider.get_models()
                    if self.models:
                        self.current_model = self.models[-1]
                    return True
            else:
                if api_key:
                    provider = provider_class(api_key)
                    self.providers[provider_name] = provider
                    self.current_provider = provider_name
                    return True
        except Exception as e:
            print(f"Error initializing {provider_name}: {e}")
        
        return False
    
    def set_provider(self, provider_name: str) -> bool:
        """Switch to a different provider."""
        if provider_name in self.providers:
            self.current_provider = provider_name
            if provider_name == 'ollama':
                provider = self.providers[provider_name]
                self.models = provider.get_models()
                if self.models:
                    self.current_model = self.models[-1]
            return True
        return False
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """Send chat request to current provider."""
        if not self.current_provider or self.current_provider not in self.providers:
            raise Exception("No LLM provider available")
        
        provider = self.providers[self.current_provider]
        return provider.chat(messages, self.current_model, **kwargs)
    
    def is_available(self) -> bool:
        """Check if current provider is available."""
        return self.current_provider is not None
