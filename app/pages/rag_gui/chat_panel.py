import streamlit as st

from github_rag.prompt_engineering.prompt_builder import build_prompt

def render_chat_panel(llm_generator):
    """Render the chat interface and handle RAG interactions."""

    st.subheader("Chat with your repository")

    # Initialize conversation history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Welcome to the GitHub Repository RAG Assistant!\n\n"
                    "Ingest a public GitHub repository and ask questions "
                    "about its source code, documentation, and structure."
                ),
            }
        ]

    # Display conversation history
    with st.container(height=400, border=True):
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # User input
    query = st.chat_input(
        "Ask a question about the repository...",
        key="rag_chat_input",
    )

    if not query:
        return

    # Check whether a repository has been ingested
    retriever = st.session_state.get("retriever")
    available_files = st.session_state.get("available_files")

    if retriever is None or available_files is None:
        st.warning("Please ingest a GitHub repository before asking questions.")
        return

    if llm_generator is None:
        st.warning(
            "No LLM is configured. Please configure your Groq API Key "
            "before asking questions."
        )
        return

    # Display the user's question
    with st.chat_message("user"):
        st.markdown(query)

    # Add the question to the conversation history
    st.session_state.chat_history.append(
        {"role": "user", "content": query}
    )

    # Run the RAG pipeline
    try:
        with st.chat_message("assistant"):
            with st.spinner("Searching the repository and generating an answer..."):

                # 1. Retrieve relevant document chunks
                retrieval_chunks = retriever.retrieve(
                    query,
                    available_files,
                )

                if not retrieval_chunks:
                    response = (
                        "I couldn't find relevant information in the "
                        "repository to answer your question."
                    )
                else:
                    # 2. Build the prompt using retrieved context
                    prompt = build_prompt(retrieval_chunks, query)

                    # 3. Generate the answer with the LLM
                    response = llm_generator.generate(prompt)

                    if not response:
                        response = "The LLM did not return a response."

            # 4. Display the answer in Markdown
            st.markdown(response)

        # Save the assistant response
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

    except Exception:
        st.error(
            "An error occurred while processing your question. "
            "Please try again."
        )

        # Keep the question in history but allow the user to retry
