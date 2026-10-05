"""
Utilities for detecting file references in user queries.

A file reference can be expressed either as a complete repository path
or as a file basename. The optional '@' prefix is supported.

Examples:
    - Query contains @scripts/AL_methods.py -> scripts/AL_methods.py detected. 
    - Query contains scripts/AL_methods.py -> scripts/AL_methods.py detected.
    - Query contains AL_methods.py -> scripts/AL_methods.py detected
    - Query contains scripts -> No files detected.
    - Query contains AL_methods -> No files detected.
"""

import re
from pathlib import PurePosixPath


def find_referenced_files(
    query: str,
    available_files: list[str],
) -> list[str]:
    """
    Find repository files referenced in a user query.

    Full file paths have priority over basenames. If a basename matches
    multiple files, all matching paths are returned.

    Args:
        query: User query.
        available_files: File paths available in the repository.

    Returns:
        A list of repository paths referenced in the query. Returns an
        empty list if no available file is referenced.
    """
    # Delete @ preffix if exists
    normalized_query = _normalize_query(query)

    # First, look for complete repository paths.
    path_matches = _find_path_matches(
        normalized_query,
        available_files,
    )

    if path_matches:
        return path_matches

    # If no complete path was found, look for file basenames.
    return _find_basename_matches(
        normalized_query,
        available_files,
    )


def _normalize_query(query: str) -> str:
    """Normalize the query before looking for file references."""
    return query.replace("@", " ")


def _find_path_matches(
    query: str,
    available_files: list[str],
) -> list[str]:
    """Find complete repository paths mentioned in the query."""
    matches = []

    for file_path in available_files:
        if _contains_path(query, file_path):
            matches.append(file_path)

    return matches


def _find_basename_matches(
    query: str,
    available_files: list[str],
) -> list[str]:
    """Find files whose basename is mentioned in the query."""
    matches = []

    for file_path in available_files:
        # Extract only the filename from the complete path
        filename = PurePosixPath(file_path).name

        if _contains_filename(query, filename):
            matches.append(file_path)

    return matches


def _contains_path(query: str, file_path: str) -> bool:
    """
    Check whether a complete repository path occurs in the query.

    The match is case-sensitive and requires the path to be delimited
    from surrounding characters.
    """
    pattern = rf"(?<![\w/.-]){re.escape(file_path)}(?![\w/.-])"

    return re.search(pattern, query) is not None


def _contains_filename(query: str, filename: str) -> bool:
    """
    Check whether a filename occurs in the query.

    The filename must appear as a complete token rather than as an
    arbitrary substring.
    """
    pattern = rf"(?<![\w.-]){re.escape(filename)}(?![\w.-])"

    return re.search(pattern, query) is not None