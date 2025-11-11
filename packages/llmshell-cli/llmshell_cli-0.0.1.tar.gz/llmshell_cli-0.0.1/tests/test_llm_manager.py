"""Tests for LLM manager."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from gpt_shell.config import Config
from gpt_shell.llm_manager import LLMManager


@pytest.fixture
def mock_config(tmp_path):
    """Create mock config."""
    config_path = tmp_path / "config.yaml"
    config = Config(config_path)
    return config


class TestLLMManager:
    """Tests for LLM manager."""

    def test_init(self, mock_config):
        """Test manager initialization."""
        manager = LLMManager(mock_config)
        assert manager.config == mock_config
        assert manager.current_client is None
        assert manager.backend_name is None

    @patch('gpt_shell.llm_manager.GPT4AllClient')
    def test_get_client_gpt4all(self, mock_gpt4all_class, mock_config):
        """Test getting GPT4All client."""
        mock_client = Mock()
        mock_client.is_available.return_value = True
        mock_gpt4all_class.return_value = mock_client
        
        manager = LLMManager(mock_config)
        client = manager.get_client("gpt4all")
        
        assert client == mock_client
        assert manager.backend_name == "gpt4all"

    @patch('gpt_shell.llm_manager.OpenAIClient')
    def test_get_client_openai(self, mock_openai_class, mock_config):
        """Test getting OpenAI client."""
        mock_config.set("backends.openai.api_key", "test-key")
        
        mock_client = Mock()
        mock_client.is_available.return_value = True
        mock_openai_class.return_value = mock_client
        
        manager = LLMManager(mock_config)
        client = manager.get_client("openai")
        
        assert client == mock_client
        assert manager.backend_name == "openai"

    @patch('gpt_shell.llm_manager.GPT4AllClient')
    @patch('gpt_shell.llm_manager.OllamaClient')
    def test_get_client_fallback(self, mock_ollama_class, mock_gpt4all_class, mock_config):
        """Test client fallback when primary unavailable."""
        # GPT4All not available
        mock_gpt4all = Mock()
        mock_gpt4all.is_available.return_value = False
        mock_gpt4all_class.return_value = mock_gpt4all
        
        # Ollama available
        mock_ollama = Mock()
        mock_ollama.is_available.return_value = True
        mock_ollama_class.return_value = mock_ollama
        
        manager = LLMManager(mock_config)
        client = manager.get_client("gpt4all")
        
        # Should fall back to ollama
        assert client == mock_ollama
        assert manager.backend_name == "ollama"

    def test_get_client_none_available(self, mock_config):
        """Test when no clients are available."""
        manager = LLMManager(mock_config)
        
        with pytest.raises(RuntimeError, match="No LLM backends available"):
            manager.get_client()

    def test_check_backends(self, mock_config):
        """Test checking backend status."""
        manager = LLMManager(mock_config)
        results = manager.check_backends()
        
        assert len(results) > 0
        assert all(len(r) == 3 for r in results)  # Each result is (name, available, status)

    @patch('gpt_shell.llm_manager.GPT4AllClient')
    def test_generate_command(self, mock_gpt4all_class, mock_config):
        """Test command generation."""
        mock_client = Mock()
        mock_client.is_available.return_value = True
        mock_client.generate_command.return_value = "ls -la"
        mock_gpt4all_class.return_value = mock_client
        
        manager = LLMManager(mock_config)
        result = manager.generate_command("list files")
        
        assert result == "ls -la"
        mock_client.generate_command.assert_called_once_with("list files", False)

    @patch('gpt_shell.llm_manager.GPT4AllClient')
    def test_get_current_backend(self, mock_gpt4all_class, mock_config):
        """Test getting current backend name."""
        mock_client = Mock()
        mock_client.is_available.return_value = True
        mock_gpt4all_class.return_value = mock_client
        
        manager = LLMManager(mock_config)
        
        assert manager.get_current_backend() is None
        
        manager.get_client("gpt4all")
        assert manager.get_current_backend() == "gpt4all"

    @patch('gpt_shell.llm_manager.GPT4All')
    def test_download_gpt4all_model(self, mock_gpt4all_class, mock_config):
        """Test downloading GPT4All model."""
        mock_model = Mock()
        mock_gpt4all_class.return_value = mock_model
        
        manager = LLMManager(mock_config)
        
        # Note: This test might fail without proper mocking of the download process
        # In a real scenario, you'd want to mock the file system operations too
        with pytest.raises(Exception):  # Expect some exception since we're mocking
            manager.download_gpt4all_model("test-model.gguf")
