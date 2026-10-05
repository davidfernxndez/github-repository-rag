"""
Tests for the Retriever class.

The tests use a mocked ChromaStore so that retrieval logic can be tested
independently of the actual vector database.
"""

from unittest.mock import Mock
from langchain_core.documents import Document
from github_rag.retrieval.retriever import Retriever


# Example repository file paths
AVAILABLE_FILES = [
    "README.md",
    "data/data_info.md",
    "main.ipynb",
    "scripts/AL_methods.py",
    "scripts/AL_performance.py",
    "scripts/AL_scalability.py",
]


def test_retrieve_without_file_reference_uses_mmr():
    """Use MMR with k=5 when no file is referenced."""

    documents = [
        Document(
            page_content="Active learning implementation.",
            metadata={"file_path": "scripts/AL_methods.py"},
        ),
        Document(
            page_content="Performance experiment.",
            metadata={"file_path": "scripts/AL_performance.py"},
        ),
    ]

    # Create a mock object that will replace the real ChromaStore
    chroma_store = Mock()

    # Configure the mock so that calling
    # max_marginal_relevance_search() returns our test documents
    chroma_store.max_marginal_relevance_search.return_value = documents

    # Inject the mock instead of a real ChromaStore
    retriever = Retriever(chroma_store)

    result = retriever.retrieve(
        query="How does the active learning algorithm work?",
        available_files=AVAILABLE_FILES,
    )

    # Check that Retriever returned the documents provided by the mock
    assert result == documents

    # Verify that Retriever called the MMR method with the expected arguments
    chroma_store.max_marginal_relevance_search.assert_called_once_with(
        query="How does the active learning algorithm work?",
        k=5,
        filter=None,
    )

    # Verify that semantic search was not used
    chroma_store.similarity_search_with_score.assert_not_called()


def test_retrieve_with_one_file_uses_semantic_search():
    """Use semantic search with k=5 when one file is referenced."""

    document = Document(
        page_content="Implementation of the active learning methods.",
        metadata={"file_path": "scripts/AL_methods.py"},
    )

    # Create a mock object that will replace the real ChromaStore
    chroma_store = Mock()

    # Configure the Mock output for similarity search
    chroma_store.similarity_search_with_score.return_value = [
        (document, 0.15),
    ]

    # Inject the mock instead of a real ChromaStore
    retriever = Retriever(chroma_store)

    result = retriever.retrieve(
        query="Explain AL_methods.py",
        available_files=AVAILABLE_FILES,
    )

    assert result == [document]

    chroma_store.similarity_search_with_score.assert_called_once_with(
        query="Explain AL_methods.py",
        k=5,
        filter={
            "file_path": "scripts/AL_methods.py",
        },
    )

    chroma_store.max_marginal_relevance_search.assert_not_called()


def test_retrieve_with_multiple_files_uses_filtered_mmr():
    """Use filtered MMR with k=10 when multiple files are referenced."""

    documents = [
        Document(
            page_content="Active learning methods.",
            metadata={"file_path": "scripts/AL_methods.py"},
        ),
        Document(
            page_content="Performance evaluation.",
            metadata={"file_path": "scripts/AL_performance.py"},
        ),
    ]

    # Create a mock object that will replace the real ChromaStore
    chroma_store = Mock()
    chroma_store.max_marginal_relevance_search.return_value = documents

    # Inject the Mock
    retriever = Retriever(chroma_store)

    result = retriever.retrieve(
        query="Compare AL_methods.py and AL_performance.py",
        available_files=AVAILABLE_FILES,
    )

    assert result == documents

    chroma_store.max_marginal_relevance_search.assert_called_once_with(
        query="Compare AL_methods.py and AL_performance.py",
        k=10,
        filter={
            "file_path": {
                "$in": [
                    "scripts/AL_methods.py",
                    "scripts/AL_performance.py",
                ]
            }
        },
    )

    chroma_store.similarity_search_with_score.assert_not_called()


def test_retrieve_with_at_file_reference():
    """Remove @ preffix from referenced file."""

    document = Document(
        page_content="Active learning methods.",
        metadata={"file_path": "scripts/AL_methods.py"},
    )

    # Create a mock object that will replace the real ChromaStore
    chroma_store = Mock()
    chroma_store.similarity_search_with_score.return_value = [
        (document, 0.20),
    ]

    retriever = Retriever(chroma_store)

    result = retriever.retrieve(
        query="Explain @scripts/AL_methods.py",
        available_files=AVAILABLE_FILES,
    )

    assert result == [document]

    chroma_store.similarity_search_with_score.assert_called_once_with(
        query="Explain scripts/AL_methods.py",
        k=5,
        filter={
            "file_path": "scripts/AL_methods.py",
        },
    )


def test_semantic_search_discards_scores():
    """Return only Documents from semantic search results."""

    document_1 = Document(
        page_content="First document.",
        metadata={"file_path": "scripts/AL_methods.py"},
    )

    document_2 = Document(
        page_content="Second document.",
        metadata={"file_path": "scripts/AL_methods.py"},
    )

    # Create a mock object that will replace the real ChromaStore
    chroma_store = Mock()
    chroma_store.similarity_search_with_score.return_value = [
        (document_1, 0.10),
        (document_2, 0.25),
    ]

    retriever = Retriever(chroma_store)

    result = retriever.retrieve(
        query="Explain AL_methods.py",
        available_files=AVAILABLE_FILES,
    )

    assert result == [document_1, document_2]
    assert all(isinstance(document, Document) for document in result)
    assert not any(isinstance(item, tuple) for item in result)