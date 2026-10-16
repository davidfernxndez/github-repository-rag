"""
Header component for the GitHub Repository RAG Assistant.
"""

import streamlit as st


def render_header():
    """Render the application header and author contact information."""

    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 16px;
                    margin-bottom: 12px;">
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                width: 60px;
                height: 60px;
                flex-shrink: 0;
                background-color: #DBEAFE;
                border-radius: 12px;
                font-size: 30px;
                line-height: 1;
                font-weight: 600;
                color: #2563EB;
            ">
                &lt;/&gt;
            </div>
            <div>
                <h1 style="margin: 0; padding: 0; line-height: 1.2;">
                    GitHub Repository
                    <span style="color: #60A5FA;">
                        RAG Assistant
                    </span>
                </h1>
                <p style="margin: 6px 0 0 0; opacity: 0.7;
                          font-size: 1.05rem;">
                    AI-powered codebase exploration
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        **Ask questions about any public GitHub repository and get
        AI-generated answers grounded in its source code,
        with relevant file references.**
        """
    )

    # Display the author's name and links to professional profiles.
    st.markdown(
        """
        <div style="display: flex; align-items: center;
                    flex-wrap: wrap; gap: 12px;
                    font-size: 0.9rem; margin-top: 2px;">
            <span style="display: flex; align-items: center; gap: 6px;
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

    st.divider()
