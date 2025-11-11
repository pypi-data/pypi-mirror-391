from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from prompting_forge.prompting import PromptTemplate
from prompting_forge.versioning import save_prompt_version


class LLMCall:
	"""
	LLM executor that can optionally version prompts and synthesize a final prompt.
	- Prompt rendering is done via prompting-forge's PromptTemplate.
	- Prompt versioning and final prompt storage are delegated to prompting-forge.
	"""

	def __init__(self, name: str, client: Any, *, enable_versioning: bool = False, version_root: Path | None = None) -> None:
		self._name = name.strip()
		if not self._name:
			raise ValueError("LLMCall name cannot be empty")
		self._client = client
		self._enable_versioning = bool(enable_versioning)
		self._version_root = version_root

	def run(self, prompt_template: PromptTemplate, context: Dict[str, Any]) -> Tuple[str, str]:
		if not isinstance(context, dict):
			raise TypeError("context must be a dict")

		# If template requests a final prompt, delegate synthesis to template (prompting-forge)
		if getattr(prompt_template, "wants_final_prompt", None) and prompt_template.wants_final_prompt():
			# The template will handle reading history, calling the llm, and saving final prompt
			prompt_template.ensure_final_prompt(self._name, self._client, version_root=self._version_root)

		# Important: template must NOT embed parser format instructions.
		rendered = prompt_template.render(context, strict=True)

		if self._enable_versioning:
			save_prompt_version(self._name, rendered, root=self._version_root)

		response = self._execute(rendered)
		return rendered, response

	def _execute(self, rendered_text: str) -> str:
		client = self._client
		# Duck-typed call: callable client returns str
		result = client(rendered_text) if callable(client) else rendered_text
		return str(result)


