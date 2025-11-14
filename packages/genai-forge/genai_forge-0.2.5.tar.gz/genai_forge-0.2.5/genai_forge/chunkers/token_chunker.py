"""
Token-based text chunker using tiktoken.

Splits text by token count, respecting LLM token limits.
"""

from typing import Any, List, Optional

from .base import BaseChunker, Chunk
from .registry import register_chunker


@register_chunker("token")
class TokenChunker(BaseChunker):
    """
    Token-based chunker using tiktoken.
    
    Splits text into chunks based on token count rather than characters.
    Useful for ensuring chunks respect LLM context window limits.
    
    Args:
        chunk_size: Target number of tokens per chunk (default: 512)
        chunk_overlap: Number of tokens to overlap between chunks (default: 50)
        encoding_name: tiktoken encoding name (default: "cl100k_base" for GPT-4)
    
    Examples:
        >>> chunker = TokenChunker(chunk_size=512, chunk_overlap=50)
        >>> chunks = chunker.chunk("Your long text here...")
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base",
    ):
        """Initialize token chunker with encoding."""
        super().__init__(chunk_size, chunk_overlap)
        self.encoding_name = encoding_name
        self._encoding: Optional[Any] = None
    
    @property
    def encoding(self):
        """Lazy load tiktoken encoding."""
        if self._encoding is None:
            try:
                import tiktoken
                self._encoding = tiktoken.get_encoding(self.encoding_name)
            except ImportError:
                raise ImportError(
                    "tiktoken is required for TokenChunker. "
                    "Install it with: pip install tiktoken"
                )
        return self._encoding

    def chunk(self, text: str, **kwargs) -> List[Chunk]:
        """
        Split text into token-based chunks.
        
        Args:
            text: The text to chunk
            **kwargs: Additional parameters (unused)
        
        Returns:
            List of Chunk objects
        """
        if not text:
            return []
        
        # Encode entire text into tokens
        tokens = self.encoding.encode(text)
        
        if not tokens:
            return []
        
        chunks = []
        start_token = 0
        chunk_index = 0
        char_position = 0  # Track character position incrementally
        
        while start_token < len(tokens):
            # Calculate end token for this chunk
            end_token = min(start_token + self.chunk_size, len(tokens))
            
            # Extract tokens for this chunk
            chunk_tokens = tokens[start_token:end_token]
            
            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Use incremental character position tracking
            char_start = char_position
            char_end = char_start + len(chunk_text)
            
            # Create chunk object
            chunk = self._create_chunk(
                text=chunk_text,
                start_index=char_start,
                end_index=char_end,
                chunk_index=chunk_index,
                metadata={"token_count": len(chunk_tokens)},
            )
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            # Ensure we always advance by at least 1 token to prevent infinite loops
            advance_tokens = max(1, self.chunk_size - self.chunk_overlap)
            
            # Update character position for next chunk
            # Decode the tokens we're actually advancing by
            if start_token + advance_tokens < len(tokens):
                advanced_text = self.encoding.decode(tokens[start_token:start_token + advance_tokens])
                char_position += len(advanced_text)
            
            start_token += advance_tokens
            chunk_index += 1
        
        return chunks

