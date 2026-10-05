"""
Tests for file reference detection.

These tests verify that the files mentioned in user queries are 
detected to use them as metadata filter in RAG retrieval.
"""

from github_rag.retrieval.file_reference import find_referenced_files


# Example repository file paths
AVAILABLE_FILES = [
    "README.md",
    "data/data_info.md",
    "enviroment.yml",
    "main.ipynb",
    "performance_experiment.ipynb",
    "scalability_experiments.ipynb",
    "scripts/AL_methods.py",
    "scripts/AL_performance.py",
    "scripts/AL_scalability.py",
    "scripts/config.py",
    "scripts/dowload_data.py",
    "scripts/plot_results.py",
]


def test_find_file_by_full_path():
    query = "Explain scripts/AL_methods.py"

    result = find_referenced_files(query, AVAILABLE_FILES)

    assert result == ["scripts/AL_methods.py"]


def test_find_file_by_full_path_with_at_prefix():
    query = "Explain @scripts/AL_methods.py"

    result = find_referenced_files(query, AVAILABLE_FILES)

    assert result == ["scripts/AL_methods.py"]


def test_find_file_by_basename():
    query = "Explain AL_methods.py"

    result = find_referenced_files(query, AVAILABLE_FILES)

    assert result == ["scripts/AL_methods.py"]


def test_directory_name_is_not_detected_as_file():
    query = "Explain scripts"

    result = find_referenced_files(query, AVAILABLE_FILES)

    assert result == []


def test_unknown_file_returns_empty_list():
    query = "Explain unknown.py"

    result = find_referenced_files(query, AVAILABLE_FILES)

    assert result == []


def test_multiple_file_references():
    query = "Compare AL_methods.py and AL_performance.py"

    result = find_referenced_files(query, AVAILABLE_FILES)

    assert result == [
        "scripts/AL_methods.py",
        "scripts/AL_performance.py",
    ]


def test_multiple_references_with_at_prefix():
    query = "Compare @AL_methods.py and @AL_performance.py"

    result = find_referenced_files(query, AVAILABLE_FILES)

    assert result == [
        "scripts/AL_methods.py",
        "scripts/AL_performance.py",
    ]


def test_duplicate_file_reference_is_returned_once():
    query = "Explain AL_methods.py and AL_methods.py"

    result = find_referenced_files(query, AVAILABLE_FILES)

    assert result == ["scripts/AL_methods.py"]


def test_similar_filename_is_not_matched():
    available_files = [
        "scripts/AL_methods.py",
        "scripts/AL_methods.py.bak",
    ]

    query = "Explain AL_methods.py"

    result = find_referenced_files(query, available_files)

    assert result == ["scripts/AL_methods.py"]


def test_basename_matching_returns_multiple_files():
    available_files = [
        "scripts/AL_methods.py",
        "tests/AL_methods.py",
        "README.md",
    ]

    query = "Explain AL_methods.py"

    result = find_referenced_files(query, available_files)

    assert result == [
        "scripts/AL_methods.py",
        "tests/AL_methods.py",
    ]

def test_full_path_resolves_ambiguous_basename():
    available_files = [
        "scripts/AL_methods.py",
        "tests/AL_methods.py",
        "README.md",
    ]

    query = "Explain tests/AL_methods.py"

    result = find_referenced_files(query, available_files)

    assert result == ["tests/AL_methods.py"]