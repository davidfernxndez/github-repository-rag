"""
Tests local and in-memory Chroma vector stores using real LangChain
documents and an actual embedding model.

Temporary directories are used for local databases and are automatically
deleted by pytest after each test. The repository's development database
is never modified.
"""

import pytest
from langchain_core.documents import Document

from github_rag.embedding.embedding_model import create_embedding_model
from github_rag.vectordatabase.chroma_store import ChromaStore


@pytest.fixture(scope="module")
def embedding_model():
    """Load the embedding model once for all tests in this module."""
    return create_embedding_model()


@pytest.fixture
def documents():
    """Create sample documents with content and metadata."""
    return [
        Document(
            page_content="Python is a programming language.",
            metadata={"file_path": "python.md", "file_type": "md"},
        ),
        Document(
            page_content="Chroma is a vector database.",
            metadata={"file_path": "chroma.md", "file_type": "md"},
        ),
    ]


def test_create_local_vector_store(
    tmp_path, documents, embedding_model
):
    """Test local database creation and document retrieval."""

    store = ChromaStore(
        mode="local",
        persist_directory=tmp_path / "chroma",
    )

    vector_store = store.create(documents, embedding_model)

    # Check that the persistent database was created.
    assert (tmp_path / "chroma").exists()

    # Check that both documents were indexed.
    assert vector_store._collection.count() == 2

    # Check that similarity search returns a relevant document.
    results = vector_store.similarity_search(
        "What is Chroma?",
        k=1,
    )

    assert len(results) == 1
    assert results[0].metadata["file_path"] == "chroma.md"


def test_create_memory_vector_store(documents, embedding_model):
    """Test creation of a non-persistent vector store."""

    store = ChromaStore(mode="memory")
    vector_store = store.create(documents, embedding_model)

    # Check that documents are indexed in memory.
    assert vector_store._collection.count() == 2

    # Check that similarity search works.
    results = vector_store.similarity_search(
        "What is Python?",
        k=1,
    )

    assert len(results) == 1
    assert results[0].metadata["file_path"] == "python.md"


def test_create_vector_store_with_empty_documents(embedding_model):
    """Test that an empty document list raises ValueError."""

    store = ChromaStore(mode="memory")

    with pytest.raises(ValueError, match="cannot be empty"):
        store.create([], embedding_model)


def test_invalid_storage_mode():
    """Test that unsupported storage modes raise ValueError."""

    with pytest.raises(ValueError, match="Invalid mode"):
        ChromaStore(mode="invalid")