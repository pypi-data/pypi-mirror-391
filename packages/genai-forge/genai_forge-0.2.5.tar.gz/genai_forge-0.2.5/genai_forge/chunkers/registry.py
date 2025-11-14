from __future__ import annotations

"""
Chunker registry + factory.

Exposes:
  - register_chunker(name: str)
  - get_chunker(name: str, **kwargs)
"""

from typing import Any, Callable, Dict

from .base import Chunker

_CHUNKER_REGISTRY: Dict[str, Callable[..., Chunker]] = {}


def register_chunker(name: str) -> Callable[[Callable[..., Chunker]], Callable[..., Chunker]]:
    """
    Decorator to register a Chunker class or factory.
    
    Usage:
        @register_chunker("character")
        class CharacterChunker(BaseChunker):
            ...
    """
    name_norm = name.lower().strip()

    def _wrap(cls_or_factory: Callable[..., Chunker]) -> Callable[..., Chunker]:
        _CHUNKER_REGISTRY[name_norm] = cls_or_factory
        return cls_or_factory

    return _wrap


def get_chunker(name: str, **kwargs: Any) -> Chunker:
    """
    Factory to create a Chunker instance by name.
    
    Args:
        name: The chunker type (e.g., "character", "token", "sentence")
        **kwargs: Parameters passed to the chunker constructor
    
    Returns:
        An initialized Chunker instance
    
    Raises:
        ValueError: Unknown/unsupported chunker type
    
    Examples:
        >>> chunker = get_chunker("character", chunk_size=500, chunk_overlap=50)
        >>> chunks = chunker.chunk("Some long text...")
    """
    name_norm = name.lower().strip()
    factory = _CHUNKER_REGISTRY.get(name_norm)
    if factory is None:
        raise ValueError(
            f"Unknown chunker '{name_norm}'. Registered: {sorted(_CHUNKER_REGISTRY.keys())}"
        )
    return factory(**kwargs)

