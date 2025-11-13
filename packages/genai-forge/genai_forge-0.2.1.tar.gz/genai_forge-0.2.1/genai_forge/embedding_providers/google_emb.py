from __future__ import annotations

import os
from typing import Any, List, Optional, Union

from dotenv import load_dotenv

from genai_forge.embeddings.base import BaseEmbedding
from genai_forge.embeddings.registry import register_embedding


@register_embedding("google")
class GoogleEmbedding(BaseEmbedding):
	"""
	Google (Gemini) Embedding provider.
	
	Supported models:
	- text-embedding-004 (Latest text embeddings, 768 dimensions)
	- embedding-001 (Legacy embeddings, 768 dimensions)
	
	Environment variables:
	- GOOGLE_API_KEY: Your Google API key
	"""

	def __init__(
		self,
		*,
		model: str,
		api_key: Optional[str] = None,
		logger: Any = None,
	) -> None:
		load_dotenv()
		key = api_key or os.getenv("GOOGLE_API_KEY")
		if not key:
			raise ValueError(
				"Google API key not found. Set GOOGLE_API_KEY environment variable "
				"or pass api_key parameter."
			)
		
		try:
			import google.generativeai as genai
		except ImportError:
			raise ImportError(
				"google-generativeai package not installed. "
				"Install with: pip install google-generativeai"
			)
		
		genai.configure(api_key=key)
		self._genai = genai
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
		
		# Google's embed_content handles batches
		result = self._genai.embed_content(
			model=f"models/{self._model}",
			content=texts,
		)
		
		# Extract embeddings
		if is_single:
			return result['embedding']
		return result['embeddings']

