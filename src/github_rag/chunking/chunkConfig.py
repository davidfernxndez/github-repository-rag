"""
Default configuration for document chunking.

This module centralizes the default chunk size and overlap used by
the different chunking strategies.
"""

# Maximum number of characters in each chunk.
DEFAULT_CHUNK_SIZE = 1000

# Number of characters shared between consecutive chunks.
DEFAULT_CHUNK_OVERLAP = 200