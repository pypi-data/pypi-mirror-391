from __future__ import annotations

"""
Common Embedding interfaces and base class.

Exposes:
  - Embedding (Protocol): minimal callable interface.
  - BaseEmbedding (ABC): enforces __call__ and provides common utilities.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Protocol, Union, runtime_checkable


@runtime_checkable
class Embedding(Protocol):
	"""Protocol for any Embedding model interface."""

	def __call__(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
		"""
		Embed text(s) into vector(s).
		
		Args:
			text: Single text string or list of text strings
		
		Returns:
			Single embedding vector (list of floats) if input is a string,
			or list of embedding vectors if input is a list of strings.
		"""
		...


class BaseEmbedding(ABC):
	"""
	Abstract base class for Embedding models.
	Responsibilities:
	  - Require subclasses to implement `__call__(text) -> embeddings`.
	  - Provide common utilities for text normalization.
	"""

	@abstractmethod
	def __call__(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
		"""
		Embed text(s) into vector(s).
		
		Args:
			text: Single text string or list of text strings
		
		Returns:
			Single embedding vector (list of floats) if input is a string,
			or list of embedding vectors if input is a list of strings.
		"""
		raise NotImplementedError

	@staticmethod
	def _normalize_text(text: Union[str, List[str]]) -> List[str]:
		"""
		Normalize text input to a list of strings.
		
		Args:
			text: Single text string or list of text strings
		
		Returns:
			List of text strings
		"""
		if isinstance(text, str):
			return [text]
		return list(text)

