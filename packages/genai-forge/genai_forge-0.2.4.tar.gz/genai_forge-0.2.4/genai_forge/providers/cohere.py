from __future__ import annotations

import os
from typing import Any, Optional

from dotenv import load_dotenv

from genai_forge.llm.base import BaseLLM
from genai_forge.llm.registry import register_llm
from prompting_forge.prompting import ChatPrompt


@register_llm("cohere")
class CohereChatLLM(BaseLLM):
	"""
	Cohere LLM provider.
	
	Supported models:
	- command-r-plus (Command R+)
	- command-r (Command R)
	- command (Command)
	- command-light (Command Light)
	
	Environment variables:
	- COHERE_API_KEY: Your Cohere API key
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
		self._temperature = float(temperature)
		self._logger = logger

	def __call__(self, prompt: Any) -> str:
		if isinstance(prompt, ChatPrompt):
			messages = prompt.to_messages()
			
			# Cohere uses a slightly different format
			cohere_messages = []
			for msg in messages:
				role = msg["role"]
				# Cohere uses "user", "assistant", "system"
				if role in ("user", "assistant", "system"):
					cohere_messages.append({
						"role": role,
						"content": msg["content"]
					})
		else:
			# Fallback: treat as plain user text
			content = self._normalize_prompt(prompt)
			cohere_messages = [{"role": "user", "content": content}]
		
		response = self._client.chat(
			model=self._model,
			messages=cohere_messages,
			temperature=self._temperature,
		)
		
		return response.message.content[0].text


