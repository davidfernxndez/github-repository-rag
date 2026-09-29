"""
File filtering rules for GitHub repository ingestion.

This module defines which files are relevant to the RAG pipeline
and which directories should be excluded during repository traversal.
"""

from pathlib import PurePath

# File extensions supported by the initial RAG implementation.
# These formats are commonly used for source code, documentation,
# configuration files, and SQL scripts.
ALLOWED_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".sql",
    ".ipynb",
    ".pdf"
}

# Directories that should not be processed during repository ingestion.
# They typically contain generated files, dependencies, virtual
# environments, build artifacts, or Git internal data.
IGNORED_DIRECTORIES = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
}


def should_include_file(path: str) -> bool:
    """
    Determine whether a repository file should be included in the RAG.

    A file is included only if its extension is supported and it does
    not belong to an ignored directory.

    Args:
        path: File path relative to the repository root.

    Returns:
        True if the file should be included in the RAG, otherwise False.
    """

    # Convert the string path into a path object so that its individual
    # components and file extension can be inspected.
    file_path = PurePath(path)

    # Ignore files located inside any excluded directory.
    if any(
        directory in IGNORED_DIRECTORIES
        for directory in file_path.parts
    ):
        return False

    # Include the file only if its extension is supported.
    return file_path.suffix.lower() in ALLOWED_EXTENSIONS