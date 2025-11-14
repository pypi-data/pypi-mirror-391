from __future__ import annotations

"""
Common Chunker interfaces and base class.

Exposes:
  - Chunk: dataclass representing a text chunk with metadata
  - Chunker (Protocol): minimal callable interface for chunking
  - BaseChunker (ABC): enforces chunk() and provides common utilities
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol, runtime_checkable


@dataclass
class Chunk:
    """
    Represents a chunk of text with metadata.
    
    Attributes:
        text: The chunk text content
        start_index: Starting character position in original text
        end_index: Ending character position in original text
        chunk_index: Sequential index of this chunk
        metadata: Additional metadata (e.g., source file, page number)
    """
    text: str
    start_index: int
    end_index: int
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __len__(self) -> int:
        """Return the length of the chunk text."""
        return len(self.text)
    
    def __str__(self) -> str:
        """String representation of the chunk."""
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Chunk({self.chunk_index}: {preview})"


@runtime_checkable
class Chunker(Protocol):
    """Protocol for any Chunker interface."""

    def chunk(self, text: str, **kwargs) -> List[Chunk]:
        """
        Split text into chunks.
        
        Args:
            text: The text to chunk
            **kwargs: Additional chunker-specific parameters
        
        Returns:
            List of Chunk objects
        """
        ...


class BaseChunker(ABC):
    """
    Abstract base class for Chunkers.
    
    Responsibilities:
      - Require subclasses to implement `chunk(text) -> List[Chunk]`
      - Provide common utilities for text processing
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target size for each chunk
            chunk_overlap: Number of characters/tokens to overlap between chunks
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(self, text: str, **kwargs) -> List[Chunk]:
        """
        Split text into chunks.
        
        Args:
            text: The text to chunk
            **kwargs: Additional chunker-specific parameters
        
        Returns:
            List of Chunk objects
        """
        raise NotImplementedError

    def __call__(self, text: str, **kwargs) -> List[Chunk]:
        """Allow chunker to be called directly."""
        return self.chunk(text, **kwargs)

    @staticmethod
    def _create_chunk(
        text: str,
        start_index: int,
        end_index: int,
        chunk_index: int,
        metadata: Dict[str, Any] | None = None,
    ) -> Chunk:
        """
        Helper to create a Chunk object.
        
        Args:
            text: The chunk text
            start_index: Start position in original text
            end_index: End position in original text
            chunk_index: Sequential chunk number
            metadata: Optional metadata dict
        
        Returns:
            Chunk object
        """
        return Chunk(
            text=text,
            start_index=start_index,
            end_index=end_index,
            chunk_index=chunk_index,
            metadata=metadata or {},
        )

