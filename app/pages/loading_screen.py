import streamlit as st

def render_loading_screen():
    """Display a temporary loading screen while initializing resources."""

    st.html("""
    <style>
    .loading-screen {
        min-height: 65vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2rem;
        font-family: sans-serif;
    }

    .loading-icon {
        font-size: 3.5rem;
        font-weight: 600;
        color: #60A5FA;
        margin-bottom: 1rem;
        line-height: 1;
    }

    .loading-title {
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    .loading-message {
        font-size: 1.05rem;
        max-width: 560px;
        line-height: 1.7;
        opacity: 0.8;
    }

    .loading-spinner {
        width: 40px;
        height: 40px;
        margin: 1.8rem 0;
        border: 4px solid rgba(128, 128, 128, 0.2);
        border-top-color: #2563EB;
        border-radius: 50%;
        animation: spin 0.9s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    @media (prefers-reduced-motion: reduce) {
        .loading-spinner {
            animation: none;
        }
    }
    </style>

    <div class="loading-screen">
        <div class="loading-icon">&lt;/&gt;</div>

        <div class="loading-title">
            Preparing the RAG Assistant
        </div>

        <div class="loading-spinner"></div>

        <div class="loading-message">
            We are initializing the resources required by the
            application, including the embedding model used to
            retrieve relevant information from GitHub repositories.
            <br><br>
            The initial setup may take a few moments.
            Thank you for your patience.
        </div>
    </div>
    """)