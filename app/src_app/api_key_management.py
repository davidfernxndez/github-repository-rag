"""
Manage LLM initialization, API key selection, and request limits.

Provides functions to initialize the default Groq API connection, create
a generator with a user-provided API key, check request availability,
and update the active LLM configuration stored in Streamlit session state.
"""

import streamlit as st

from github_rag.LLM_generation.generator import LLMGenerator


# Maximum number of requests allowed when using the default API key.
DEFAULT_API_REQUEST_LIMIT = 5

def load_default_llm_generator() -> LLMGenerator:
    """Initialize the shared LLM using the server's Groq API key."""

    # Retrieve the default API key from Streamlit secrets.
    # This keeps the key out of the application source code."""
    api_key = st.secrets.get("GROQ_API_KEY")

    # Return None if no default API key has been configured.
    if not api_key:
        return None

    # Create an LLM generator that uses the default API key.
    return LLMGenerator(mode="API", api_key=api_key)

def create_custom_llm_generator(api_key: str) -> LLMGenerator:
    """Create an LLM instance using a user's own API key."""

    # Create a separate generator configured with the user's API key.
    return LLMGenerator(mode="API", api_key=api_key)


def can_use_api_key() -> bool:
    """Check whether the active LLM can be used."""

    # Custom API keys are not subject to the application's default
    # request counter. Their usage is governed by the provider's limits.
    # The default API key is available only while requests remain.
    return (
        st.session_state.llm_source == "custom"
        or (
            st.session_state.llm_source == "default"
            and st.session_state.default_counter
            < DEFAULT_API_REQUEST_LIMIT
        )
    )

def get_default_request_remaining() -> int:
    """Return the remaining requests for the default API key."""

    # Subtract the number of requests already used from the limit.
    # max() prevents the displayed number from becoming negative.
    return max(
        0,
        DEFAULT_API_REQUEST_LIMIT - st.session_state.default_counter,
    )

def configure_custom_api_key(api_key: str):
    """Replace the current LLM with a user-configured instance."""

    # Remove the active generator reference before creating its replacement.
    st.session_state.pop("llm_generator", None)

    # Initialize a new generator using the user's API key.
    generator = create_custom_llm_generator(api_key)

    # Update the session state to use the custom generator and identify
    # its source so the rest of the application can apply the correct logic.
    st.session_state.llm_generator = generator
    st.session_state.llm_source = "custom"



