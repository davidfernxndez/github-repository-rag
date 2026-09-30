"""
Code document chunker.

This module provides the CodeChunker class, which splits source code
documents using language-specific separators provided by LangChain.
"""

# Document Langchain structure
from langchain_core.documents import Document

# LangChain chunking tools 
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

# Chunk global configuration
from .chunkconfig import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

# Map file extensions to the corresponding LangChain programming language.
LANGUAGE_MAP = {
    ".py": Language.PYTHON,
    ".js": Language.JS,
    ".ts": Language.TS,
    ".java": Language.JAVA,
    ".cpp": Language.CPP,
    ".c": Language.C,
    ".go": Language.GO,
    ".rs": Language.RUST,
    ".sql": Language.SQL,
}


class CodeChunker:
    """
    Split source code documents using language-specific separators.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        # Store the chunking configuration so it can be used
        # when creating the text splitter.
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: Document) -> list[Document]:
        """
        Split a code document into smaller chunks.

        The language is determined from the file extension stored
        in the document metadata. LangChain then applies
        language-specific separators when splitting the code.

        Args:
            document: Code document to split.

        Returns:
            A list of Documents containing the resulting code chunks.
        """
        # Get the file extension from the document metadata.
        file_type = document.metadata.get("file_type")

        # Map the file extension to a LangChain Language.
        language = self._get_language(file_type)

        # Create a language-aware recursive text splitter.
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        # split_documents() preserves the original document metadata.
        return splitter.split_documents([document])

    @staticmethod
    def _get_language(file_type: str | None) -> Language:
        """
        Get the LangChain language associated with a file extension.

        Args:
            file_type: File extension stored in document metadata.

        Returns:
            The corresponding LangChain Language.

        Raises:
            ValueError: If the file type is not supported.
        """

        try:
            return LANGUAGE_MAP[file_type]
        except KeyError as exc:
            # Fail explicitly if an unsupported code extension
            # reaches this chunker.
            raise ValueError(
                f"Unsupported code file type: {file_type}"
            ) from exc