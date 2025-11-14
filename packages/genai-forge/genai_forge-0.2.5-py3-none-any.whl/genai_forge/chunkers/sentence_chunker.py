"""
Sentence-aware text chunker.

Splits text at sentence boundaries for better semantic coherence.
"""

import re
from typing import List

from .base import BaseChunker, Chunk
from .registry import register_chunker


@register_chunker("sentence")
class SentenceChunker(BaseChunker):
    """
    Sentence-aware chunker.
    
    Splits text into chunks that respect sentence boundaries, creating
    more semantically coherent chunks. Accumulates sentences until
    reaching the target chunk size.
    
    Args:
        chunk_size: Target character size per chunk (default: 1000)
        chunk_overlap: Number of characters to overlap (default: 200)
        respect_sentences: If True, never break mid-sentence (default: True)
    
    Examples:
        >>> chunker = SentenceChunker(chunk_size=500, chunk_overlap=100)
        >>> chunks = chunker.chunk("First sentence. Second sentence. Third...")
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        respect_sentences: bool = True,
    ):
        """Initialize sentence chunker."""
        super().__init__(chunk_size, chunk_overlap)
        self.respect_sentences = respect_sentences
        
        # Sentence boundary pattern (simple but effective)
        # Matches: . ! ? followed by space/newline/end
        self.sentence_pattern = re.compile(r'([.!?]+[\s\n]+|[.!?]+$)')

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
        
        Returns:
            List of sentences
        """
        # Split by sentence boundaries while keeping the punctuation
        parts = self.sentence_pattern.split(text)
        
        # Recombine sentence text with its punctuation
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            sentence = parts[i]
            if i + 1 < len(parts):
                sentence += parts[i + 1]
            sentences.append(sentence)
        
        # Handle last part if no delimiter at end
        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1])
        
        return [s for s in sentences if s.strip()]

    def chunk(self, text: str, **kwargs) -> List[Chunk]:
        """
        Split text into sentence-aware chunks.
        
        Args:
            text: The text to chunk
            **kwargs: Additional parameters (unused)
        
        Returns:
            List of Chunk objects
        """
        if not text:
            return []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        if not sentences:
            return []
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        # Track positions in original text
        position = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            # If adding this sentence would exceed chunk_size
            if current_size + sentence_len > self.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = "".join(current_chunk)
                chunk_start = position - current_size
                chunk_end = position
                
                chunk = self._create_chunk(
                    text=chunk_text,
                    start_index=chunk_start,
                    end_index=chunk_end,
                    chunk_index=chunk_index,
                    metadata={"sentence_count": len(current_chunk)},
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Handle overlap: keep last sentences that fit in overlap
                if self.chunk_overlap > 0:
                    overlap_size = 0
                    overlap_sentences = []
                    for sent in reversed(current_chunk):
                        if overlap_size + len(sent) <= self.chunk_overlap:
                            overlap_sentences.insert(0, sent)
                            overlap_size += len(sent)
                        else:
                            break
                    current_chunk = overlap_sentences
                    current_size = overlap_size
                else:
                    current_chunk = []
                    current_size = 0
            
            # Add current sentence
            current_chunk.append(sentence)
            current_size += sentence_len
            position += sentence_len
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = "".join(current_chunk)
            chunk_start = position - current_size
            chunk_end = position
            
            chunk = self._create_chunk(
                text=chunk_text,
                start_index=chunk_start,
                end_index=chunk_end,
                chunk_index=chunk_index,
                metadata={"sentence_count": len(current_chunk)},
            )
            chunks.append(chunk)
        
        return chunks

