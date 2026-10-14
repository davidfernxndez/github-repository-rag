"""
Main GUI module for the GitHub Repository RAG Assistant.

Coordinates the header, repository ingestion panel,
Groq API Key panel, and chat interface.
"""

import streamlit as st

from utils.resources import initialize_resources

from .header import render_header
from .repository_panel import render_repository_panel
from .api_key_panel import render_api_key_panel
from .chat_panel import render_chat_panel

def render_rag_gui(embedding_model, llm_generator):
    """Render the complete RAG Assistant interface."""

    # 1. Header: title, subtitle and contact information
    render_header()

    # 2. Repository ingestion and API Key configuration
    repository_col, api_key_col = st.columns([3, 1], gap="large")

    with repository_col:
        render_repository_panel(embedding_model=embedding_model)

    with api_key_col:
        #render_api_key_panel()
        print("TO DO")

    # 3. Chat interface
    render_chat_panel(llm_generator)
