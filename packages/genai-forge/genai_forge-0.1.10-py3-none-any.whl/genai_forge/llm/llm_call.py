from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Tuple

from prompting_forge.prompting import BasePromptTemplate
from prompting_forge.versioning import PromptRecord, save_prompt_record, based_on_versions, next_prompt_version


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

		# Normalize context once
		ctx = dict(context)

		# Build a ChatPrompt (captures system + user)
		chat = prompt_template(ctx)

		# Render final text (same content as chat.user since no instructions are injected here)
		rendered = chat.user

		response = self._execute(rendered)

		# Optional: save a rich JSON record after we have the response
		if self._enable_versioning:
			has_final = bool(getattr(prompt_template, "_final_template", None))
			template_str = getattr(prompt_template, "_final_template", None) or getattr(prompt_template, "_template", None)
			model = getattr(self._client, "_model", None)

			# Build PromptRecord fields
			ts = datetime.now(timezone.utc).isoformat()
			version_num = -1 if has_final and bool(getattr(prompt_template, "wants_final_prompt", None) and prompt_template.wants_final_prompt()) else next_prompt_version(self._name, root=self._version_root)
			record = PromptRecord(
				ts=ts,
				instance=self._name,
				version=version_num,
				system=chat.system,
				template=template_str or "",
				variables=ctx,
				user=chat.user,
				output_parser=None,
				llm_response=response,
				model=model,
				instructions_injected=False,
				has_final_template=has_final,
				notes=None,
				based_on_versions=based_on_versions(self._name, root=self._version_root),
			)
			save_prompt_record(self._name, record, root=self._version_root)

		return rendered, response

	def _execute(self, rendered_text: str) -> str:
		client = self._client
		# Duck-typed call: callable client returns str
		try:
			result = client(rendered_text) if callable(client) else rendered_text
		except Exception as e:
			return f"ERROR_CALLING_CLIENT: {e}"
		return str(result)


