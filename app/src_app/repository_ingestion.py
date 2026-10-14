from github_rag.ingestion.repository import GitHubRepositoryLoader
from github_rag.processing.processor import Processor
from github_rag.chunking.chunker import Chunker
from github_rag.vectordatabase.chroma_store import ChromaStore
from github_rag.retrieval.retriever import Retriever


def ingest_repository(
    repository_url: str,
    embedding_model,
    progress_callback=None,
):
    """
    Ingest a GitHub repository and prepare it for retrieval.

    Returns:
        tuple: (retriever, available_files)
    """

    def report_progress(message):
        if progress_callback is not None:
            progress_callback(message)

    # Load repository files
    report_progress("Downloading repository files...")
    loader = GitHubRepositoryLoader(repository_url)
    documents = loader.load()

    if not documents:
        raise ValueError(
            "No supported files were found in the repository."
        )

    # Process documents
    report_progress("Processing repository files...")
    processor = Processor()
    documents_processed = processor.process(documents)

    # Split documents into chunks
    report_progress("Splitting documents into chunks...")
    chunker = Chunker()
    documents_chunking = chunker.chunk(documents_processed)

    if not documents_chunking:
        raise ValueError(
            "No document chunks were generated."
        )

    # Create the in-memory vector store
    report_progress("Generating embeddings and indexing chunks...")
    vector_store = ChromaStore(mode="memory")

    vector_store.create(
        documents=documents_chunking,
        embedding_model=embedding_model,
    )

    # Prepare the retriever
    available_files = vector_store.get_unique_file_paths()
    retriever = Retriever(vector_store)

    return retriever, available_files
