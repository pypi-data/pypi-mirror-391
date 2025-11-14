from __future__ import annotations

import os
from typing import Any, List, Optional, Union

from dotenv import load_dotenv
from openai import OpenAI

from genai_forge.embeddings.base import BaseEmbedding
from genai_forge.embeddings.registry import register_embedding


@register_embedding("openai")
class OpenAIEmbedding(BaseEmbedding):
	"""
	OpenAI Embedding provider.
	
	Supported models:
	- text-embedding-3-large (OpenAI Embeddings V3 Large, 3072 dimensions)
	- text-embedding-3-small (OpenAI Embeddings V3 Small, 1536 dimensions)
	- text-embedding-ada-002 (OpenAI Embeddings V2, 1536 dimensions)
	
	Environment variables:
	- OPENAI_API_KEY: Your OpenAI API key
	"""

	def __init__(
		self,
		*,
		model: str,
		api_key: Optional[str] = None,
		logger: Any = None,
	) -> None:
		load_dotenv()
		key = api_key or os.getenv("OPENAI_API_KEY")
		# Client can also read key from env automatically, but we pass it if present
		self._client = OpenAI(api_key=key) if key else OpenAI()
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
			input=texts,
		)
		
		embeddings = [item.embedding for item in response.data]
		
		if is_single:
			return embeddings[0]
		return embeddings

