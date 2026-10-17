"""
Main entry point of the Streamlit app
"""

import streamlit as st

from pages.rag_gui import render_rag_gui
from pages.loading_screen import render_loading_screen
from pages.groq_api_key_guide import render_groq_api_key_guide
from utils.resources import initialize_resources
from styles.css_styles import load_custom_styles


def main():
    """Configure the application, initialize resources, and render the selected page."""

    # --------------------------------------------------
    # Page configuration
    # --------------------------------------------------

    # Set the browser tab title, use the full available width,
    # and expand the sidebar when the application is first opened.
    st.set_page_config(
        page_title="GitHub Repository RAG Assistant",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --------------------------------------------------
    # Resource initialization and CSS styles
    # --------------------------------------------------

    # Apply the application's custom CSS before rendering the interface.
    load_custom_styles()

    # Create a placeholder that can display and later remove the loading screen.
    loading_screen = st.empty()

    # Display the loading screen only while resources are being initialized
    # for the first time in the current user session.
    if not st.session_state.get("resources_initialized", False):
        with loading_screen.container():
            render_loading_screen()

    try:
        # Load the resources required by the application and retrieve
        # the embedding model.
        embedding_model = initialize_resources()

        # Store the initialization status in the session state so that
        # subsequent Streamlit reruns do not display the loading screen again.
        st.session_state["resources_initialized"] = True

    except Exception:
        # Remove the loading screen and stop execution if initialization fails.
        # The user can refresh the page to retry the initialization process.
        loading_screen.empty()

        st.error(
            "The application could not initialize its resources. "
            "Please refresh the page and try again."
        )
        st.stop()

    # Remove the loading screen once initialization has completed successfully.
    loading_screen.empty()

    # --------------------------------------------------
    # Sidebar navigation
    # --------------------------------------------------

    # Initialize the selected section when the user opens the application
    # for the first time in the current session.
    if "section" not in st.session_state:
        st.session_state["section"] = "RAG Assistant"

    # Define the available application sections and their navigation labels
    # and icons. The selected section is tracked in session state.
    SECTIONS = {
        "RAG Assistant": {
            "label": "RAG Assistant",
            "icon": ":material/chat_bubble_outline:",
        },
        "Architecture & Design": {
            "label": "Architecture & Design",
            "icon": ":material/layers:",
        },
        "Groq API Key Guide": {
            "label": "Groq API Key Guide",
            "icon": ":material/key:",
        },
    }

    with st.sidebar:
        # Display the application branding, a visual separator,
        # and the navigation menu heading.
        st.markdown(
            """
            <div style="padding: 4px 0 8px;">
                <div style="font-size: 1.5rem; font-weight: 700; line-height: 1.2;">
                    <span style="color: #60A5FA;">&lt;/&gt;</span>
                    GitHub RAG
                </div>
                <div style="font-size: 0.8rem; opacity: 0.65; line-height: 1.2;">
                    ASSISTANT
                </div>
            </div>

            <hr style="margin: 6px 0 10px; opacity: 1;">

            <div style="font-size: 0.75rem;
                        font-weight: 600;
                        letter-spacing: 0.04em;
                        opacity: 0.65;
                        margin-bottom: 8px;">
                NAVIGATION MENU
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Render one button per section and visually distinguish
        # the currently selected section.
        for section, config in SECTIONS.items():
            is_active = st.session_state["section"] == section

            if st.button(
                config["label"],
                key=f"nav_{section}",
                icon=config["icon"],
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                # Update the selected section and rerun the script
                # to render the corresponding page.
                st.session_state["section"] = section
                st.rerun()

        # Separate the navigation menu from the external project link.
        st.markdown(
            """
            <hr style="margin: 6px 0 10px; opacity: 1;">
            """,
            unsafe_allow_html=True,
        )

        # Provide direct access to the project's public GitHub repository.
        st.markdown(
            """
                <a href="https://github.com/davidfernxndez/github-repository-rag"
                target="_blank"
                style="text-decoration: none; font-size: 0.9rem;">
                    ↗  View project on GitHub
                </a>
                """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------
    # Application interface
    # --------------------------------------------------

    # Render the page associated with the currently selected section.
    # The embedding model is passed to the RAG interface for reuse.
    if st.session_state.section == "RAG Assistant":
        render_rag_gui(embedding_model)

    elif st.session_state.section == "Architecture & Design":
        # TODO: Replace the temporary placeholder with the architecture page.
        # render_architecture_page()
        print("Temporal Hello")

    elif st.session_state.section == "Groq API Key Guide":
        render_groq_api_key_guide()


if __name__ == "__main__":
    main()