"""
Text document chunker.

This module provides the TextChunker class, which splits text-based
documents using a recursive character-based strategy.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .chunkConfig import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

class TextChunker:
    """
    Split text-based documents using recursive character splitting.

    This chunker is used for plain text and structured text formats
    such as JSON, YAML, and TOML.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk(self, document: Document) -> list[Document]:
        """
        Split a document into smaller chunks.

        Args:
            document: Text-based document to split.

        Returns:
            A list of chunked Documents.
        """
        return self._splitter.split_documents([document])