from threading import Lock
import streamlit as st

from github_rag.LLM_generation.generator import LLMGenerator


DEFAULT_API_REQUEST_LIMIT = 10

@st.cache_resource(show_spinner="Initializing default LLM...")
def load_default_llm_generator() -> LLMGenerator:
    """Initialize the shared LLM using the server's Groq API key."""
    api_key = st.secrets.get("GROQ_API_KEY")

    if not api_key:
        return None

    return LLMGenerator(mode="API", api_key=api_key)

def create_custom_llm_generator(api_key: str) -> LLMGenerator:
    """Create an LLM instance using a user's own API key."""
    return LLMGenerator(mode="API", api_key=api_key)


def configure_custom_api_key(api_key: str):
    """Replace the current LLM with a user-configured instance."""
    # Remove the previous instance before creating the new one.
    st.session_state.pop("llm_generator", None)

    generator = create_custom_llm_generator(api_key)

    st.session_state.llm_generator = generator
    st.session_state.llm_source = "custom"
    st.session_state.show_api_key_form = False



@st.cache_resource
def get_default_api_quota():
    """Return the shared default API quota state."""
    return {
        "count": 0,
        "lock": Lock(),
    }


def reserve_default_api_request() -> bool:
    """Reserve one of the ten default API requests."""
    quota = get_default_api_quota()

    with quota["lock"]:
        if quota["count"] >= DEFAULT_API_REQUEST_LIMIT:
            return False

        quota["count"] += 1
        return True


def get_default_api_usage() -> int:
    """Return the number of reserved default API requests."""
    quota = get_default_api_quota()

    with quota["lock"]:
        return quota["count"]


def create_custom_llm_generator(api_key: str) -> LLMGenerator:
    """Create an LLM instance using a user's own API key."""
    return LLMGenerator(mode="API", api_key=api_key)