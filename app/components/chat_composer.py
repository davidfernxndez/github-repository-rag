"""Define and render the custom Streamlit chat composer component.

This module loads the HTML, CSS, and JavaScript assets that implement the
chat input interface, registers them as a Streamlit component, and exposes
a helper function to pass available repository files to the frontend and
retrieve submitted message data.
"""

from pathlib import Path
import streamlit as st


# Resolve the directory containing the component's frontend assets.
_COMPONENT_DIR = Path(__file__).parent

# Load the HTML structure, CSS styles, and JavaScript behavior of the composer.
# UTF-8 encoding ensures that the assets are read consistently.
HTML = (_COMPONENT_DIR / "chat_composer.html").read_text(
    encoding="utf-8"
)

CSS = (_COMPONENT_DIR / "chat_composer.css").read_text(
    encoding="utf-8"
)

JS = (_COMPONENT_DIR / "chat_composer.js").read_text(
    encoding="utf-8"
)


# Register the frontend assets as a reusable Streamlit component.
_chat_composer = st.components.v2.component(
    name="github_rag_chat_composer",
    html=HTML,
    css=CSS,
    js=JS,
)


def render_chat_composer(
    available_files: list[str],
) -> dict | None:
    """Render the chat composer and return submitted message data.

    Args:
        available_files: Repository file paths available for autocomplete
            and file referencing in the chat input.

    Returns:
        The submitted component payload, containing the message text and
        selected repository files, or None if no submission is available.
    """

    # Render the component with the available repository files.
    # The stable key identifies this component instance across reruns.
    # The no-op callback satisfies the submission callback interface;
    # the submitted value is retrieved from the component result below.
    result = _chat_composer(
        key="github_rag_chat_composer",
        data={"available_files": available_files},
        on_submit_change=lambda: None,
    )

    # Return the payload associated with the component's submit trigger.
    return result.submit
