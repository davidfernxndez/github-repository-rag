"""
Orchestrate GitHub repository ingestion and RAG retriever initialization.
"""

from github_rag.ingestion.repository import GitHubRepositoryLoader
from github_rag.processing.processor import Processor
from github_rag.chunking.chunker import Chunker
from github_rag.vectordatabase.chroma_store import ChromaStore
from github_rag.retrieval.retriever import Retriever


# Define the ingestion stages displayed by the application interface.
INGESTION_STAGES = (
    "Loading repository files as LangChain Documents...",
    "Processing specialized document formats...",
    "Chunking documents...",
    "Generating embeddings and indexing chunks in ChromaDB...",
    "Initializing the RAG retriever...",
)


def ingest_repository(
    repository_url: str,
    embedding_model,
    progress_callback=None,
):
    """
    Ingest a GitHub repository and prepare it for retrieval.

    Args:
        repository_url: URL of the public GitHub repository to ingest.
        embedding_model: Model used to generate document embeddings.
        progress_callback: Optional callback invoked at each ingestion stage.

    Returns:
        tuple: The initialized retriever and the list of available file paths.
    """

    def report_progress(message):
        """Notify the caller of the current ingestion stage."""

        if progress_callback is not None:
            progress_callback(message)

    # Load supported repository files as LangChain Document objects.
    report_progress(INGESTION_STAGES[0])
    loader = GitHubRepositoryLoader(repository_url)
    documents = loader.load()

    if not documents:
        raise ValueError(
            "No supported files were found in the repository."
        )

    # Process documents and extract content from specialized file formats.
    report_progress(INGESTION_STAGES[1])
    processor = Processor()
    documents_processed = processor.process(documents)

    # Split processed documents into smaller chunks for retrieval.
    report_progress(INGESTION_STAGES[2])
    chunker = Chunker()
    documents_chunking = chunker.chunk(documents_processed)

    if not documents_chunking:
        raise ValueError(
            "No document chunks were generated."
        )

    # Generate embeddings and store the chunks in an in-memory ChromaDB collection.
    report_progress(INGESTION_STAGES[3])
    vector_store = ChromaStore(mode="memory")
    vector_store.create(
        documents=documents_chunking,
        embedding_model=embedding_model,
    )

    # Initialize the retriever and collect the indexed file paths.
    report_progress(INGESTION_STAGES[4])
    available_files = vector_store.get_unique_file_paths()
    retriever = Retriever(vector_store)

    return retriever, available_files
