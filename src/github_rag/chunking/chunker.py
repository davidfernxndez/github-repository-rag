"""
Document chunking coordinator.

This module provides the Chunker class, which routes documents
to the appropriate format-specific chunker.
"""

# LangChain Document structure
from langchain_core.documents import Document

# Import file type groups used to select the chunking strategy
from github_rag.ingestion.filters import (
    CODE_EXTENSIONS,
    MARKDOWN_EXTENSIONS,
    TEXT_EXTENSIONS,
    STRUCTURED_EXTENSIONS,
)

# Import format-specific chunking strategies
from .code import CodeChunker
from .markdown import MarkdownChunker
from .text import TextChunker

# Import default chunking configuration
from .chunkConfig import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


class Chunker:
    """
    Coordinate the chunking of processed documents.

    Documents are routed to a format-specific chunker based on
    their file type.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        # Initialize the format-specific chunkers.

        # Code Chunker
        self._code_chunker = CodeChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Markdown Chunker
        self._markdown_chunker = MarkdownChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Text Chunker
        self._text_chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into smaller retrieval units.

        Each document is routed to the chunker associated with
        its file type. Documents without a specific chunking
        strategy are kept unchanged.

        Args:
            documents: Documents produced by the processing stage.

        Returns:
            A list of chunked Documents.
        """
        chunks: list[Document] = []

        for document in documents:
            # Get the file type from the document metadata.
            file_type = document.metadata.get("file_type")

            # Select the appropriate chunking strategy.
            chunker = self._get_chunker(file_type)

            # Keep documents unchanged when no chunking strategy
            # is available for their file type.
            if chunker is None:
                chunks.append(document)
                continue

            # Apply the selected chunker to the document.
            chunks.extend(chunker.chunk(document))

        return chunks

    def _get_chunker(self, file_type: str | None):
        """
        Return the chunker associated with a file type.

        Args:
            file_type: File extension stored in document metadata.

        Returns:
            The appropriate format-specific chunker, or None if
            the file type is not supported.
        """

        # Code files
        if file_type in CODE_EXTENSIONS:
            return self._code_chunker

        # Markdown files
        if file_type in MARKDOWN_EXTENSIONS:
            return self._markdown_chunker

        # Text or structured data files
        if (
            file_type in TEXT_EXTENSIONS
            or file_type in STRUCTURED_EXTENSIONS
        ):
            return self._text_chunker

        # No specific chunking strategy is available
        return None