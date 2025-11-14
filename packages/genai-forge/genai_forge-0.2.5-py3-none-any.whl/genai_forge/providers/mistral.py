from __future__ import annotations

import os
from typing import Any, Optional

from dotenv import load_dotenv

from genai_forge.llm.base import BaseLLM
from genai_forge.llm.registry import register_llm
from prompting_forge.prompting import ChatPrompt


@register_llm("mistral")
class MistralChatLLM(BaseLLM):
	"""
	Mistral AI LLM provider.
	
	Supported models:
	- mistral-large-latest (Mistral Large)
	- mistral-medium-latest (Mistral Medium)
	- mistral-small-latest (Mistral Small)
	- open-mistral-7b (Open Mistral 7B)
	- open-mixtral-8x7b (Open Mixtral 8x7B)
	- open-mixtral-8x22b (Open Mixtral 8x22B)
	
	Environment variables:
	- MISTRAL_API_KEY: Your Mistral API key
	"""

	def __init__(
		self,
		*,
		model: str,
		temperature: float = 0.3,
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
		self._temperature = float(temperature)
		self._logger = logger

	def __call__(self, prompt: Any) -> str:
		if isinstance(prompt, ChatPrompt):
			messages = prompt.to_messages()
		else:
			# Fallback: treat as plain user text
			content = self._normalize_prompt(prompt)
			messages = [{"role": "user", "content": content}]
		
		response = self._client.chat.complete(
			model=self._model,
			messages=messages,
			temperature=self._temperature,
		)
		
		return response.choices[0].message.content or ""


