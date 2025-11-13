from __future__ import annotations

import os
from typing import Any, Optional

from dotenv import load_dotenv

from genai_forge.llm.base import BaseLLM
from genai_forge.llm.registry import register_llm
from prompting_forge.prompting import ChatPrompt


@register_llm("google")
class GoogleChatLLM(BaseLLM):
	"""
	Google (Gemini) LLM provider.
	
	Supported models:
	- gemini-2.0-flash-exp (Gemini 2.0 Flash Experimental)
	- gemini-1.5-pro (Gemini 1.5 Pro)
	- gemini-1.5-flash (Gemini 1.5 Flash)
	- gemini-1.5-flash-8b (Gemini 1.5 Flash-8B)
	
	Environment variables:
	- GOOGLE_API_KEY: Your Google API key
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
		self._temperature = float(temperature)
		self._logger = logger

	def __call__(self, prompt: Any) -> str:
		if isinstance(prompt, ChatPrompt):
			messages = prompt.to_messages()
			
			# Google uses a different message format
			# System message is handled separately
			system_instruction = None
			chat_messages = []
			
			for msg in messages:
				if msg["role"] == "system":
					system_instruction = msg["content"]
				elif msg["role"] == "user":
					chat_messages.append({"role": "user", "parts": [msg["content"]]})
				elif msg["role"] == "assistant":
					chat_messages.append({"role": "model", "parts": [msg["content"]]})
			
			# Create model with configuration
			generation_config = {
				"temperature": self._temperature,
				"max_output_tokens": 8192,
			}
			
			model_kwargs = {
				"model_name": self._model,
				"generation_config": generation_config,
			}
			if system_instruction:
				model_kwargs["system_instruction"] = system_instruction
			
			model = self._genai.GenerativeModel(**model_kwargs)
			
			# Generate response
			if len(chat_messages) == 1:
				# Single user message
				response = model.generate_content(chat_messages[0]["parts"][0])
			else:
				# Multi-turn conversation
				chat = model.start_chat(history=chat_messages[:-1])
				response = chat.send_message(chat_messages[-1]["parts"][0])
			
			return response.text
		else:
			# Fallback: treat as plain user text
			content = self._normalize_prompt(prompt)
			generation_config = {
				"temperature": self._temperature,
				"max_output_tokens": 8192,
			}
			model = self._genai.GenerativeModel(
				model_name=self._model,
				generation_config=generation_config,
			)
			response = model.generate_content(content)
			return response.text


