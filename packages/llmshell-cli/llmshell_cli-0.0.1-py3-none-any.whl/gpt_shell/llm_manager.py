"""LLM backend manager with fallback support."""

from typing import Optional, List, Tuple
from pathlib import Path

from gpt_shell.config import Config
from gpt_shell.llm_client import (
    LLMClient,
    GPT4AllClient,
    OpenAIClient,
    OllamaClient,
    CustomClient,
)


class LLMManager:
    """Manages LLM backends and provides fallback logic."""

    def __init__(self, config: Config):
        """
        Initialize LLM manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.current_client: Optional[LLMClient] = None
        self.backend_name: Optional[str] = None

    def get_client(self, backend: Optional[str] = None) -> LLMClient:
        """
        Get LLM client for specified backend.

        Args:
            backend: Backend name. If None, uses config default

        Returns:
            LLM client instance

        Raises:
            RuntimeError: If no backends are available
        """
        if backend is None:
            backend = self.config.get("llm_backend", "gpt4all")

        # Try requested backend first
        client = self._create_client(backend)
        if client and client.is_available():
            self.current_client = client
            self.backend_name = backend
            return client

        # If requested backend not available, try fallback order
        fallback_order = self._get_fallback_order(backend)
        for fallback_backend in fallback_order:
            client = self._create_client(fallback_backend)
            if client and client.is_available():
                self.current_client = client
                self.backend_name = fallback_backend
                return client

        # No backends available
        raise RuntimeError(
            "No LLM backends available. Please configure at least one backend:\n"
            "  - GPT4All: run 'llmshell model install' to download model\n"
            "  - OpenAI: set API key with 'llmshell config set backends.openai.api_key YOUR_KEY'\n"
            "  - Ollama: ensure Ollama is running locally\n"
            "  - Custom: configure custom API endpoint"
        )

    def _create_client(self, backend: str) -> Optional[LLMClient]:
        """
        Create client for specific backend.

        Args:
            backend: Backend name

        Returns:
            LLM client instance or None if configuration invalid
        """
        backend_config = self.config.get_backend_config(backend)

        try:
            if backend == "gpt4all":
                model_name = backend_config.get("model", "mistral-7b-instruct-v0.2.Q4_0.gguf")
                model_path = backend_config.get("model_path")
                
                # If no explicit path, check models directory
                if not model_path:
                    models_dir = self.config.get_models_dir()
                    potential_path = models_dir / model_name
                    if potential_path.exists():
                        model_path = str(models_dir)
                
                return GPT4AllClient(model_name=model_name, model_path=model_path)

            elif backend == "openai":
                api_key = backend_config.get("api_key")
                if not api_key:
                    return None
                model = backend_config.get("model", "gpt-4-turbo")
                base_url = backend_config.get("base_url")
                return OpenAIClient(api_key=api_key, model=model, base_url=base_url)

            elif backend == "ollama":
                model = backend_config.get("model", "llama3")
                api_url = backend_config.get("api_url", "http://localhost:11434")
                return OllamaClient(model=model, api_url=api_url)

            elif backend == "custom":
                api_url = backend_config.get("api_url")
                if not api_url:
                    return None
                headers = backend_config.get("headers", {})
                return CustomClient(api_url=api_url, headers=headers)

            else:
                return None

        except Exception:
            return None

    def _get_fallback_order(self, preferred: str) -> List[str]:
        """
        Get fallback order for backends.

        Args:
            preferred: Preferred backend (to exclude from fallbacks)

        Returns:
            List of backend names in fallback order
        """
        # Default fallback order: gpt4all -> ollama -> openai -> custom
        all_backends = ["gpt4all", "ollama", "openai", "custom"]
        
        # Remove preferred backend from fallbacks
        fallbacks = [b for b in all_backends if b != preferred]
        
        return fallbacks

    def check_backends(self) -> List[Tuple[str, bool, str]]:
        """
        Check status of all configured backends.

        Returns:
            List of tuples (backend_name, is_available, status_message)
        """
        results = []
        
        for backend in self.config.list_backends():
            client = self._create_client(backend)
            if client is None:
                results.append((backend, False, "Not configured"))
            elif client.is_available():
                results.append((backend, True, "Available"))
            else:
                error_msg = getattr(client, "error", "Not available")
                results.append((backend, False, error_msg))
        
        return results

    def generate_command(self, prompt: str, explain: bool = False, backend: Optional[str] = None) -> str:
        """
        Generate command using LLM.

        Args:
            prompt: Natural language prompt
            explain: Whether to include explanation
            backend: Specific backend to use (optional)

        Returns:
            Generated command
        """
        client = self.get_client(backend)
        return client.generate_command(prompt, explain)

    def get_current_backend(self) -> Optional[str]:
        """
        Get name of currently active backend.

        Returns:
            Backend name or None
        """
        return self.backend_name

    def download_gpt4all_model(self, model_name: Optional[str] = None) -> Path:
        """
        Download GPT4All model.

        Args:
            model_name: Model name to download. If None, uses config default

        Returns:
            Path to downloaded model

        Raises:
            RuntimeError: If download fails
        """
        if model_name is None:
            model_name = self.config.get("backends.gpt4all.model", "mistral-7b-instruct-v0.2.Q4_0.gguf")

        models_dir = self.config.get_models_dir()

        try:
            from gpt4all import GPT4All
            
            # GPT4All will download to its default location, then we can use it
            print(f"Downloading {model_name}...")
            print("This may take a few minutes depending on your internet connection.")
            
            model = GPT4All(
                model_name=model_name,
                model_path=str(models_dir),
                allow_download=True,
            )
            
            model_path = models_dir / model_name
            
            # Update config with model path
            self.config.set("backends.gpt4all.model_path", str(models_dir))
            
            return model_path

        except Exception as e:
            raise RuntimeError(f"Failed to download model: {e}")
