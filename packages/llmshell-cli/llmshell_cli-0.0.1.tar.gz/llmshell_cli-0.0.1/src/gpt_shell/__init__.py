"""llmshell-cli: A Python package for GPT shell interactions."""

__version__ = "0.0.1"

from gpt_shell.config import Config
from gpt_shell.llm_manager import LLMManager
from gpt_shell.llm_client import LLMClient

__all__ = ["Config", "LLMManager", "LLMClient", "__version__"]
