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
        margin-bottom: 1rem;
    }

    .loading-title {
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    .loading-message {
        font-size: 1.05rem;
        max-width: 600px;
        line-height: 1.7;
        opacity: 0.8;
    }

    .loading-spinner {
        width: 44px;
        height: 44px;
        margin: 1.8rem 0;
        border: 4px solid rgba(128, 128, 128, 0.2);
        border-top-color: #4F8BF9;
        border-radius: 50%;
        animation: spin 0.9s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>

    <div class="loading-screen">
        <div class="loading-icon">🤖</div>

        <div class="loading-title">
            Preparing your RAG Assistant
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