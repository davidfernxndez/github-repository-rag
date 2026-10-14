import streamlit as st


def render_header():
    """Render the application header and author contact information."""

    st.title("GitHub Repository RAG Assistant")

    st.markdown(
        """
        Ask questions about any public GitHub repository and get
        answers grounded in its source code, with relevant references.
        """
    )

    st.markdown(
        """
        **David Fernández Martínez** ·
        [GitHub](https://github.com/davidfernxndez) ·
        [LinkedIn](https://www.linkedin.com/)
        """
    )

    st.divider()