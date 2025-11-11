"""Tests for LLM clients."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from gpt_shell.llm_client import (
    GPT4AllClient,
    OpenAIClient,
    OllamaClient,
    CustomClient,
)


class TestGPT4AllClient:
    """Tests for GPT4All client."""

    @patch('gpt_shell.llm_client.GPT4All')
    def test_init_success(self, mock_gpt4all):
        """Test successful initialization."""
        mock_model = Mock()
        mock_gpt4all.return_value = mock_model
        
        client = GPT4AllClient("test-model")
        assert client.is_available()
        assert client.model == mock_model

    @patch('gpt_shell.llm_client.GPT4All')
    def test_init_failure(self, mock_gpt4all):
        """Test initialization failure."""
        mock_gpt4all.side_effect = Exception("Model not found")
        
        client = GPT4AllClient("test-model")
        assert not client.is_available()

    @patch('gpt_shell.llm_client.GPT4All')
    def test_generate_command(self, mock_gpt4all):
        """Test command generation."""
        mock_model = Mock()
        mock_model.generate.return_value = "ls -la"
        mock_model.chat_session.return_value.__enter__ = Mock(return_value=None)
        mock_model.chat_session.return_value.__exit__ = Mock(return_value=None)
        mock_gpt4all.return_value = mock_model
        
        client = GPT4AllClient("test-model")
        result = client.generate_command("list files")
        
        assert result == "ls -la"
        mock_model.generate.assert_called_once()


class TestOpenAIClient:
    """Tests for OpenAI client."""

    @patch('gpt_shell.llm_client.OpenAI')
    def test_init_success(self, mock_openai_class):
        """Test successful initialization."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        client = OpenAIClient(api_key="test-key", model="gpt-4")
        assert client.is_available()
        assert client.client == mock_client

    def test_init_no_api_key(self):
        """Test initialization without API key."""
        client = OpenAIClient(api_key=None)
        assert not client.is_available()

    @patch('gpt_shell.llm_client.OpenAI')
    def test_generate_command(self, mock_openai_class):
        """Test command generation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "docker ps -a"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        client = OpenAIClient(api_key="test-key")
        result = client.generate_command("list docker containers")
        
        assert result == "docker ps -a"


class TestOllamaClient:
    """Tests for Ollama client."""

    @patch('gpt_shell.llm_client.requests')
    def test_init_success(self, mock_requests):
        """Test successful initialization."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3:latest"}]
        }
        mock_requests.get.return_value = mock_response
        
        client = OllamaClient(model="llama3")
        assert client.is_available()

    @patch('gpt_shell.llm_client.requests')
    def test_init_failure(self, mock_requests):
        """Test initialization failure."""
        mock_requests.get.side_effect = Exception("Connection refused")
        
        client = OllamaClient(model="llama3")
        assert not client.is_available()

    @patch('gpt_shell.llm_client.requests')
    def test_generate_command(self, mock_requests):
        """Test command generation."""
        # Mock availability check
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "models": [{"name": "llama3:latest"}]
        }
        
        # Mock generate request
        mock_post_response = Mock()
        mock_post_response.json.return_value = {
            "response": "find . -name '*.py'"
        }
        
        mock_requests.get.return_value = mock_get_response
        mock_requests.post.return_value = mock_post_response
        
        client = OllamaClient(model="llama3")
        result = client.generate_command("find python files")
        
        assert result == "find . -name '*.py'"


class TestCustomClient:
    """Tests for Custom API client."""

    @patch('gpt_shell.llm_client.requests')
    def test_init_success(self, mock_requests):
        """Test successful initialization."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        
        client = CustomClient(api_url="http://localhost:8000/v1")
        assert client.is_available()

    @patch('gpt_shell.llm_client.requests')
    def test_init_failure(self, mock_requests):
        """Test initialization failure."""
        mock_requests.get.side_effect = Exception("Connection refused")
        
        client = CustomClient(api_url="http://localhost:8000/v1")
        assert not client.is_available()

    @patch('gpt_shell.llm_client.requests')
    def test_generate_command(self, mock_requests):
        """Test command generation."""
        # Mock availability check
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        
        # Mock generate request
        mock_post_response = Mock()
        mock_post_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "df -h"
                }
            }]
        }
        
        mock_requests.get.return_value = mock_get_response
        mock_requests.post.return_value = mock_post_response
        
        client = CustomClient(api_url="http://localhost:8000/v1")
        result = client.generate_command("show disk usage")
        
        assert result == "df -h"
