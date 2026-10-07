"""
Tests for the prompt builder method.
"""
from langchain_core.documents import Document
from github_rag.prompt_engineering.prompt_builder import build_context, build_prompt

def test_build_context_includes_document_metadata_and_content():
    document = Document(
        page_content="def retrieve(): ...",
        metadata={
            "file_path": "src/retrieval/retriever.py",
            "source": "https://github.com/user/repo/blob/main/src/retrieval/retriever.py",
        },
    )

    context = build_context([document])

    assert "src/retrieval/retriever.py" in context
    assert "https://github.com/user/repo/blob/main/src/retrieval/retriever.py" in context
    assert "def retrieve(): ..." in context


def test_build_context_includes_multiple_documents():
    documents = [
        Document(
            page_content="retrieval code",
            metadata={"file_path": "retriever.py", "source": "url1"},
        ),
        Document(
            page_content="database code",
            metadata={"file_path": "chroma_store.py", "source": "url2"},
        ),
    ]

    context = build_context(documents)

    assert "retriever.py" in context
    assert "retrieval code" in context
    assert "chroma_store.py" in context
    assert "database code" in context


def test_build_context_with_empty_documents():
    context = build_context([])

    assert context == ""


def test_build_prompt_includes_context():
    document = Document(
        page_content="The Retriever uses MMR.",
        metadata={
            "file_path": "src/retrieval/retriever.py",
            "source": "https://github.com/user/repo/blob/main/src/retrieval/retriever.py",
        },
    )

    prompt = build_prompt([document], "How does retrieval work?")

    assert "The Retriever uses MMR." in prompt
    assert "src/retrieval/retriever.py" in prompt
    assert "https://github.com/user/repo/blob/main/src/retrieval/retriever.py" in prompt


def test_build_prompt_includes_instructions():
    prompt = build_prompt([], "How does retrieval work?")

    assert "Base your answer on the relevant retrieved context." in prompt
    assert "rather than guessing" in prompt
    assert "Cite at the end the source file(s) used." in prompt
    assert "Source: [<File_name>](<Source>)" in prompt