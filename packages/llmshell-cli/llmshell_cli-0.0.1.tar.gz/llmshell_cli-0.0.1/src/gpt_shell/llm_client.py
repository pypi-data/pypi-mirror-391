"""LLM client abstraction for multiple backends."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json


SYSTEM_PROMPT = """You are a helpful Linux/Unix shell command generator. 
Your task is to convert natural language requests into valid shell commands.

Rules:
1. Output ONLY the command, no explanations unless specifically asked
2. Use safe, standard Unix/Linux commands
3. Prefer common tools (ls, grep, find, docker, etc.)
4. If the request is unclear, output the most likely command
5. For destructive operations (rm, etc.), include safety flags when possible

Examples:
Input: "list all docker containers"
Output: docker ps -a

Input: "find all python files in current directory"
Output: find . -name "*.py"

Input: "show disk usage"
Output: df -h

Now, respond to the user's request with just the command."""


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_command(self, prompt: str, explain: bool = False) -> str:
        """
        Generate a shell command from natural language prompt.

        Args:
            prompt: Natural language description
            explain: If True, include explanation

        Returns:
            Generated command or command with explanation
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this client is available and properly configured.

        Returns:
            True if available, False otherwise
        """
        pass


class GPT4AllClient(LLMClient):
    """GPT4All local LLM client."""

    def __init__(self, model_name: str, model_path: Optional[str] = None):
        """
        Initialize GPT4All client.

        Args:
            model_name: Name of the model
            model_path: Path to model file (optional)
        """
        self.model_name = model_name
        self.model_path = model_path
        self.model = None
        self._available = False
        self._initialize()

    def _initialize(self):
        """Initialize GPT4All model."""
        try:
            from gpt4all import GPT4All
            self.model = GPT4All(
                model_name=self.model_name,
                model_path=self.model_path,
                allow_download=False,  # Don't auto-download, we'll handle this
            )
            self._available = True
        except Exception as e:
            self._available = False
            self.error = str(e)

    def generate_command(self, prompt: str, explain: bool = False) -> str:
        """Generate command using GPT4All."""
        if not self.is_available():
            raise RuntimeError("GPT4All client is not available")

        if explain:
            user_prompt = f"{prompt}\n\nProvide the command and a brief explanation."
        else:
            user_prompt = prompt

        try:
            with self.model.chat_session(system_prompt=SYSTEM_PROMPT):
                response = self.model.generate(user_prompt, max_tokens=200, temp=0.1)
                
                # Extract just the command (before ### or other delimiters)
                cleaned_response = response.strip()
                
                # Split by common delimiters
                for delimiter in ['###', '```', '\n\n', 'End of']:
                    if delimiter in cleaned_response:
                        cleaned_response = cleaned_response.split(delimiter)[0].strip()
                        break
                
                return cleaned_response
        except Exception as e:
            raise RuntimeError(f"Error generating command: {e}")

    def is_available(self) -> bool:
        """Check if GPT4All is available."""
        return self._available


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo", base_url: Optional[str] = None):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model name
            base_url: Optional custom base URL
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = None
        self._available = False
        self._initialize()

    def _initialize(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            if self.api_key:
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self.client = OpenAI(**kwargs)
                self._available = True
            else:
                self._available = False
        except Exception as e:
            self._available = False
            self.error = str(e)

    def generate_command(self, prompt: str, explain: bool = False) -> str:
        """Generate command using OpenAI."""
        if not self.is_available():
            raise RuntimeError("OpenAI client is not available")

        if explain:
            user_prompt = f"{prompt}\n\nProvide the command and a brief explanation."
        else:
            user_prompt = prompt

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Error generating command: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self._available and self.client is not None


class OllamaClient(LLMClient):
    """Ollama API client."""

    def __init__(self, model: str, api_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.

        Args:
            model: Model name
            api_url: Ollama API URL
        """
        self.model = model
        self.api_url = api_url.rstrip("/")
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Check if Ollama is available."""
        try:
            import requests
            response = requests.get(f"{self.api_url}/api/tags", timeout=2)
            if response.status_code == 200:
                # Check if our model is available
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                self._available = any(self.model in name for name in model_names)
            else:
                self._available = False
        except Exception:
            self._available = False

    def generate_command(self, prompt: str, explain: bool = False) -> str:
        """Generate command using Ollama."""
        if not self.is_available():
            raise RuntimeError("Ollama client is not available")

        import requests

        if explain:
            user_prompt = f"{prompt}\n\nProvide the command and a brief explanation."
        else:
            user_prompt = prompt

        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{SYSTEM_PROMPT}\n\nUser request: {user_prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 200,
                    }
                },
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Error generating command: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        if not self._available:
            self._check_availability()
        return self._available


class CustomClient(LLMClient):
    """Custom API client for generic LLM endpoints."""

    def __init__(self, api_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize custom API client.

        Args:
            api_url: API endpoint URL
            headers: Optional headers (e.g., Authorization)
        """
        self.api_url = api_url
        self.headers = headers or {}
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Check if custom API is available."""
        try:
            import requests
            response = requests.get(self.api_url, headers=self.headers, timeout=2)
            self._available = response.status_code in [200, 401, 405]  # Endpoint exists
        except Exception:
            self._available = False

    def generate_command(self, prompt: str, explain: bool = False) -> str:
        """Generate command using custom API."""
        if not self.is_available():
            raise RuntimeError("Custom API client is not available")

        import requests

        if explain:
            user_prompt = f"{prompt}\n\nProvide the command and a brief explanation."
        else:
            user_prompt = prompt

        try:
            # Assume OpenAI-compatible format
            response = requests.post(
                self.api_url,
                headers={**self.headers, "Content-Type": "application/json"},
                json={
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.1,
                },
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            
            # Try different response formats
            if "choices" in result:
                return result["choices"][0]["message"]["content"].strip()
            elif "response" in result:
                return result["response"].strip()
            else:
                return str(result)
        except Exception as e:
            raise RuntimeError(f"Error generating command: {e}")

    def is_available(self) -> bool:
        """Check if custom API is available."""
        if not self._available:
            self._check_availability()
        return self._available
