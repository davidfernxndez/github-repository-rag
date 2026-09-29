"""
Tests for the GitHub repository ingestion module.

This module verifies that GitHubRepositoryLoader:
- Correctly validates and parses GitHub repository URLs.
- Successfully clones and reads a repository.
- Converts supported files into LangChain Documents.
- Stores the expected metadata in each Document.
- Generates valid GitHub source URLs.
"""

# Pytest framework
import pytest

# LangChain Document structure 
from langchain_core.documents import Document

# Import the component that we want to test.
from github_rag.ingestion.repository import GitHubRepositoryLoader


# Public GitHub repository used by the integration tests.
#
# The repository is intentionally kept fixed so that all integration
# tests operate on the same input.
REPOSITORY_URL = "https://github.com/psf/requests"


@pytest.fixture(scope="module")
def ingested_documents():
    """
    Ingest the test repository once and reuse the resulting Documents.

    A pytest fixture is a reusable resource that can be requested
    by one or more tests.
    """
    # Create the object responsible for loading the GitHub repository.
    loader = GitHubRepositoryLoader(REPOSITORY_URL)

    # Execute the ingestion process and return the resulting Documents.
    #
    # The returned value becomes available to tests that request
    # the ``ingested_documents`` fixture.
    return loader.load()


def test_parse_repository_name():
    """
    Unit test:
        Test that a valid GitHub URL is correctly parsed.
    """

    # Define a valid GitHub repository URL to use as test input.
    repository_url = "https://github.com/owner/repository"

    # Create the loader using the test URL.
    # The constructor internally parses the URL and stores the
    # repository name.
    loader = GitHubRepositoryLoader(repository_url)

    # Assert:
    # Verify that the repository name was extracted correctly.
    assert loader.repository_name == "owner/repository"


def test_parse_repository_name_with_git_suffix():
    """
    Unit test:
        Test that the optional .git suffix is removed.

    GitHub repository URLs can optionally end with ``.git``.
    The loader should normalize both forms to the same repository name.
    """

    # Define a GitHub repository URL ending with .git.
    repository_url = "https://github.com/owner/repository.git"

    # Create the loader and let it parse the URL.
    loader = GitHubRepositoryLoader(repository_url)

    # Verify that the .git suffix was removed.
    assert loader.repository_name == "owner/repository"


@pytest.mark.parametrize(
    # Name of the argument that will receive each test value.
    "repository_url",

    # List of invalid URLs that should be rejected.
    [
        "https://gitlab.com/owner/repository",
        "https://github.com/owner",
        "https://github.com/owner/repository/extra",
        "https://github.com/",
    ],
)
def test_invalid_repository_url(repository_url):
    """
    Test that invalid repository URLs raise ValueError.

    ``pytest.mark.parametrize`` allows us to execute the same test
    multiple times with different input values.

    Instead of writing four separate test functions, pytest runs
    this function once for each URL in the list.

    The expected behavior is a ValueError because the URLs do not
    follow the format accepted by GitHubRepositoryLoader.
    """

    # ``pytest.raises`` verifies that the code inside the ``with``
    # block raises the expected exception.
    with pytest.raises(ValueError):
        GitHubRepositoryLoader(repository_url)


def test_repository_ingestion(ingested_documents):
    """
    Test that the repository is successfully ingested.

    The ``ingested_documents`` argument tells pytest that this test
    requires the fixture defined above.

    Pytest automatically executes the fixture and provides its
    returned value to the test.
    """

    # The loader should produce at least one Document.
    assert len(ingested_documents) > 0

    # Every returned object should be an instance of LangChain Document.
    assert all(
        isinstance(document, Document)
        for document in ingested_documents
    )


def test_documents_have_content(ingested_documents):
    """
    Test that ingested Documents contain file contents.
    """

    # Check that every Document contains non-empty content.
    assert all(
        document.page_content.strip()
        for document in ingested_documents
    )


def test_document_metadata(ingested_documents):
    """
    Test that ingested Documents contain the required metadata.
    """

    # Define the metadata fields that every Document is expected to have.
    required_metadata = {
        "repository",
        "file_path",
        "file_type",
        "source",
        "branch",
    }

    # Check every ingested Document individually.
    for document in ingested_documents:
        assert required_metadata.issubset(document.metadata.keys())


def test_supported_files_only(ingested_documents):
    """
    Test that only supported file types are ingested.
    """

    # Define the file extensions supported by the ingestion pipeline.
    #
    # This should correspond to the extensions defined in filters.py.
    allowed_extensions = {
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

    # Check every ingested Document.
    for document in ingested_documents:

        # Retrieve the file extension stored in the Document metadata.
        file_type = document.metadata["file_type"]

        # Verify that the extension belongs to the supported set.
        assert file_type in allowed_extensions


def test_source_urls(ingested_documents):
    """Test that every document contains a GitHub source URL."""

    for document in ingested_documents:
        source = document.metadata["source"]
        repository = document.metadata["repository"]

        assert source.startswith("https://github.com/")
        assert repository in source