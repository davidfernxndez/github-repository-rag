"""
Unit tests for the Jupyter Notebook document processor.

These tests verify that notebook cells are correctly converted into
LangChain Documents, that empty cells and outputs are ignored, and
that document metadata is preserved and extended correctly.
"""

import json

from langchain_core.documents import Document

from github_rag.processing.notebook import NotebookProcessor


def test_notebook_processing():
    """
    Test that a notebook is converted into one Document per non-empty cell.

    Markdown cells should be identified as Markdown files, while code cells
    should use the notebook's programming language as their file type.
    """
    notebook = {
        "metadata": {
            "language_info": {
                "name": "python"
            }
        },
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Introduction"],
            },
            {
                "cell_type": "code",
                "source": ["print('Hello')"],
            },
        ],
    }

    # The notebook is represented as JSON inside the input Document,
    # matching the format produced by the ingestion stage.
    document = Document(
        page_content=json.dumps(notebook),
        metadata={
            "repository": "owner/repository",
            "file_path": "notebooks/example.ipynb",
            "file_type": ".ipynb",
            "source": (
                "https://github.com/owner/repository/"
                "blob/main/notebooks/example.ipynb"
            ),
            "branch": "main",
        },
    )

    processor = NotebookProcessor()

    processed_documents = processor.process(document)

    assert len(processed_documents) == 2

    assert processed_documents[0].page_content == "# Introduction"
    assert processed_documents[0].metadata["file_type"] == ".md"

    assert processed_documents[1].page_content == "print('Hello')"
    assert processed_documents[1].metadata["file_type"] == ".py"


def test_empty_cells_are_ignored():
    """
    Test that empty and whitespace-only cells are not processed.
    """
    notebook = {
        "metadata": {
            "language_info": {
                "name": "python"
            }
        },
        "cells": [
            {
                "cell_type": "markdown",
                "source": [],
            },
            {
                "cell_type": "code",
                "source": ["x = 10"],
            },
            {
                "cell_type": "code",
                "source": ["   "],
            },
        ],
    }

    document = Document(
        page_content=json.dumps(notebook),
        metadata={},
    )

    processor = NotebookProcessor()

    processed_documents = processor.process(document)

    assert len(processed_documents) == 1
    assert processed_documents[0].page_content == "x = 10"


def test_notebook_metadata_is_preserved():
    """
    Test that original document metadata is preserved and cell-specific
    metadata is added to the processed Documents.
    """
    notebook = {
        "metadata": {
            "language_info": {
                "name": "python"
            }
        },
        "cells": [
            {
                "cell_type": "code",
                "source": ["x = 10"],
            },
        ],
    }

    original_metadata = {
        "repository": "owner/repository",
        "file_path": "notebook.ipynb",
        "file_type": ".ipynb",
        "source": (
            "https://github.com/owner/repository/"
            "blob/main/notebook.ipynb"
        ),
        "branch": "main",
    }

    document = Document(
        page_content=json.dumps(notebook),
        metadata=original_metadata,
    )

    processor = NotebookProcessor()

    processed_documents = processor.process(document)

    metadata = processed_documents[0].metadata

    # Original metadata from the ingestion stage should be preserved.
    assert metadata["repository"] == "owner/repository"
    assert metadata["file_path"] == "notebook.ipynb"
    assert metadata["source"] == original_metadata["source"]
    assert metadata["branch"] == "main"

    # The processor should add metadata describing the notebook cell.
    assert metadata["source_file_type"] == ".ipynb"
    assert metadata["cell_index"] == 0
    assert metadata["cell_type"] == "code"
    assert metadata["file_type"] == ".py"


def test_notebook_outputs_are_ignored():
    """
    Test that notebook cell outputs are not included in the Document content.
    """
    notebook = {
        "metadata": {
            "language_info": {
                "name": "python"
            }
        },
        "cells": [
            {
                "cell_type": "code",
                "source": ["print('Hello')"],
                "outputs": [
                    {
                        "output_type": "stream",
                        "text": ["Hello\n"],
                    }
                ],
            },
        ],
    }

    document = Document(
        page_content=json.dumps(notebook),
        metadata={},
    )

    processor = NotebookProcessor()

    processed_documents = processor.process(document)

    assert len(processed_documents) == 1

    # Only the cell source should be preserved; outputs are ignored.
    assert processed_documents[0].page_content == "print('Hello')"