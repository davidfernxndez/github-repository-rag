"""
Tests the creation of Hugging Face embedding models using full model IDs
and model names without the 'sentence-transformers/' prefix. Also verifies
that attempting to load a nonexistent model raises the expected exception.
"""

import pytest

from github_rag.embedding.embedding_model import create_embedding_model

# Model used to test initialization with and without the prefix.
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
FULL_MODEL_NAME = f"sentence-transformers/{MODEL_NAME}"


def test_load_model_with_prefix():
    """Test loading an existing model using its full Hugging Face ID."""

    # Initialize the model using its complete repository ID.
    model = create_embedding_model(FULL_MODEL_NAME)

    # Verify that the model was created successfully.
    assert model is not None


def test_load_model_without_prefix():
    """Test loading an existing model without the sentence-transformers prefix."""

    # Initialize the model using only its name.
    # The function should automatically add the required prefix.
    model = create_embedding_model(MODEL_NAME)

    # Verify that the model was created successfully.
    assert model is not None


def test_load_nonexistent_model():
    """Test that loading a nonexistent model raises ValueError."""

    # Verify that the function raises ValueError when the model
    # does not exist on Hugging Face.
    with pytest.raises(ValueError, match="does not exist"):
        create_embedding_model("nonexistent-model-123456789")