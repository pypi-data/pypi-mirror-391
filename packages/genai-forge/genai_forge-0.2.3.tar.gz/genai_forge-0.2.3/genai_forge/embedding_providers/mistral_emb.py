from __future__ import annotations

import os
from typing import Any, List, Optional, Union

from dotenv import load_dotenv

from genai_forge.embeddings.base import BaseEmbedding
from genai_forge.embeddings.registry import register_embedding


@register_embedding("mistral")
class MistralEmbedding(BaseEmbedding):
	"""
	Mistral AI Embedding provider.
	
	Supported models:
	- mistral-embed (Mistral Embeddings, 1024 dimensions)
	
	Environment variables:
	- MISTRAL_API_KEY: Your Mistral API key
	"""

	def __init__(
		self,
		*,
		model: str,
		api_key: Optional[str] = None,
		logger: Any = None,
	) -> None:
		load_dotenv()
		key = api_key or os.getenv("MISTRAL_API_KEY")
		if not key:
			raise ValueError(
				"Mistral API key not found. Set MISTRAL_API_KEY environment variable "
				"or pass api_key parameter."
			)
		
		try:
			from mistralai import Mistral
		except ImportError:
			raise ImportError(
				"mistralai package not installed. Install with: pip install mistralai"
			)
		
		self._client = Mistral(api_key=key)
		self._model = model
		self._logger = logger

	def __call__(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
		"""
		Embed text(s) into vector(s).
		
		Args:
			text: Single text string or list of text strings
		
		Returns:
			Single embedding vector if input is a string,
			or list of embedding vectors if input is a list of strings.
		"""
		is_single = isinstance(text, str)
		texts = [text] if is_single else text
		
		response = self._client.embeddings.create(
			model=self._model,
			inputs=texts,
		)
		
		embeddings = [item.embedding for item in response.data]
		
		if is_single:
			return embeddings[0]
		return embeddings

