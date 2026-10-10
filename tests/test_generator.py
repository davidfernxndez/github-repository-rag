"""Tests for the LLMGenerator class."""

from unittest.mock import MagicMock, patch

import pytest

from github_rag.LLM_generation.generator import LLMGenerator


def test_invalid_mode_raises_error():
    """Test that an invalid mode raises ValueError."""
    with pytest.raises(ValueError, match="Invalid LLM mode"):
        LLMGenerator(mode="invalid")


@patch("github_rag.LLM_generation.generator.ChatOllama")
def test_local_mode_loads_ollama(mock_chat_ollama):
    """Test that local mode loads the Ollama model."""
    generator = LLMGenerator(mode="local")

    mock_chat_ollama.assert_called_once_with(
        model=LLMGenerator.LOCAL_MODEL,
        temperature=LLMGenerator.TEMPERATURE,
    )

    assert generator.mode == "local"
    assert generator.llm == mock_chat_ollama.return_value


@patch("github_rag.LLM_generation.generator.ChatGroq")
def test_api_mode_loads_groq(mock_chat_groq):
    """Test that API mode loads the Groq model."""
    generator = LLMGenerator(
        mode="API",
        api_key="test-api-key",
    )

    mock_chat_groq.assert_called_once_with(
        model=LLMGenerator.API_MODEL,
        api_key="test-api-key",
        temperature=LLMGenerator.TEMPERATURE,
    )
    assert generator.llm == mock_chat_groq.return_value


@patch.dict("os.environ", {}, clear=True)
def test_api_mode_without_api_key_raises_error():
    """Test that API mode requires a Groq API key."""
    with patch(
        "github_rag.LLM_generation.generator.load_dotenv"
    ):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                ValueError,
                match="GROQ_API_KEY environment variable is required",
            ):
                LLMGenerator(mode="API")


@patch("github_rag.LLM_generation.generator.ChatOllama")
def test_generate_returns_response_content(mock_chat_ollama):
    """Test that generate returns the LLM response content."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Generated response."

    mock_llm.invoke.return_value = mock_response
    mock_chat_ollama.return_value = mock_llm

    generator = LLMGenerator(mode="local")

    prompt = "Explain this repository."
    result = generator.generate(prompt)

    mock_llm.invoke.assert_called_once_with(prompt)

    assert result == "Generated response."