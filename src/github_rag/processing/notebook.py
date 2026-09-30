"""
Jupyter Notebook document processor.

This module provides the NotebookProcessor class, which converts
Jupyter Notebook cells into individual LangChain Documents.
"""

# Json to process notebook content
import json

# LangChain Document structure
from langchain_core.documents import Document

# Import available languages
from github_rag.ingestion.filters import LANGUAGE_TO_EXTENSION

class NotebookProcessor:
    """
    Process Jupyter Notebook documents cell by cell.

    Each non-empty notebook cell is converted into a separate
    LangChain Document. Cell outputs are intentionally ignored.
    """

    def process(self, document: Document) -> list[Document]:
        """
        Convert a Jupyter Notebook into one Document per non-empty cell.

        Args:
            document: Document
                A LangChain Document containing the raw JSON
                content of a Jupyter Notebook.

        Returns:
            A list of Documents representing the non-empty notebook cells.
        """
        # The notebook is stored as JSON inside the input Document.
        notebook = self._parse_notebook(document.page_content)

        # The language is defined at notebook level and is used to
        # determine the file type of code cells.
        language = self._get_language(notebook)

        processed_documents: list[Document] = []

        # Each notebook cell becomes an independent Document.
        # Cell outputs are ignored because only the cell source is extracted.
        for cell_index, cell in enumerate(notebook.get("cells", [])):
            cell_type = cell.get("cell_type")
            source = self._get_cell_source(cell)

            # Empty cells do not contain useful information for retrieval.
            if not source.strip():
                continue

            file_type = self._get_file_type(
                cell_type=cell_type,
                language=language,
            )
            
            # Preserve the original document metadata and add information
            # specific to the notebook cell.
            metadata = {
                **document.metadata,
                "file_type": file_type,
                "source_file_type": ".ipynb",
                "cell_index": cell_index,
                "cell_type": cell_type,
            }

            processed_documents.append(
                Document(
                    page_content=source,
                    metadata=metadata,
                )
            )

        return processed_documents

    @staticmethod
    def _parse_notebook(content: str) -> dict:
        """
        Parse notebook JSON content.

        Args:
            content: Raw JSON content of the notebook.

        Returns:
            Parsed notebook content.
        """
        try:
            notebook = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Invalid Jupyter Notebook JSON content."
            ) from exc

        # A valid notebook must be represented by a JSON object,
        # which is loaded by Python as a dictionary.
        if not isinstance(notebook, dict):
            raise ValueError(
                "Invalid Jupyter Notebook content. "
                "Expected a JSON object."
            )

        return notebook

    @staticmethod
    def _get_language(notebook: dict) -> str | None:
        """
        Get the programming language declared by the notebook.

        The language information is obtained from ``language_info``
        first and falls back to ``kernelspec`` when necessary.

        Args:
            notebook: dict 
                Parsed notebook content as a dictionary.

        Returns:
            Detected language.
        """
        metadata = notebook.get("metadata", {})

        # ``language_info`` is the preferred source because it directly
        # describes the language used by the notebook.
        language_info = metadata.get("language_info", {})
        language = language_info.get("name")

        if language:
            return language.lower()

        # Some notebooks may not contain ``language_info`` but may
        # specify the language through their kernel specification.
        kernelspec = metadata.get("kernelspec", {})
        language = kernelspec.get("language")

        if language:
            return language.lower()

        return None

    @staticmethod
    def _get_cell_source(cell: dict) -> str:
        """
        Extract the source code or Markdown content from a cell.

        Jupyter may represent ``source`` either as a string or as
        a list of strings.
        """
        source = cell.get("source", "")
        
        # The notebook format may store source as a list of lines.
        # Joining the elements reconstructs the original cell content.
        if isinstance(source, list):
            return "".join(source)

        if isinstance(source, str):
            return source

        return ""

    def _get_file_type(
        self,
        cell_type: str | None,
        language: str | None,
    ) -> str:
        """
        Determine the file type associated with a notebook cell.
        """
        # Markdown cells are always treated as Markdown documents.
        if cell_type == "markdown":
            return ".md"

        if cell_type == "code":
            # Code cells use the notebook's programming language.
            # Unknown languages fall back to plain text.
            return LANGUAGE_TO_EXTENSION.get(
                language,
                ".txt",
            )

        return ".txt"