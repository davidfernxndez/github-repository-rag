"""
Chroma vector store management for the RAG pipeline.

Provides the `ChromaStore` class to create and manage Chroma vector
stores from LangChain Documents.

Two storage modes are supported:
    - local: stores the vector database persistently on disk.
    - memory: creates a non-persistent vector database for temporary use,
      such as during application deployment.

The class also provides the main operations required during the retrieval
stage of the RAG pipeline, including:
    - retrieving stored documents and metadata,
    - retrieving unique repository file paths,
    - similarity search with scores,
    - Maximal Marginal Relevance (MMR) search,
    - optional metadata filtering.
"""

from pathlib import Path
from uuid import uuid4

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


# Repository root directory.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Default directory for local Chroma databases.
DEFAULT_PERSIST_DIRECTORY = PROJECT_ROOT / "data" / "chroma"

# Default name of the Chroma collection.
DEFAULT_COLLECTION_NAME = "github_repository"


class ChromaStore:
    """Create and manage a Chroma vector store for the RAG pipeline."""

    def __init__(
        self,
        mode: str = "local",
        persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        """Initialize the vector store configuration.

        Args:
            mode: Storage mode, either ``"local"`` or ``"memory"``.
                Local mode persists the database on disk, while memory mode
                uses a temporary in-memory database.
            persist_directory: Directory used for persistent storage in
                local mode. Ignored in memory mode.
            collection_name: Name of the Chroma collection.
        """
        if mode not in {"local", "memory"}:
            raise ValueError(
                "Invalid mode. Choose 'local' or 'memory'."
            )

        self.mode = mode
        self.collection_name = collection_name
        if mode == "local":
            self.persist_directory = Path(persist_directory)
        else:
            self.persist_directory = None

        self.vector_store: Chroma | None = None

    def create(
        self,
        documents: list[Document],
        embedding_model: Embeddings,
    ) -> Chroma:
        """Create a vector store from LangChain Documents.

        In local mode, an existing collection with the same name is replaced
        before creating the new vector store. In memory mode, a unique
        collection is created for each instance.

        Args:
            documents: Documents to store, including their content and
                metadata.
            embedding_model: Embedding model used to generate document
                embeddings.
        
        Returns:
            The created Chroma vector store.
        """
        if not documents:
            raise ValueError("The document list cannot be empty.")

        if self.mode == "local":
            self.vector_store = self._create_local(
                documents,
                embedding_model,
            )
        else:
            self.vector_store = self._create_memory(
                documents,
                embedding_model,
            )

        return self.vector_store

    def _create_local(
        self,
        documents: list[Document],
        embedding_model: Embeddings,
    ) -> Chroma:
        """Create or replace a persistent local vector store."""

        # Create the directory if it does not exist.
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Open the persistent Chroma database.
        client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        # Replace the previous collection to avoid mixing old and
        # new repository documents when running the pipeline again.
        existing_collections = [
            collection.name for collection in client.list_collections()
        ]

        if self.collection_name in existing_collections:
            client.delete_collection(name=self.collection_name)

        return Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            collection_name=self.collection_name,
            client=client,
        )

    def _create_memory(
        self,
        documents: list[Document],
        embedding_model: Embeddings,
    ) -> Chroma:
        """Create a temporary, non-persistent vector store."""

        # A unique collection name prevents collisions between instances.
        collection_name = f"github_repository_{uuid4().hex}"

        # An ephemeral client does not persist the database to disk.
        client = chromadb.EphemeralClient()

        return Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            collection_name=collection_name,
            client=client,
        )
    
    def count(self) -> int:
        """Return the number of documents stored in the vector database.

        Returns:
            Number of documents (chunks) currently stored.
        """

        if self.vector_store is None:
            raise RuntimeError("The vector store has not been created yet.")

        return self.vector_store._collection.count()


    def get(self, limit: int | None = None) -> dict:
        """
        Retrieve documents and metadata from the vector database.

        Args:
            limit: Maximum number of stored documents to retrieve.
                If ``None``, all documents are retrieved.

        Returns:
            Dictionary containing the retrieved collection data.
        """
        if self.vector_store is None:
            raise RuntimeError("The vector store has not been created yet.")

        return self.vector_store._collection.get(limit=limit)


    def get_unique_file_paths(self) -> list[str]:
        """Return the unique repository file names stored in the database.

        The filenames are obtained from the ``file_path`` document metadata.
        Since multiple chunks can belong to the same file, duplicate paths
        are removed.

        Returns:
            Sorted list of unique repository file paths.
        """

        if self.vector_store is None:
            raise RuntimeError("The vector store has not been created yet.")

        results = self.vector_store._collection.get(
            include=["metadatas"]
        )

        # Use set to discard duplicated file names
        file_paths = {
            metadata["file_path"]
            for metadata in results["metadatas"]
            if metadata and "file_path" in metadata
        }

        return sorted(file_paths)


    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: dict | None = None,
    ) -> list[tuple[Document, float]]:
        """
        Retrieve the most similar documents to a query. Documents are ranked 
        according to the similarity between the query embedding and the stored
        document embeddings.

        Args:
            query: Text query used for semantic retrieval.
            k: Number of documents to return.
            filter: Optional metadata filter used to restrict the search
                to specific documents.

        Returns:
            List of ``(Document, score)`` tuples. The score is the distance
            returned by the underlying vector store; lower values generally
            indicate greater similarity.
        """
        if self.vector_store is None:
            raise RuntimeError("The vector store has not been created yet.")

        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
        )


    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: dict | None = None,
    ) -> list[Document]:
        """
        Retrieve relevant and diverse documents using MMR.

        MMR first retrieves ``fetch_k`` candidate documents and then selects
        ``k`` documents by balancing their relevance to the query with their
        similarity to the other selected documents.

        Args:
            query: Text query used for semantic retrieval.
            k: Number of documents to return.
            fetch_k: Number of candidate documents considered before applying
                MMR. It should generally be greater than or equal to ``k``.
            lambda_mult: Controls the relevance-diversity trade-off.
                ``1.0`` favors relevance, while ``0.0`` favors diversity.
            filter: Optional metadata filter used to restrict the search
                candidates.

        Returns:
            List of documents selected by the MMR algorithm.
        """
        if self.vector_store is None:
            raise RuntimeError("The vector store has not been created yet.")

        return self.vector_store.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            filter=filter,
        )