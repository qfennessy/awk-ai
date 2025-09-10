#!/usr/bin/env python3
"""
AI Provider implementations for PyAwk
Supports multiple AI services: Anthropic, OpenAI, Gemini, and local models
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Optional


class AIProvider:
    """Base class for AI service providers"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or self.get_api_key()
    
    def get_api_key(self):
        """Get API key from environment or config"""
        raise NotImplementedError
    
    def call_api(self, prompt, max_tokens=100):
        """Make authenticated API call"""
        raise NotImplementedError


class AnthropicProvider(AIProvider):
    """Anthropic Claude API implementation"""
    
    def get_api_key(self):
        """Get Anthropic API key from environment"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            # Try reading from config file
            try:
                with open(os.path.expanduser('~/.pyawk/config.json'), 'r') as f:
                    config = json.load(f)
                    api_key = config.get('anthropic_api_key')
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        return api_key
    
    def call_api(self, prompt, max_tokens=100):
        """Make authenticated call to Anthropic API"""
        if not self.api_key:
            return None  # Fall back to simulation
            
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-haiku-20240307",  # Using Haiku for cost efficiency
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": str(prompt)}
            ]
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['content'][0]['text'].strip()
                
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, json.JSONDecodeError):
            return None  # Fall back to simulation


class OpenAIProvider(AIProvider):
    """OpenAI GPT API implementation"""
    
    def get_api_key(self):
        """Get OpenAI API key from environment"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            try:
                with open(os.path.expanduser('~/.pyawk/config.json'), 'r') as f:
                    config = json.load(f)
                    api_key = config.get('openai_api_key')
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        return api_key
    
    def call_api(self, prompt, max_tokens=100):
        """Make authenticated call to OpenAI API"""
        if not self.api_key:
            return None  # Fall back to simulation
            
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": str(prompt)}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content'].strip()
                
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, json.JSONDecodeError):
            return None  # Fall back to simulation


class GeminiProvider(AIProvider):
    """Google Gemini API implementation"""
    
    def get_api_key(self):
        """Get Gemini API key from environment"""
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            try:
                with open(os.path.expanduser('~/.pyawk/config.json'), 'r') as f:
                    config = json.load(f)
                    api_key = config.get('gemini_api_key') or config.get('google_api_key')
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        return api_key
    
    def call_api(self, prompt, max_tokens=100):
        """Make authenticated call to Gemini API"""
        if not self.api_key:
            return None  # Fall back to simulation
            
        # Use gemini-1.5-flash for better availability and performance
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": str(prompt)}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7
            }
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
                
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, json.JSONDecodeError):
            return None  # Fall back to simulation


class LocalAIProvider(AIProvider):
    """Local AI server (like Ollama) implementation"""
    
    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or os.getenv('LOCAL_AI_URL', 'http://localhost:11434')
        self.model = model or os.getenv('LOCAL_AI_MODEL', 'llama2')
        super().__init__(api_key=None)
    
    def get_api_key(self):
        return None  # Local AI doesn't need authentication
    
    def call_api(self, prompt, max_tokens=100):
        """Call local AI server"""
        url = f"{self.base_url}/api/generate"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "prompt": str(prompt),
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['response'].strip()
                
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, json.JSONDecodeError):
            return None  # Fall back to simulation


class SimulatedProvider(AIProvider):
    """Fallback simulated AI provider for demo purposes"""
    
    def get_api_key(self):
        return None  # No API key needed for simulation
    
    def call_api(self, prompt, max_tokens=100) -> Optional[str]:
        """Return simulated responses based on prompt patterns"""
        prompt_lower = str(prompt).lower()
        
        # Simple pattern matching for demo purposes
        if "sentiment" in prompt_lower:
            text = prompt_lower.split("text:")[-1].strip() if "text:" in prompt_lower else prompt_lower
            if any(word in text for word in ["love", "amazing", "great", "perfect", "excited", "beautiful"]):
                return "positive"
            elif any(word in text for word in ["hate", "terrible", "awful", "bad", "frustrated", "stressful"]):
                return "negative"
            else:
                return "neutral"
        
        elif "classify" in prompt_lower and "categories" in prompt_lower:
            text = prompt_lower.split("text:")[-1].strip() if "text:" in prompt_lower else prompt_lower
            if any(word in text for word in ["discover", "species", "ocean", "earthquake"]):
                return "science"
            elif any(word in text for word in ["stock", "market", "economic", "budget", "layoffs"]):
                return "business" 
            elif any(word in text for word in ["championship", "basketball", "wins"]):
                return "sports"
            elif any(word in text for word in ["ai", "technology", "tech", "healthcare"]):
                return "technology"
            elif any(word in text for word in ["political", "leaders", "climate", "policies"]):
                return "politics"
            elif any(word in text for word in ["celebrity", "chef", "restaurant"]):
                return "entertainment"
            else:
                return "general"
        
        elif "translate" in prompt_lower and "spanish" in prompt_lower:
            # Simple translation examples
            text = prompt_lower.split(":")[-1].strip()
            translations = {
                "i love this": "me encanta esto",
                "hello": "hola", 
                "good morning": "buenos días",
                "thank you": "gracias",
                "laptop": "portátil",
                "headphones": "auriculares",
                "phone": "teléfono"
            }
            for eng, esp in translations.items():
                if eng in text:
                    return text.replace(eng, esp)
            return "traducción simulada"
        
        elif "extract" in prompt_lower and "person" in prompt_lower:
            text = str(prompt).split("Text:")[-1] if "Text:" in str(prompt) else str(prompt)
            names = []
            # Simple name detection
            import re
            name_patterns = [r'\b[A-Z][a-z]+ [A-Z][a-z]+\b']
            for pattern in name_patterns:
                names.extend(re.findall(pattern, text))
            return ", ".join(names) if names else "none"
        
        elif "summarize" in prompt_lower:
            return "Brief summary of the content"
        
        elif "math" in prompt_lower or "problem" in prompt_lower:
            # Simple math extraction
            text = str(prompt).lower()
            if "15" in text and "7" in text:
                return "8"
            return "42"  # Default answer to everything
        
        elif "fact" in prompt_lower or ("true or false" in prompt_lower):
            text = str(prompt).lower()
            if "pacific ocean" in text and "largest" in text:
                return "true"
            elif "cats" in text and "fly" in text:
                return "false"
            return "uncertain"
        
        else:
            return "AI-generated response: " + str(prompt)[:50] + "..."


# Global AI provider instance
_ai_provider = None

def get_ai_provider() -> AIProvider:
    """Get or create the AI provider instance"""
    global _ai_provider
    
    if _ai_provider is None:
        # Try providers in order of preference
        provider = os.getenv('PYAWK_AI_PROVIDER', '').lower()
        
        if provider == 'anthropic' or os.getenv('ANTHROPIC_API_KEY'):
            _ai_provider = AnthropicProvider()
        elif provider == 'openai' or os.getenv('OPENAI_API_KEY'):
            _ai_provider = OpenAIProvider()
        elif provider == 'gemini' or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY'):
            _ai_provider = GeminiProvider()
        elif provider == 'local' or os.getenv('LOCAL_AI_URL'):
            _ai_provider = LocalAIProvider()
        else:
            # Check config file for any API keys
            try:
                with open(os.path.expanduser('~/.pyawk/config.json'), 'r') as f:
                    config = json.load(f)
                    if config.get('anthropic_api_key'):
                        _ai_provider = AnthropicProvider()
                    elif config.get('openai_api_key'):
                        _ai_provider = OpenAIProvider()
                    elif config.get('gemini_api_key') or config.get('google_api_key'):
                        _ai_provider = GeminiProvider()
                    else:
                        _ai_provider = SimulatedProvider()
            except (FileNotFoundError, json.JSONDecodeError):
                _ai_provider = SimulatedProvider()
    
    return _ai_provider


def reset_provider():
    """Reset the provider (useful for testing or switching providers)"""
    global _ai_provider
    _ai_provider = None