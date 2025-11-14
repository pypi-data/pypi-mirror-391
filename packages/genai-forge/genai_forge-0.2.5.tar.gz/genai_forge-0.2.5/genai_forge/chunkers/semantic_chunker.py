"""
Semantic text chunker using embeddings.

Creates chunks based on semantic similarity rather than fixed sizes.
"""

from typing import List, Optional

from .base import BaseChunker, Chunk
from .registry import register_chunker
from ..embeddings.base import Embedding


@register_chunker("semantic")
class SemanticChunker(BaseChunker):
    """
    Semantic chunker using embeddings.
    
    Groups sentences into chunks based on semantic similarity.
    Uses embeddings to determine when topic shifts occur and creates
    new chunks at those boundaries.
    
    Args:
        embedding: Embedding model to use for computing similarities
        chunk_size: Soft target for chunk size in characters (default: 1000)
        similarity_threshold: Cosine similarity threshold for splitting (default: 0.7)
        min_chunk_size: Minimum chunk size in characters (default: 100)
    
    Examples:
        >>> from genai_forge import get_embedding
        >>> embedding = get_embedding("openai:text-embedding-3-small")
        >>> chunker = SemanticChunker(embedding=embedding, similarity_threshold=0.75)
        >>> chunks = chunker.chunk("Your text with multiple topics...")
    """

    def __init__(
        self,
        embedding: Embedding,
        chunk_size: int = 1000,
        similarity_threshold: float = 0.7,
        min_chunk_size: int = 100,
    ):
        """Initialize semantic chunker."""
        # For semantic chunker, overlap is determined by similarity
        super().__init__(chunk_size=chunk_size, chunk_overlap=0)
        self.embedding = embedding
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Cosine similarity score (0 to 1)
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)

    def _split_sentences(self, text: str) -> List[str]:
        """
        Simple sentence splitter.
        
        Args:
            text: Text to split
        
        Returns:
            List of sentences
        """
        import re
        pattern = re.compile(r'([.!?]+[\s\n]+|[.!?]+$)')
        parts = pattern.split(text)
        
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            sentence = parts[i]
            if i + 1 < len(parts):
                sentence += parts[i + 1]
            sentences.append(sentence.strip())
        
        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1].strip())
        
        return [s for s in sentences if s]

    def chunk(self, text: str, **kwargs) -> List[Chunk]:
        """
        Split text into semantically coherent chunks.
        
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
        
        # If only one sentence, return it as a single chunk
        if len(sentences) == 1:
            return [
                self._create_chunk(
                    text=text,
                    start_index=0,
                    end_index=len(text),
                    chunk_index=0,
                    metadata={"sentence_count": 1, "semantic_score": 1.0},
                )
            ]
        
        # Compute embeddings for all sentences
        sentence_embeddings = self.embedding(sentences)
        if isinstance(sentence_embeddings[0], float):
            # Single sentence case
            sentence_embeddings = [sentence_embeddings]
        
        # Group sentences into chunks based on similarity
        chunks = []
        current_chunk_sentences = [sentences[0]]
        current_chunk_size = len(sentences[0])
        chunk_index = 0
        position = 0
        chunk_start = 0
        
        for i in range(1, len(sentences)):
            # Calculate similarity with previous sentence
            similarity = self._cosine_similarity(
                sentence_embeddings[i - 1],
                sentence_embeddings[i]
            )
            
            # Check if we should start a new chunk
            should_split = (
                # Low similarity indicates topic shift
                (similarity < self.similarity_threshold) or
                # Chunk is getting too large
                (current_chunk_size + len(sentences[i]) > self.chunk_size)
            )
            
            # Don't split if current chunk is too small (unless similarity is very low)
            if current_chunk_size < self.min_chunk_size and similarity > 0.5:
                should_split = False
            
            if should_split and current_chunk_sentences:
                # Create chunk from accumulated sentences
                chunk_text = " ".join(current_chunk_sentences)
                
                chunk = self._create_chunk(
                    text=chunk_text,
                    start_index=chunk_start,
                    end_index=position,
                    chunk_index=chunk_index,
                    metadata={
                        "sentence_count": len(current_chunk_sentences),
                        "avg_similarity": similarity,
                    },
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk
                current_chunk_sentences = []
                current_chunk_size = 0
                chunk_start = position
            
            # Add current sentence
            current_chunk_sentences.append(sentences[i])
            current_chunk_size += len(sentences[i]) + 1  # +1 for space
            position += len(sentences[i]) + 1
        
        # Don't forget the last chunk
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            
            chunk = self._create_chunk(
                text=chunk_text,
                start_index=chunk_start,
                end_index=position,
                chunk_index=chunk_index,
                metadata={
                    "sentence_count": len(current_chunk_sentences),
                },
            )
            chunks.append(chunk)
        
        return chunks

