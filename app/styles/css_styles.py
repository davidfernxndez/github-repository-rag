"""
Custom CSS styles.
"""

import streamlit as st

def load_custom_styles():
    """Apply custom CSS styles to the application."""

    # Assistant icon in the chat panel
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

    # Sidebar navigation buttons.
    st.markdown(
        """
        <style>
        /* Sidebar background and default text color. */
        [data-testid="stSidebar"] {
            background-color: #0F172A;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #E2E8F0;
        }

        /* Sidebar navigation buttons. */
        [data-testid="stSidebar"] button {
            border-radius: 8px;
            justify-content: flex-start;
            transition: background-color 0.2s ease,
                        border-color 0.2s ease,
                        color 0.2s ease;
        }

        /* Inactive navigation items. */
        [data-testid="stSidebar"] button[kind="secondary"] {
            background-color: transparent;
            color: #CBD5E1;
            border-color: transparent;
        }

        [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: #1E293B;
            color: #FFFFFF;
            border-color: #334155;
        }

        /* Active navigation item. */
        [data-testid="stSidebar"] button[kind="primary"] {
            background-color: #2563EB;
            color: #FFFFFF;
            border-color: #2563EB;
        }

        [data-testid="stSidebar"] button[kind="primary"]:hover {
            background-color: #1D4ED8;
            border-color: #1D4ED8;
            color: #FFFFFF;
        }

        /* Sidebar links. */
        [data-testid="stSidebar"] a {
            color: #93C5FD;
        }

        [data-testid="stSidebar"] a:hover {
            color: #BFDBFE;
        }

        /* Sidebar dividers. */
        [data-testid="stSidebar"] hr {
            border-color: #334155;
        }

        /* Keep sidebar icons visible against the dark background. */
        [data-testid="stSidebar"] svg {
            color: inherit;
        }

        /* Keep the sidebar collapse button visible. */
        [data-testid="stBaseButton-headerNoPadding"] {
            opacity: 1 !important;
            visibility: visible !important;
            color: #FFFFFF !important;
        }

        [data-testid="stBaseButton-headerNoPadding"] span,
        [data-testid="stBaseButton-headerNoPadding"] [data-testid="stIconMaterial"] {
            color: #FFFFFF !important;
        }

        /* Hover effect. */
        [data-testid="stBaseButton-headerNoPadding"]:hover {
            background-color: #1E293B !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Specific containers background
    st.markdown(
    """
        <style>
        /* Chat interface. */
        div[data-testid="stLayoutWrapper"]:has(
            > div[data-testid="stVerticalBlock"][data-test-scroll-behavior="scroll-to-bottom"]
        ) {
            background-color: #FFFFFF !important;
            border-radius: 12px;
        }
        /* Repository ingestion form. */
        div[data-testid="stForm"] {
            background-color: #FFFFFF;
            border: 1.5px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
        }
        /* API key limit notice container. */
        div[data-testid="stLayoutWrapper"]:has(
            > div[data-testid="stVerticalBlock"] div[data-testid="stAlert"]
        ) {
            background-color: #FFFFFF;
            border: 1.5px solid #E2E8F0;
            border-radius: 12px;
            padding: 8px;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )