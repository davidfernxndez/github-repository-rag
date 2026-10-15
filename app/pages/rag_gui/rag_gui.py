"""
Main GUI module for the GitHub Repository RAG Assistant.

Coordinates the header, repository ingestion panel,
API Key panel, and chat interface.
"""

import streamlit as st

from .header import render_header
from .repository_panel import render_repository_panel
from .api_key_panel import render_api_key_panel
from .chat_panel import render_chat_panel

def render_rag_gui(embedding_model):
    """Render the complete RAG Assistant interface."""

    # Header: title, subtitle and contact information
    render_header()

    # Repository ingestion and API Key configuration
    repository_col, api_key_col = st.columns([2, 1], gap="large")

    with repository_col:
        render_repository_panel(embedding_model=embedding_model)

    with api_key_col:
        render_api_key_panel()

    st.divider()

    # Chat interface
    render_chat_panel()

    st.divider()


    # Display the author's name and links to professional profiles.
    st.markdown(
        """
        <div style="display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-wrap: wrap;
                    gap: 12px;
                    font-size: 0.9rem;
                    margin-top: -2px;
                    text-align: center;">
            <span style="display: flex;
                        align-items: center;
                        gap: 6px;
                        font-weight: 600;">
                <span style="font-size: 1rem;">👤</span>
                David Fernández Martínez
            </span>
            <span style="opacity: 0.4;">·</span>
            <a href="https://github.com/davidfernxndez"
            target="_blank"
            style="text-decoration: none;">
                GitHub ↗
            </a>
            <a href="https://www.linkedin.com/"
            target="_blank"
            style="text-decoration: none;">
                LinkedIn ↗
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )