import streamlit as st

from github_rag.embedding.embedding_model import create_embedding_model
from src_app.api_key_management import load_default_llm_generator


@st.cache_resource
def get_embedding_model():
    """Load and cache the shared embedding model."""
    return create_embedding_model()


@st.cache_resource
def get_default_llm_generator():
    """Load and cache the default LLM generator."""
    return load_default_llm_generator()


def initialize_resources():
    """Initialize shared application resources."""
    embedding_model = get_embedding_model()
    llm_generator = get_default_llm_generator()

    return embedding_model, llm_generator