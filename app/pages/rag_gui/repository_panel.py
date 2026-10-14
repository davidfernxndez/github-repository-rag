import streamlit as st

from src_app.repository_ingestion import ingest_repository


def render_repository_panel(embedding_model):
    """Render the repository ingestion form and manage its state."""

    st.subheader("Repository")

    with st.form("repository_form"):
        repository_url = st.text_input(
            "GitHub repository URL",
            placeholder="https://github.com/owner/repository",
        )

        submitted = st.form_submit_button(
            "Ingest repository",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    repository_url = repository_url.strip()

    if not repository_url:
        st.warning("Please enter a GitHub repository URL.")
        return

    # Reset the previous repository state before re-ingestion
    st.session_state.pop("retriever", None)
    st.session_state.pop("available_files", None)
    st.session_state.pop("repository_url", None)

    try:
        with st.status(
            "Starting repository ingestion...",
            expanded=True,
        ) as status:

            def update_progress(message):
                status.update(
                    label=message,
                    state="running",
                )

            retriever, available_files = ingest_repository(
                repository_url=repository_url,
                embedding_model=embedding_model,
                progress_callback=update_progress,
            )

            # Store resources for subsequent chat interactions
            st.session_state["retriever"] = retriever
            st.session_state["available_files"] = available_files
            st.session_state["repository_url"] = repository_url

            status.update(
                label="Repository ingested successfully!",
                state="complete",
                expanded=False,
            )

        #st.success(
        #    f"Repository ready. {len(available_files)} files indexed."
        #)

    except Exception as error:
        st.error(f"Repository ingestion failed: {error}")
