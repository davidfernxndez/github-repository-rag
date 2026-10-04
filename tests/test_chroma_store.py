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
            page_content="Python supports object-oriented programming.",
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

    store.create(documents, embedding_model)

    # Verify that the persistent database directory was created.
    assert (tmp_path / "chroma").exists()

    # Verify that all documents were indexed.
    assert store.count() == 3

    # Verify that semantic search returns the expected document.
    results = store.similarity_search_with_score(
        "What is Chroma?",
        k=1,
    )

 
    assert len(results) == 1
    assert results[0][0].metadata["file_path"] == "chroma.md"


def test_create_memory_vector_store(documents, embedding_model):
    """Test creation of a non-persistent vector store."""

    store = ChromaStore(mode="memory")
    store.create(documents, embedding_model)

    # Verify that all documents were indexed in the in-memory database.
    assert store.count() == 3

    # Verify that semantic search works on the in-memory database.
    results = store.similarity_search_with_score(
        "What is Python?",
        k=1,
    )

    assert len(results) == 1
    assert results[0][0].metadata["file_path"] == "python.md"


def test_create_vector_store_with_empty_documents(embedding_model):
    """Test that an empty document list raises ValueError."""

    store = ChromaStore(mode="memory")

    # Creating a vector store without documents should not be allowed.
    with pytest.raises(ValueError, match="cannot be empty"):
        store.create([], embedding_model)


def test_invalid_storage_mode():
    """Test that unsupported storage modes raise ValueError."""

    # Only 'local' and 'memory' modes should be accepted.
    with pytest.raises(ValueError, match="Invalid mode"):
        ChromaStore(mode="invalid")

def test_count(documents, embedding_model):
    """Test that count returns the number of stored documents."""

    store = ChromaStore(mode="memory")
    store.create(documents, embedding_model)

    # Verify that count matches the number of indexed documents.
    assert store.count() == 3


def test_get(documents, embedding_model):
    """Test that get returns the requested number of documents."""

    store = ChromaStore(mode="memory")
    store.create(documents, embedding_model)

    # Retrieve only a subset of the stored documents.
    results = store.get(limit=2)

    # Verify that the requested number of IDs, documents, and metadata
    # entries is returned.
    assert len(results["ids"]) == 2
    assert len(results["documents"]) == 2
    assert len(results["metadatas"]) == 2


def test_get_unique_file_paths(documents, embedding_model):
    """Test that get_unique_file_paths returns unique file paths."""

    store = ChromaStore(mode="memory")
    store.create(documents, embedding_model)

    file_paths = store.get_unique_file_paths()

    # Two chunks belong to python.md, so only two unique file paths
    # should be returned.
    assert file_paths == [
        "chroma.md",
        "python.md",
    ]


def test_similarity_search_with_score(documents, embedding_model):
    """Test similarity search returns documents and scores."""

    store = ChromaStore(mode="memory")
    store.create(documents, embedding_model)

    results = store.similarity_search_with_score(
        query="What is Chroma?",
        k=2,
    )

    # Verify that the requested number of results is returned.
    assert len(results) == 2

    # Each result should contain a LangChain Document and a distance score.
    for document, score in results:
        assert isinstance(document, Document)
        assert isinstance(score, float)


def test_similarity_search_with_file_filter(
    documents,
    embedding_model,
):
    """Test similarity search with a metadata filter."""

    store = ChromaStore(mode="memory")
    store.create(documents, embedding_model)

    results = store.similarity_search_with_score(
        query="programming language",
        k=5,
        filter={"file_path": "python.md"},
    )

    # Only the two chunks belonging to python.md should be returned.
    assert len(results) == 2

    # Verify that every result satisfies the metadata filter.
    for document, _ in results:
        assert document.metadata["file_path"] == "python.md"


def test_max_marginal_relevance_search(
    documents,
    embedding_model,
):
    """Test MMR returns the requested number of documents."""

    store = ChromaStore(mode="memory")
    store.create(documents, embedding_model)

    results = store.max_marginal_relevance_search(
        query="What is Python?",
        k=2,
        fetch_k=3,
        lambda_mult=0.5,
    )

    # Verify that MMR returns the requested number of documents.
    assert len(results) == 2

    # Verify that all results are LangChain Documents.
    for document in results:
        assert isinstance(document, Document)


def test_max_marginal_relevance_search_with_file_filter(
    documents,
    embedding_model,
):
    """Test MMR with a metadata filter."""

    store = ChromaStore(mode="memory")
    store.create(documents, embedding_model)

    results = store.max_marginal_relevance_search(
        query="programming language",
        k=2,
        fetch_k=3,
        lambda_mult=0.5,
        filter={"file_path": "python.md"},
    )

    # Only documents from python.md should be returned.
    assert len(results) == 2

    # Verify that every result satisfies the metadata filter.
    for document in results:
        assert document.metadata["file_path"] == "python.md"