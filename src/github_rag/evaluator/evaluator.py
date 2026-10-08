"""
Evaluation utilities for the GitHub Repository RAG system.

This module provides LLM-as-a-Judge evaluation using Ragas to measure
the faithfulness and answer relevancy of generated responses.
"""

import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from ragas.embeddings import HuggingFaceEmbeddings
from ragas.llms import llm_factory
from ragas.metrics.collections import AnswerRelevancy, Faithfulness


DEFAULT_JUDGE_MODEL = "openai/gpt-oss-20b"
DEFAULT_EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class RAGEvaluator:
    """Evaluate RAG responses using Ragas metrics."""

    def __init__(
        self,
        judge_model: str = DEFAULT_JUDGE_MODEL,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:
        """Initialize the RAG evaluator.

        Args:
            judge_model: Model used as the LLM judge through Groq.
            embedding_model: Hugging Face model used by Answer Relevancy.
        """
        load_dotenv()

        groq_api_key = os.getenv("GROQ_API_KEY")

        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY was not found in the .env file."
            )

        # Create the OpenAI asyn client
        judge_client = AsyncOpenAI(
            api_key=groq_api_key,
            base_url=GROQ_BASE_URL,
        )

        # Get the LLM model
        self.judge_llm = llm_factory(
            model=judge_model,
            provider="openai",
            client=judge_client,
        )

        # Get the embeddings model
        self.judge_embeddings = HuggingFaceEmbeddings(
            model=embedding_model
        )

        # Create Faithfulness metric with the
        # LLM judge model
        self.faithfulness = Faithfulness(
            llm=self.judge_llm
        )

        # Create the answer relevancy metric with the
        # LLM judge model and the embeddings
        self.answer_relevancy = AnswerRelevancy(
            llm=self.judge_llm,
            embeddings=self.judge_embeddings,
        )

    async def evaluate_faithfulness(
        self,
        user_input: str,
        response: str,
        retrieved_contexts: list[str],
    ) -> float:
        """Evaluate whether the response is supported by the contexts.

        Args:
            user_input: User's original question.
            response: Generated answer.
            retrieved_contexts: Contexts retrieved and used to generate
                the answer.

        Returns:
            Faithfulness score between 0 and 1.
        """
        result = await self.faithfulness.ascore(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts,
        )

        return result.value

    async def evaluate_answer_relevancy(
        self,
        user_input: str,
        response: str,
    ) -> float:
        """Evaluate whether the response answers the user's question.

        Args:
            user_input: User's original question.
            response: Generated answer.

        Returns:
            Answer relevancy score between 0 and 1.
        """
        result = await self.answer_relevancy.ascore(
            user_input=user_input,
            response=response,
        )

        return result.value

    async def evaluate(
        self,
        user_input: str,
        response: str,
        retrieved_contexts: list[str],
    ) -> dict[str, float]:
        """Evaluate a RAG response using both evaluation metrics.

        Args:
            user_input: User's original question.
            response: Generated answer.
            retrieved_contexts: Contexts retrieved and used to generate
                the answer.

        Returns:
            Dictionary containing faithfulness and answer relevancy
            scores.
        """
        faithfulness_result = await self.evaluate_faithfulness(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts,
        )

        answer_relevancy_result = await self.evaluate_answer_relevancy(
            user_input=user_input,
            response=response,
        )

        return {
            "faithfulness": faithfulness_result,
            "answer_relevancy": answer_relevancy_result,
        }