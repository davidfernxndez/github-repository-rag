"""
This module manages the Github repository ingestion interface and progress display.
"""

import streamlit as st

from src_app.repository_ingestion import (
    INGESTION_STAGES,
    ingest_repository,
)


def _render_stages(stages_panel, active_stage):
    """Display completed, active, and pending ingestion stages."""

    with stages_panel.container():
        for index, stage in enumerate(INGESTION_STAGES):
            # Mark stages that have already been completed.
            if index < active_stage:
                st.markdown(f"✅ {stage}")

            # Highlight the stage currently being executed.
            elif index == active_stage:
                st.markdown(f"🔄 **{stage}**")

            # Keep upcoming stages visibly marked as pending.
            else:
                st.markdown(f"⚪ {stage}")


def _update_progress(
    message,
    progress_bar,
    progress_text,
    stages_panel,
    status,
    current_stage,
):
    """Update the progress indicators and return the current stage."""

    # Advance the stage counter without exceeding the total number of stages.
    if current_stage < len(INGESTION_STAGES):
        current_stage += 1

    # Update the progress bar and display the current step.
    progress_bar.progress(
        current_stage / len(INGESTION_STAGES)
    )
    progress_text.caption(
        f"Step {current_stage} of {len(INGESTION_STAGES)}"
    )

    # Refresh the stage list to reflect the current progress.
    _render_stages(stages_panel, current_stage - 1)

    # Display the current ingestion operation in the status panel.
    status.update(
        label=message,
        state="running",
    )

    return current_stage


def _render_completed_stages(stages_panel):
    """Display all ingestion stages as completed."""

    # Render each ingestion stage with a completion indicator.
    with stages_panel.container():
        for stage in INGESTION_STAGES:
            st.markdown(f"✅ {stage}")


def _render_completed_ingestion():
    """Recreate the completed ingestion status after a rerun."""

    # Skip rendering if no repository has been ingested successfully.
    if not st.session_state.get("ingestion_completed", False):
        return

    # Recreate the collapsed status panel with the completed progress.
    with st.status(
        "Repository ready for questions.",
        state="complete",
        expanded=False,
    ):
        st.progress(1.0)
        st.caption("The repository has been indexed successfully. You can now ask questions about its codebase.")

        stages_panel = st.empty()
        _render_completed_stages(stages_panel)


def _reset_repository_state():
    """Clear the previous repository and ingestion status."""

    st.session_state.pop("retriever", None)
    st.session_state.pop("available_files", None)
    st.session_state.pop("repository_url", None)
    st.session_state.pop("ingestion_completed", None)

    # Reset the chat history for the new repository.
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "Welcome to the **GitHub Repository RAG Assistant**!\n\n"
                "To get started:\n"
                "- Ingest a public GitHub repository using the panel above.\n"
                "- Ask questions about its source code, documentation, and structure.\n"
                "- Use `@file_path` to reference specific files and provide context."
            ),
        }
    ]


def _ingest_repository_with_progress(repository_url, embedding_model):
    """Ingest a repository while displaying the progress of each stage."""
    with st.status(
        "Preparing repository ingestion...",
        expanded=True,
    ) as status:

        progress_bar = st.progress(0)
        progress_text = st.empty()
        stages_panel = st.empty()

        current_stage = 0

        # Initialize the progress panel with all stages pending.
        _render_stages(stages_panel, -1)

        def progress_callback(message):
            nonlocal current_stage

            # Update the progress indicators as each ingestion stage starts.
            current_stage = _update_progress(
                message=message,
                progress_bar=progress_bar,
                progress_text=progress_text,
                stages_panel=stages_panel,
                status=status,
                current_stage=current_stage,
            )

        # Execute the ingestion pipeline and report progress through the callback.
        retriever, available_files = ingest_repository(
            repository_url=repository_url,
            embedding_model=embedding_model,
            progress_callback=progress_callback,
        )

        # Mark all stages as completed after successful ingestion.
        progress_bar.progress(1.0)
        progress_text.caption(
            "The repository has been indexed successfully. You can now ask questions about its codebase."
        )
        _render_completed_stages(stages_panel)

        # Collapse the status panel and display the successful completion state.
        status.update(
            label="Repository ready for questions.",
            state="complete",
            expanded=False,
        )

    return retriever, available_files


def render_repository_panel(embedding_model):
    """Render the repository ingestion form and manage its state."""

    st.subheader("Repository")

    st.caption(
        "Connect a public GitHub repository to explore its codebase."
    )

    with st.form("repository_form"):
        repository_url = st.text_input(
            "GitHub repository URL:",
            placeholder="https://github.com/owner/repository",
            help=(
                "Enter the URL of a public GitHub repository "
                "you want to analyze."
            ),
        )
        submitted = st.form_submit_button(
            "Ingest repository",
            type="primary",
            use_container_width=True,
        )

    # Preserve the completed status across Streamlit reruns.
    if not submitted:
        _render_completed_ingestion()
        return

    # Get the repository URL
    repository_url = repository_url.strip()

    if not repository_url:
        st.warning("Please enter a public GitHub repository URL.")
        _render_completed_ingestion()
        return

    # Clear the previous repository and conversation state.
    _reset_repository_state()

    try:
        retriever, available_files = _ingest_repository_with_progress(
            repository_url=repository_url,
            embedding_model=embedding_model,
        )

        # Store the ingestion results for subsequent RAG queries.
        st.session_state["retriever"] = retriever
        st.session_state["available_files"] = available_files
        st.session_state["repository_url"] = repository_url
        st.session_state["ingestion_completed"] = True

    except Exception as error:
        st.error("Repository ingestion failed.")
        st.caption(str(error))
