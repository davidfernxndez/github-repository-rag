"""
Provides a factory function to create Hugging Face embedding models
compatible with LangChain's HuggingFaceEmbeddings.

Accepts full Hugging Face model IDs or model names without the
'sentence-transformers/' prefix. The default model is
'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'.

Verifies that the model repository exists and is accessible before
initializing the embedding model.
"""

from huggingface_hub import model_info
from huggingface_hub.utils import HfHubHTTPError, RepositoryNotFoundError
from langchain_huggingface import HuggingFaceEmbeddings


DEFAULT_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


def create_embedding_model(
    model_name: str = DEFAULT_MODEL,
) -> HuggingFaceEmbeddings:
    """Create a Hugging Face embedding model.

    Args:
        model_name: Hugging Face model ID. Accepts:
            - A full model ID, e.g.
              "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2".
            - A model name without the "sentence-transformers/" prefix,
              e.g. "paraphrase-multilingual-MiniLM-L12-v2".

            Other model IDs hosted on Hugging Face are also accepted,
            provided they exist and are compatible with Sentence Transformers.

    Returns:
        A configured HuggingFaceEmbeddings instance.

    Raises:
        ValueError: If the model ID is invalid or the repository does not exist.
        RuntimeError: If Hugging Face cannot be reached or the model
            cannot be initialized.
    """
    model_name = model_name.strip()

    if not model_name:
        raise ValueError("model_name cannot be empty.")

    if "/" not in model_name:
        model_name = f"sentence-transformers/{model_name}"

    try:
        model_info(model_name)
    except RepositoryNotFoundError as exc:
        raise ValueError(
            f"Hugging Face model '{model_name}' does not exist "
            "or is not accessible."
        ) from exc
    except HfHubHTTPError as exc:
        raise RuntimeError(
            f"Could not verify Hugging Face model '{model_name}'."
        ) from exc

    try:
        return HuggingFaceEmbeddings(model_name=model_name)
    except Exception as exc:
        raise RuntimeError(
            f"Could not initialize embedding model '{model_name}'. "
            "Check that it is compatible with Sentence Transformers."
        ) from exc