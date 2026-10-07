"""
This module constructs the context provided to the LLM from the documents
retrieved by the retrieval component and combines it with the user's query
and the instructions that define the expected response behavior.
"""

from langchain_core.documents import Document


def build_context(documents: list[Document]) -> str:
    """Build the context section from retrieved documents.

    Each document is represented by its file path, source URL, and content.
    These elements provide the LLM with both the information needed to answer
    the query and the metadata required to cite the source files.

    Args:
        documents: List of LangChain documents retrieved for the user's query.

    Returns:
        A formatted string containing the file path, source URL, and content
        of each retrieved document.
    """

    context = "\n\n".join(
        f"""File_name: {doc.metadata.get("file_path")}
    Source: {doc.metadata.get("source")}

    Content:
    {doc.page_content}"""
        for doc in documents
    )

    return context


def build_prompt(documents: list[Document], query: str) -> str:
    """Build the prompt for the LLM from retrieved documents and user query.

    The prompt provides the LLM with the retrieved context, the user's query,
    and instructions for generating a grounded answer with source citations.

    Args:
        documents: List of LangChain documents retrieved for the user's query.
        query: User's question to be answered by the LLM.

    Returns:
        A formatted prompt containing the retrieved context, user query,
        and instructions for generating the final answer.
    """

    # Format the context using the retrieved documents
    context = build_context(documents)

    # Build the prompt with LLM instructions
    prompt = f"""
    You are an assistant specialized in answering questions
    about GitHub repositories.

    Use the retrieved context to answer the user's question.

    Context:
    {context}

    Question:
    {query}

    Instructions:
    - Base your answer on the relevant retrieved context.
    - If the context does not contain enough information, explicitly state that
    rather than guessing.
    - Cite at the end the source file(s) used.
    - Format each citation as a Markdown link using the file name as the link text:
    Source: [<File_name>](<Source>)
    """
    
    return prompt