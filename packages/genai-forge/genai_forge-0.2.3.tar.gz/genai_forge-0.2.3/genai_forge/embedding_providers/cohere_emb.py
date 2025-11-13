from __future__ import annotations

import os
from typing import Any, List, Optional, Union

from dotenv import load_dotenv

from genai_forge.embeddings.base import BaseEmbedding
from genai_forge.embeddings.registry import register_embedding


@register_embedding("cohere")
class CohereEmbedding(BaseEmbedding):
	"""
	Cohere Embedding provider.
	
	Supported models:
	- embed-english-v3.0 (English embeddings, 1024 dimensions)
	- embed-multilingual-v3.0 (Multilingual embeddings, 1024 dimensions)
	- embed-english-light-v3.0 (Lightweight English, 384 dimensions)
	- embed-multilingual-light-v3.0 (Lightweight Multilingual, 384 dimensions)
	
	Environment variables:
	- COHERE_API_KEY: Your Cohere API key
	"""

	def __init__(
		self,
		*,
		model: str,
		api_key: Optional[str] = None,
		logger: Any = None,
	) -> None:
		load_dotenv()
		key = api_key or os.getenv("COHERE_API_KEY")
		if not key:
			raise ValueError(
				"Cohere API key not found. Set COHERE_API_KEY environment variable "
				"or pass api_key parameter."
			)
		
		try:
			import cohere
		except ImportError:
			raise ImportError(
				"cohere package not installed. Install with: pip install cohere"
			)
		
		self._client = cohere.ClientV2(api_key=key)
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
		
		response = self._client.embed(
			model=self._model,
			texts=texts,
			input_type="search_document",  # or "search_query" depending on use case
			embedding_types=["float"],
		)
		
		embeddings = response.embeddings.float_
		
		if is_single:
			return embeddings[0]
		return embeddings

