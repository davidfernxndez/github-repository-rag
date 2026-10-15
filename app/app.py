import streamlit as st

from pages.rag_gui import render_rag_gui
from pages.loading_screen import render_loading_screen
from utils.resources import initialize_resources
from styles import load_custom_styles

def main():
    # --------------------------------------------------
    # Page configuration
    # --------------------------------------------------

    st.set_page_config(
        page_title="GitHub Repository RAG Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # --------------------------------------------------
    # Resource initialization and CSS styles
    # --------------------------------------------------
    load_custom_styles()
    loading_screen = st.empty()

    # Show the loading screen once per user session.
    if not st.session_state.get("resources_initialized", False):
        with loading_screen.container():
            render_loading_screen()

    try:
        embedding_model = initialize_resources()
        st.session_state["resources_initialized"] = True

    except Exception:
        loading_screen.empty()
        st.error(
            "The application could not initialize its resources. "
            "Please refresh the page and try again."
        )
        st.stop()

    # Remove the loading screen after initialization.
    loading_screen.empty()

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    if "section" not in st.session_state:
        st.session_state.section = "RAG Assistant"

    with st.sidebar:
        st.title("Navigation")

        # Add your navigation controls here.
        # ...


    # --------------------------------------------------
    # Application interface
    # --------------------------------------------------

    if st.session_state.section == "RAG Assistant":
        render_rag_gui(embedding_model)


if __name__ == "__main__":
    main()
