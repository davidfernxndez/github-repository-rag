"""Chroma vector database creation and persistence.

Provides a class to create Chroma vector stores from LangChain Documents.
Supports two modes:
    - local: stores the database persistently in a local directory.
    - memory: creates a non-persistent database suitable for temporary use.

In local mode, an existing collection with the same name is replaced.
In memory mode, a unique collection is created for each instance.
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
    """Create and manage a Chroma vector store."""

    def __init__(
        self,
        mode: str = "local",
        persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        """Initialize the vector store configuration.

        Args:
            mode: Storage mode, either 'local' or 'memory'.
            persist_directory: Directory used for persistent local storage.
                Ignored when mode is 'memory'.
            collection_name: Name of the Chroma collection.

        Raises:
            ValueError: If the storage mode is unsupported.
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

    def create(
        self,
        documents: list[Document],
        embedding_model: Embeddings,
    ) -> Chroma:
        """Create a Chroma vector store from LangChain Documents.

        Args:
            documents: Documents containing page_content and metadata.
            embedding_model: Embedding model used to vectorize documents.

        Returns:
            A Chroma vector store containing the documents and embeddings.
        """
        if not documents:
            raise ValueError("The document list cannot be empty.")

        if self.mode == "local":
            return self._create_local(documents, embedding_model)

        return self._create_memory(documents, embedding_model)

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