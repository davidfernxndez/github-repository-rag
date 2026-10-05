"""
Retrieval logic for the GitHub repository RAG system.

The retrieval strategy is selected according to the number of repository
files referenced in the user query:

- One file reference:
    Semantic search restricted to the referenced file. When the user
    specifies a single file, the retrieval context is well defined, so
    selecting the most semantically relevant chunks is sufficient.

- Multiple file references:
    Maximal Marginal Relevance (MMR) restricted to the referenced files.
    Queries that reference multiple files often require comparing or
    combining information across them (e.g., comparing how a feature is
    implemented in file A and file B). MMR promotes diversity among the
    retrieved chunks and a larger number of results is used to provide
    broader coverage of the specified files.

- No file reference:
    Maximal Marginal Relevance (MMR) over the whole repository. In this
    case, the user typically asks a more general question without knowing
    where the relevant information is located. MMR helps retrieve diverse
    information from different parts of the repository, while limiting the
    number of results keeps the context provided to the LLM manageable.
"""

from langchain_core.documents import Document
from github_rag.retrieval.file_reference import find_referenced_files
from github_rag.vectordatabase.chroma_store import ChromaStore
from pathlib import PurePosixPath


class Retriever:
    """Select and execute the retrieval strategy for a user query."""

    SEMANTIC_K = 5
    MMR_K = 5
    RESTRICTED_FILE_MMR_K = 10

    def __init__(self, chroma_store: ChromaStore):
        """
        Initialize the retriever.

        Args:
            chroma_store: ChromaStore instance used to perform retrieval.
        """
        self.chroma_store = chroma_store

    def retrieve(
        self,
        query: str,
        available_files: list[str],
    ) -> list[Document]:
        """
        Retrieve documents relevant to the user query.

        The retrieval strategy depends on the number of repository files
        referenced in the query:

        - One file:
            Semantic search restricted to that file, with k=5.

        - Multiple files:
            MMR search restricted to those files, with k=10.

        - No files:
            MMR search over the whole repository, with k=5.

        Args:
            query: User query.
            available_files: Files available in the repository.

        Returns:
            List of retrieved LangChain Documents.
        """
        # Detect mentioned files in the user query
        referenced_files = find_referenced_files(
            query=query,
            available_files=available_files,
        )

        # Remove @ prefix from referenced files
        query_for_retrieval = self._clean_query(
            query=query,
            referenced_files=referenced_files,
        )

        # One referenced file: semantic search with file filter
        if len(referenced_files) == 1:
            return self._semantic_search(
                query=query_for_retrieval,
                referenced_files=referenced_files,
                k=self.SEMANTIC_K,
            )

        # Multiple referenced files: filtered MMR search
        if len(referenced_files) > 1:
            return self._mmr_search(
                query=query_for_retrieval,
                k=self.RESTRICTED_FILE_MMR_K,
                referenced_files=referenced_files,
            )

        # No referenced files: MMR search over the whole repository
        return self._mmr_search(
            query=query_for_retrieval,
            k=self.MMR_K,
        )
    
    def _clean_query(
        self,
        query: str,
        referenced_files: list[str],
    ) -> str:
        """
        Remove '@' markers from referenced files in the query.

        The file reference itself is preserved because it may provide
        useful semantic information for retrieval.
        """
        if not referenced_files:
            return query
        
        clean_query = query

        for file_path in referenced_files:
            filename = PurePosixPath(file_path).name

            # Detect the complete file_path
            clean_query = clean_query.replace(
                f"@{file_path}",
                file_path,
            )

            # Detect only the filename
            clean_query = clean_query.replace(
                f"@{filename}",
                filename,
            )

        return clean_query

    def _semantic_search(
        self,
        query: str,
        referenced_files: list[str],
        k: int,
    ) -> list[Document]:
        """Perform semantic search restricted to the referenced file."""

        # Build the ChromaDB metadata filter
        file_filter = self._build_file_filter(referenced_files)

        # Apply semantic search
        results = self.chroma_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=file_filter,
        )

        # Extract only the LangChain documents
        return [document for document, _ in results]

    def _mmr_search(
        self,
        query: str,
        k: int,
        referenced_files: list[str] | None = None,
    ) -> list[Document]:
        """
        Perform MMR search, optionally restricted to referenced files.
        """

        # Build the ChromaDB metadata filter when files are provided
        file_filter = None

        if referenced_files:
            file_filter = self._build_file_filter(referenced_files)

        return self.chroma_store.max_marginal_relevance_search(
            query=query,
            k=k,
            filter=file_filter,
        )

    @staticmethod
    def _build_file_filter(
        referenced_files: list[str],
    ) -> dict:
        """Build a ChromaDB metadata filter for the referenced files."""

        if len(referenced_files) == 1:
            return {"file_path": referenced_files[0]}

        return {"file_path": {"$in": referenced_files}}