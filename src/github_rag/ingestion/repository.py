"""
This module provides the GitHubRepositoryLoader class, which clones a
GitHub repository, filters its relevant files, reads their contents,
and converts them into LangChain Documents with source metadata.
"""
# Standard library
from pathlib import Path # Work with files and paths
import subprocess  # Run Git commands
import tempfile    # Create temporal repository
from urllib.parse import urlparse # Validate ULR Github

# LangChain Document structure 
from langchain_core.documents import Document

# Defined rules to discard files
from .filters import should_include_file


class GitHubRepositoryLoader:
    """
    Load relevant files from a GitHub repository
    and convert them into LangChain Documents.

    This class is responsible for the repository ingestion stage
    of the RAG pipeline. It clones a GitHub repository, filters
    its supported files, reads their contents, and converts them
    into LangChain Documents with source metadata.
    """

    def __init__(self, repository_url: str):
        """
        Initialize the repository loader.

        Args:
            repository_url: str
                URL of the GitHub repository to ingest.
        """
        # Store the original repository URL for the Git clone operation.
        self.repository_url = repository_url
        
        # Extract the repository identifier (owner/repository)
        # used to identify the repository and build source URLs.
        self.repository_name = self._parse_repository_name(repository_url)

    @staticmethod
    def _parse_repository_name(repository_url: str) -> str:
        """
        Validate a GitHub repository URL and extract its repository name,
        which can be used to identify the repository independently of its
        full URL.

        Args:
            repository_url: str
                Full URL of the GitHub repository.
                Expected format: https://github.com/owner/repository

        Returns:
            The repository name in ``owner/repository`` format.

        """
        # Parse the URL into its components (scheme, domain, path, etc.).
        parsed_url = urlparse(repository_url)

        # Make sure the URL belongs to GitHub.
        if parsed_url.netloc.lower() != "github.com":
            raise ValueError(
                "Invalid repository URL. "
                "The URL must point to github.com."
            )
        
        # Remove leading and trailing slashes from the repository path.
        path = parsed_url.path.strip("/")

        # A GitHub repository URL must contain exactly two components:
        # the repository owner and the repository name.
        parts = path.split("/")

        if len(parts) != 2:
            raise ValueError(
                "Invalid GitHub repository URL. "
                "Expected format: https://github.com/owner/repository"
            )

        # Separate the repository owner from the repository name.
        owner, repository = parts

        # Remove the optional .git suffix.
        if repository.endswith(".git"):
            repository = repository[:-4]

        # Make sure both the owner and repository name are not empty.
        if not owner or not repository:
            raise ValueError(
                "Invalid GitHub repository URL."
            )

        return f"{owner}/{repository}"


    def _clone_repository(self, destination: Path) -> None:
        """
        Clone the GitHub repository into the specified directory.

        Args:
            destination: Path object
                Local directory where the repository will be cloned.
        Returns:
            None.
        """

        # A shallow clone with depth 1 is used because the ingestion
        # pipeline only needs the files from the latest repository state,
        # not its complete Git history.
        command = [
            "git",
            "clone",
            "--depth",
            "1",
            self.repository_url,
            str(destination),
        ]

        # Execute Git as a system command.
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            # This occurs when the Git executable cannot be found.
            raise RuntimeError(
                "Git was not found. "
                "Make sure Git is installed and available in PATH."
            ) from exc

        except subprocess.CalledProcessError as exc:
            # Git is available, but the clone operation failed.
            error_message = exc.stderr.strip()
            raise RuntimeError(
                f"Failed to clone repository "
                f"'{self.repository_name}'.\n"
                f"Git error: {error_message}"
            ) from exc


    @staticmethod
    def _get_default_branch(repository_path: Path) -> str:
        """
        Get the branch currently checked out in the cloned repository.

        Args:
            repository_path: Path object
                Local path to the cloned Git repository.

        Returns:
            The name of the currently checked-out branch.
        """

        # Build the Git command used to obtain the current branch.
        # The -C option makes Git execute the command inside the
        # specified repository without changing the process working directory.
        command = [
            "git",
            "-C",
            str(repository_path),
            "branch",
            "--show-current",
        ]

        # Execute Git command
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            # Git is available, but the branch could not be determined.
            error_message = exc.stderr.strip()
            raise RuntimeError(
                "Unable to determine the repository's default branch.\n"
                f"Git error: {error_message}"
            ) from exc

        # Remove whitespace and the trailing newline from Git's output.
        branch = result.stdout.strip()

        # Make sure Git actually returned a branch name.
        if not branch:
            raise RuntimeError(
                "Unable to determine the repository's default branch."
            )

        return branch


    def _create_source_url(
        self,
        branch: str,
        file_path: Path,
    ) -> str:
        """
        Build the public GitHub URL for a repository file.

        The generated URL is stored in the Document metadata so that
        retrieved chunks can be linked back to their original source
        file on GitHub.

        Args:
            branch: str
                Name of the repository branch containing the file.
            file_path: str
                Path to the file relative to the repository root.

        Returns:
            A public GitHub URL pointing to the specified file.

        """
        return (
            f"https://github.com/{self.repository_name}"
            f"/blob/{branch}/{file_path.as_posix()}"
        )


    def load(self) -> list[Document]:
        """
        Clone the GitHub repository and convert its supported files
        into LangChain Documents.

        The repository is cloned into a temporary directory. Each file
        is then filtered according to the supported file types and
        ignored directories defined in ``filters.py``. The contents of
        valid files are read and converted into Documents together with
        metadata identifying their original location and source URL.

        Returns:
            A list of LangChain Documents, one for each supported file
            successfully read from the repository.
        """

        # Store the Documents created from the repository files.
        documents: list[Document] = []

        # Create a temporary directory that is automatically
        # removed when the loading process finishes.
        with tempfile.TemporaryDirectory() as temp_dir:

            # Define the local path where the repository will be cloned.
            repository_path = Path(temp_dir) / "repository"

            # Clone the GitHub repository.
            self._clone_repository(repository_path)

            # Get the actual branch checked out by Git.
            branch = self._get_default_branch(repository_path)

            # Recursively iterate over every file and directory
            # contained in the cloned repository.
            for file_path in repository_path.rglob("*"):

                # Skip directories and process files only.
                if not file_path.is_file():
                    continue

                # Convert the absolute file path into a path relative
                # to the repository root. This path will be used both
                # for filtering and for the Document metadata.
                relative_path = file_path.relative_to(repository_path)

                # Ignore files that are not relevant to the RAG,
                # according to the rules defined in filters.py.
                if not should_include_file(str(relative_path)):
                    continue

                # Read the file as UTF-8 text so that its contents
                # can be stored in the Document.
                try:
                    content = file_path.read_text(
                        encoding="utf-8"
                    )

                except UnicodeDecodeError:
                    # Skip files whose contents cannot be decoded as UTF-8.
                    continue

                except OSError:
                    # Skip files that cannot be accessed or read.
                    continue

                if not content.strip():
                    # Skip files that are empty
                    continue

                # Build a direct link to the original file on GitHub.
                source_url = self._create_source_url(
                    branch=branch,
                    file_path=relative_path,
                )

                # Convert the file into a LangChain Document.
                # The metadata allows the RAG pipeline to identify
                # and cite the original source of each document.
                document = Document(
                    page_content=content,
                    metadata={
                        "repository": self.repository_name,
                        "file_path": relative_path.as_posix(),
                        "file_type": file_path.suffix.lower(),
                        "source": source_url,
                        "branch": branch,
                    },
                )
                documents.append(document)

        return documents