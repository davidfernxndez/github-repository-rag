"""
Initialize and manage shared application resources.

Caches the embedding model, default LLM generator, and Groq tutorial
images to avoid unnecessary reinitialization and disk reads.

Initializes the session-specific LLM configuration and request counter
when a new Streamlit session starts.
"""

import streamlit as st
from pathlib import Path
from github_rag.embedding.embedding_model import create_embedding_model
from src_app.api_key_management import load_default_llm_generator

# --------------------------------------------------
# Resource paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GROQ_IMAGES_DIR = PROJECT_ROOT / "images" / "groq"
ARCHITECTURE_IMAGE_PATH = PROJECT_ROOT / "images" / "architecture_design.png"

# --------------------------------------------------
# Cached shared resources
# --------------------------------------------------

@st.cache_resource
def get_embedding_model():
    """Load and cache the shared embedding model."""

    # Reuse the same embedding model across Streamlit sessions.
    # The model is loaded again only when the cache is invalidated.
    return create_embedding_model()


@st.cache_resource
def get_default_llm_generator():
    """Load and cache the default LLM generator."""

    # Reuse the default LLM generator instead of creating a new instance
    # on every script rerun or session initialization.
    return load_default_llm_generator()

@st.cache_data
def load_groq_image(image_name: str) -> bytes:
    """Load and cache a Groq tutorial image."""

    # Read the image from the project's images/groq directory.
    image_path = GROQ_IMAGES_DIR / image_name

    return image_path.read_bytes()

@st.cache_data
def load_architecture_image() -> bytes:
    """Load and cache the system architecture diagram."""
    return ARCHITECTURE_IMAGE_PATH.read_bytes()

# --------------------------------------------------
# Session initialization
# --------------------------------------------------

def initialize_resources():
    """Initialize application resources and session state."""

    # Retrieve the cached embedding model used to process repository content
    # and user queries.
    embedding_model = get_embedding_model()

    # Initialize the LLM configuration only once per user session.
    # Existing session settings are preserved across Streamlit reruns.
    if "llm_generator" not in st.session_state:

        # Assign the shared default generator
        st.session_state.llm_generator = get_default_llm_generator()

        # Assign default source to identify the Free API access service
        st.session_state.llm_source = "default"

        # Count requests made using the default API key in this session.
        st.session_state.default_counter = 0

    # Return the embedding model for use by the RAG system.
    return embedding_model
