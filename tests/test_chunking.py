"""
Tests for document chunking.

These tests verify that documents are routed to the appropriate
chunking strategy and that the resulting chunks preserve the
expected content and metadata.
"""

from langchain_core.documents import Document

from github_rag.chunking.chunker import Chunker
from github_rag.chunking.code import CodeChunker
from github_rag.chunking.markdown import MarkdownChunker
from github_rag.chunking.text import TextChunker


def create_document(content: str, file_type: str) -> Document:
    """Create a test document with representative metadata."""
    return Document(
        page_content=content,
        metadata={
            "repository": "test-repository",
            "file_path": f"src/example{file_type}",
            "file_type": file_type,
            "source": (
                f"https://github.com/example/test-repository/"
                f"blob/main/src/example{file_type}"
            ),
            "branch": "main",
        },
    )


# ---------------------------------------------------------------------------
# CodeChunker
# ---------------------------------------------------------------------------


def test_code_chunker_splits_python_code():
    """CodeChunker should split a Python document into multiple chunks."""
    document = create_document(
        "def process(data):\n    return data\n" * 100,
        ".py",
    )

    chunker = CodeChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk(document)

    assert len(chunks) > 1
    assert all(chunk.metadata["file_type"] == ".py" for chunk in chunks)


def test_code_chunker_preserves_metadata():
    """CodeChunker should preserve the original document metadata."""
    document = create_document(
        "def process(data):\n    return data\n" * 20,
        ".py",
    )

    chunks = CodeChunker(
        chunk_size=100,
        chunk_overlap=20,
    ).chunk(document)

    for chunk in chunks:
        assert chunk.metadata["repository"] == "test-repository"
        assert chunk.metadata["file_path"] == "src/example.py"
        assert chunk.metadata["source"].startswith("https://github.com/")
        assert chunk.metadata["branch"] == "main"


def test_code_chunker_rejects_unsupported_file_type():
    """CodeChunker should reject unsupported code file types."""
    document = create_document(
        "some content",
        ".txt",
    )

    chunker = CodeChunker()

    try:
        chunker.chunk(document)
        assert False
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# MarkdownChunker
# ---------------------------------------------------------------------------


def test_markdown_chunker_preserves_headers():
    """MarkdownChunker should preserve headers in content and metadata."""
    document = create_document(
        "# Introduction\n\n"
        "This is an introduction.\n\n"
        "## Installation\n\n"
        "This explains how to install the project.",
        ".md",
    )

    chunks = MarkdownChunker().chunk(document)

    assert len(chunks) == 2

    assert "# Introduction" in chunks[0].page_content
    assert chunks[0].metadata["header_1"] == "Introduction"

    assert "## Installation" in chunks[1].page_content
    assert chunks[1].metadata["header_2"] == "Installation"


def test_markdown_chunker_preserves_original_metadata():
    """MarkdownChunker should preserve the original document metadata."""
    document = create_document(
        "# Introduction\n\nSome content.",
        ".md",
    )

    chunks = MarkdownChunker().chunk(document)

    assert chunks[0].metadata["repository"] == "test-repository"
    assert chunks[0].metadata["file_path"] == "src/example.md"
    assert chunks[0].metadata["file_type"] == ".md"


def test_markdown_chunker_without_headers_uses_recursive_splitting():
    """Markdown without headers should use recursive character splitting."""
    document = create_document(
        "This is a long Markdown document without any headers.\n" * 100,
        ".md",
    )

    chunker = MarkdownChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk(document)

    assert len(chunks) > 1


# ---------------------------------------------------------------------------
# TextChunker
# ---------------------------------------------------------------------------


def test_text_chunker_splits_text():
    """TextChunker should split plain text into multiple chunks."""
    document = create_document(
        "This is a text document.\n" * 100,
        ".txt",
    )

    chunker = TextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk(document)

    assert len(chunks) > 1


def test_text_chunker_preserves_metadata():
    """TextChunker should preserve the original document metadata."""
    document = create_document(
        "Some text content.\n" * 50,
        ".json",
    )

    chunks = TextChunker(
        chunk_size=100,
        chunk_overlap=20,
    ).chunk(document)

    for chunk in chunks:
        assert chunk.metadata["repository"] == "test-repository"
        assert chunk.metadata["file_type"] == ".json"


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------


def test_chunker_routes_documents_by_file_type():
    """Chunker should route documents to the appropriate strategy."""
    documents = [
        create_document("def test():\n    pass\n" * 20, ".py"),
        create_document("# Title\n\nSome content.", ".md"),
        create_document("Some text content.\n" * 20, ".txt"),
        create_document('{"name": "test"}\n' * 20, ".json"),
    ]

    chunker = Chunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk(documents)

    assert len(chunks) > len(documents)

    file_types = {chunk.metadata["file_type"] for chunk in chunks}

    assert ".py" in file_types
    assert ".md" in file_types
    assert ".txt" in file_types
    assert ".json" in file_types