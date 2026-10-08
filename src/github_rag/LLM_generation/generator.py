"""
LLM generation module.

This module provides a unified interface for generating text using either
a local LLM served by Ollama or an LLM accessed through the Groq API.
"""

import os

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama


# Load environment variables from the .env file.
load_dotenv()


class LLMGenerator:
    """Generate text using a local or API-based LLM."""

    # Default configuration for the local LLM.
    LOCAL_MODEL = "qwen3:1.7b"

    # Default configuration for the API-based LLM.
    API_MODEL = "openai/gpt-oss-20b"

    # Use deterministic generation for RAG responses.
    TEMPERATURE = 0.0

    # Environment variable containing the Groq API key.
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    def __init__(self, mode: str):
        """
        Initialize the LLM generator.

        Args:
            mode: LLM execution mode. It must be either "local" or "API".

        Raises:
            ValueError: If the selected mode is not supported or if the
                Groq API key is missing when using API mode.
        """
        if mode not in {"local", "API"}:
            raise ValueError(
                "Invalid LLM mode. Expected 'local' or 'API'."
            )

        self.mode = mode
        self.llm = self._load_llm()

    def _load_llm(self) -> BaseChatModel:
        """
        Load the LLM according to the selected execution mode.

        Returns:
            Configured LangChain chat model.

        Raises:
            ValueError: If the Groq API key is missing when using API mode.
        """
        if self.mode == "local":
            return ChatOllama(
                model=self.LOCAL_MODEL,
                temperature=self.TEMPERATURE,
            )

        if not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY environment variable is required "
                "when using API mode."
            )

        return ChatGroq(
            model=self.API_MODEL,
            api_key=self.GROQ_API_KEY,
            temperature=self.TEMPERATURE,
        )

    def generate(self, prompt: str) -> str:
        """
        Generate a response for the given prompt.

        Args:
            prompt: Prompt to send to the LLM.

        Returns:
            Generated response as a string.
        """
        response = self.llm.invoke(prompt)

        return response.content