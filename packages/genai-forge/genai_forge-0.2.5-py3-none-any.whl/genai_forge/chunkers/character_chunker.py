"""
Character-based text chunker.

Splits text by character count with configurable overlap.
"""

from typing import List

from .base import BaseChunker, Chunk
from .registry import register_chunker


@register_chunker("character")
class CharacterChunker(BaseChunker):
    """
    Simple character-based chunker.
    
    Splits text into chunks of specified character length with overlap.
    Most basic chunking strategy, useful when you want precise control
    over chunk sizes.
    
    Examples:
        >>> chunker = CharacterChunker(chunk_size=100, chunk_overlap=20)
        >>> chunks = chunker.chunk("Your long text here...")
    """

    def chunk(self, text: str, **kwargs) -> List[Chunk]:
        """
        Split text into character-based chunks.
        
        Args:
            text: The text to chunk
            **kwargs: Additional parameters (unused for character chunker)
        
        Returns:
            List of Chunk objects
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position for this chunk
            end = min(start + self.chunk_size, len(text))
            
            # Extract chunk text
            chunk_text = text[start:end]
            
            # Create chunk object
            chunk = self._create_chunk(
                text=chunk_text,
                start_index=start,
                end_index=end,
                chunk_index=chunk_index,
            )
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            # Ensure we always advance by at least 1 character to prevent infinite loops
            advance = max(1, self.chunk_size - self.chunk_overlap)
            start += advance
            chunk_index += 1
        
        return chunks

