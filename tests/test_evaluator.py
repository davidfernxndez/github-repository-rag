"""
Tests for the RAG evaluator.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from github_rag.evaluator import RAGEvaluator


@patch("github_rag.evaluator.evaluator.Faithfulness")
@patch("github_rag.evaluator.evaluator.AnswerRelevancy")
@patch("github_rag.evaluator.evaluator.HuggingFaceEmbeddings")
@patch("github_rag.evaluator.evaluator.AsyncOpenAI")
@patch("github_rag.evaluator.evaluator.llm_factory")
def test_evaluator_initialization(
    mock_llm_factory,
    mock_async_openai,
    mock_embeddings,
    mock_answer_relevancy,
    mock_faithfulness,
    monkeypatch,
):
    """Test that the RAG evaluator is initialized correctly."""
    monkeypatch.setenv("GROQ_API_KEY", "test-api-key")

    evaluator = RAGEvaluator()

    mock_async_openai.assert_called_once()
    mock_llm_factory.assert_called_once()
    mock_embeddings.assert_called_once()
    mock_faithfulness.assert_called_once()
    mock_answer_relevancy.assert_called_once()

    assert evaluator.judge_llm is mock_llm_factory.return_value
    assert evaluator.judge_embeddings is mock_embeddings.return_value


def test_evaluate_faithfulness():
    """Test faithfulness evaluation."""
    evaluator = object.__new__(RAGEvaluator)

    evaluator.faithfulness = MagicMock()

    result = MagicMock()
    result.value = 0.95

    evaluator.faithfulness.ascore = AsyncMock(return_value=result)

    score = asyncio.run(
        evaluator.evaluate_faithfulness(
            user_input="What embedding model is used?",
            response="The project uses MiniLM.",
            retrieved_contexts=["The project uses MiniLM."],
        )
    )

    assert score == 0.95

    evaluator.faithfulness.ascore.assert_awaited_once_with(
        user_input="What embedding model is used?",
        response="The project uses MiniLM.",
        retrieved_contexts=["The project uses MiniLM."],
    )


def test_evaluate_answer_relevancy():
    """Test answer relevancy evaluation."""
    evaluator = object.__new__(RAGEvaluator)

    evaluator.answer_relevancy = MagicMock()

    result = MagicMock()
    result.value = 0.90

    evaluator.answer_relevancy.ascore = AsyncMock(return_value=result)

    score = asyncio.run(
        evaluator.evaluate_answer_relevancy(
            user_input="What embedding model is used?",
            response="The project uses MiniLM.",
        )
    )

    assert score == 0.90

    evaluator.answer_relevancy.ascore.assert_awaited_once_with(
        user_input="What embedding model is used?",
        response="The project uses MiniLM.",
    )


def test_evaluate():
    """Test evaluation using both metrics."""
    evaluator = object.__new__(RAGEvaluator)

    evaluator.evaluate_faithfulness = AsyncMock(return_value=0.95)
    evaluator.evaluate_answer_relevancy = AsyncMock(return_value=0.90)

    results = asyncio.run(
        evaluator.evaluate(
            user_input="What embedding model is used?",
            response="The project uses MiniLM.",
            retrieved_contexts=["The project uses MiniLM."],
        )
    )

    assert results == {
        "faithfulness": 0.95,
        "answer_relevancy": 0.90,
    }

    evaluator.evaluate_faithfulness.assert_awaited_once()
    evaluator.evaluate_answer_relevancy.assert_awaited_once()

