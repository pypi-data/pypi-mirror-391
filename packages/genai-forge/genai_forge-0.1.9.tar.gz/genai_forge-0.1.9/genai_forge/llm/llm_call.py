from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Tuple

from prompting_forge.prompting import BasePromptTemplate
from prompting_forge.versioning import save_prompt_version


class LLMCall:
	"""
	LLM executor with optional prompt versioning.
	Responsibilities:
	  - Render prompts via prompting-forge templates
	  - Optionally persist versioned prompts (system + user) for traceability
	  - Execute the provided client
	"""

	def __init__(self, name: str, client: Any, *, enable_versioning: bool = False, version_root: Path | None = None) -> None:
		self._name = name.strip()
		if not self._name:
			raise ValueError("LLMCall name cannot be empty")
		self._client = client
		self._enable_versioning = bool(enable_versioning)
		self._version_root = version_root

	def run(self, prompt_template: BasePromptTemplate, context: Mapping[str, Any]) -> Tuple[str, str]:
		"""
		Render a prompt using the given template and context, optionally save a version,
		then execute the LLM client.

		Returns:
		  (rendered_text, response_text)
		"""
		if not isinstance(context, Mapping):
			raise TypeError("context must be a mapping of variable names to values")

		# Build a ChatPrompt for optional versioning (captures system + user)
		chat = prompt_template(dict(context))

		# Render final text (templates must not embed parser instructions)
		rendered = prompt_template.render(dict(context), strict=True)

		response = self._execute(rendered)

		# Optional: save a rich JSON record after we have the response
		if self._enable_versioning:
			template_str = getattr(prompt_template, "_final_template", None) or getattr(prompt_template, "_template", None)
			model = getattr(self._client, "_model", None)
			save_prompt_version(
				self._name,
				system=chat.system,
				user_text=chat.user,
				root=self._version_root,
				template=template_str,
				query=dict(context).get("query"),
				variables=dict(context),
				output_parser=None,
				llm_response=response,
				model=model,
				instructions_injected=False,
				has_final=bool(getattr(prompt_template, "_final_template", None)),
			)
		return rendered, response

	def _execute(self, rendered_text: str) -> str:
		client = self._client
		# Duck-typed call: callable client returns str
		try:
			result = client(rendered_text) if callable(client) else rendered_text
		except Exception as e:
			return f"ERROR_CALLING_CLIENT: {e}"
		return str(result)


