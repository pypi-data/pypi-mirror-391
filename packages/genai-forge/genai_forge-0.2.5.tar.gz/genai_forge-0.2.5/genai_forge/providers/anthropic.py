from __future__ import annotations

import os
from typing import Any, Optional

from dotenv import load_dotenv

from genai_forge.llm.base import BaseLLM
from genai_forge.llm.registry import register_llm
from prompting_forge.prompting import ChatPrompt


@register_llm("anthropic")
class AnthropicChatLLM(BaseLLM):
	"""
	Anthropic (Claude) LLM provider.
	
	Supported models:
	- claude-3-5-sonnet-20241022 (Claude 3.5 Sonnet)
	- claude-3-5-haiku-20241022 (Claude 3.5 Haiku)
	- claude-3-opus-20240229 (Claude 3 Opus)
	- claude-3-sonnet-20240229 (Claude 3 Sonnet)
	- claude-3-haiku-20240307 (Claude 3 Haiku)
	
	Environment variables:
	- ANTHROPIC_API_KEY: Your Anthropic API key
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
		key = api_key or os.getenv("ANTHROPIC_API_KEY")
		if not key:
			raise ValueError(
				"Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
				"or pass api_key parameter."
			)
		
		try:
			from anthropic import Anthropic
		except ImportError:
			raise ImportError(
				"anthropic package not installed. Install with: pip install anthropic"
			)
		
		self._client = Anthropic(api_key=key)
		self._model = model
		self._temperature = float(temperature)
		self._logger = logger

	def __call__(self, prompt: Any) -> str:
		if isinstance(prompt, ChatPrompt):
			messages = prompt.to_messages()
			# Anthropic requires separating system message
			system_msg = None
			user_messages = []
			
			for msg in messages:
				if msg["role"] == "system":
					system_msg = msg["content"]
				else:
					user_messages.append(msg)
			
			# Anthropic API call
			kwargs = {
				"model": self._model,
				"messages": user_messages,
				"temperature": self._temperature,
				"max_tokens": 4096,  # Reasonable default
			}
			if system_msg:
				kwargs["system"] = system_msg
			
			response = self._client.messages.create(**kwargs)
			return response.content[0].text
		else:
			# Fallback: treat as plain user text
			content = self._normalize_prompt(prompt)
			response = self._client.messages.create(
				model=self._model,
				messages=[{"role": "user", "content": content}],
				temperature=self._temperature,
				max_tokens=4096,
			)
			return response.content[0].text


