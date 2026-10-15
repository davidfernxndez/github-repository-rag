"""
Custom CSS styles.
"""

import streamlit as st


def load_custom_styles():
    """Apply custom CSS styles to the application."""

    st.markdown(
        """
        <style>
        /* Customize the assistant chat avatar. */
        [data-testid="stChatMessageAvatarAssistant"] {
            color: #2563EB !important;
            background-color: #DBEAFE !important;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
