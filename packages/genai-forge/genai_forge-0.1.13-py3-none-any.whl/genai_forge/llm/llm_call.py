from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Tuple

from prompting_forge.prompting import BasePromptTemplate
from prompting_forge.versioning import final_prompt_path, based_on_versions, save_prompt_version
import json


class LLMCall:
	"""
	LLM executor with optional prompt versioning.
	Responsibilities:
	  - Render prompts via prompting-forge templates
	  - Optionally persist LLM call artifacts under .llm_call/<instance>
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

		# If versioning is enabled and this is NOT a final prompt, save a prompt version JSON
		version_json_path: Path | None = None
		if self._enable_versioning:
			has_final_template = bool(getattr(prompt_template, "_final_template", None)) and prompt_template.wants_final_prompt()
			if not has_final_template:
				try:
					version_json_path = save_prompt_version(
						self._name,
						system=chat.system,
						user_text="",  # do not store rendered content here; content is saved in llm_call
						root=self._version_root,
						template=getattr(prompt_template, "_template", None) or "",
						variables=dict(ctx),
						output_parser=None,
						llm_response=None,
						model=None,
						instructions_injected=False,
						has_final=False,
						notes=None,
						based_on_versions=None,
					)
				except Exception:
					version_json_path = None

		response = self._execute(rendered)

		# Optional: save LLM call JSON record (separate from .prompt records)
		if self._enable_versioning:
			self._save_llm_call(prompt_template, chat.system, rendered, ctx, response, version_json_path)

		return rendered, response

	def _execute(self, rendered_text: str) -> str:
		client = self._client
		# Duck-typed call: callable client returns str
		try:
			result = client(rendered_text) if callable(client) else rendered_text
		except Exception as e:
			return f"ERROR_CALLING_CLIENT: {e}"
		return str(result)

	def _save_llm_call(
		self,
		prompt_template: BasePromptTemplate,
		system: str | None,
		rendered_user: str,
		variables: Mapping[str, Any],
		response_text: str,
		prompt_version_path: Path | None,
	) -> None:
		"""
		Save an LLM call record under .llm_call/<instance>/
		Includes a reference to the prompt version or final prompt JSON.
		"""
		# Save llm_call under the genai-forge workspace root
		call_root = Path(__file__).resolve().parents[2]
		target_dir = call_root / ".llm_call" / self._name
		target_dir.mkdir(parents=True, exist_ok=True)

		# Determine prompt reference
		has_final = bool(getattr(prompt_template, "_final_template", None)) and prompt_template.wants_final_prompt()
		prompt_ref_path = None
		prompt_ref_type = None
		version_paths: list[str] = []
		if prompt_version_path is not None:
			prompt_ref_path = str(prompt_version_path)
			prompt_ref_type = "version"
		elif has_final:
			prompt_ref_path = str(final_prompt_path(self._name, root=self._version_root))
			prompt_ref_type = "final"
			# Also include all version JSON paths used to build the final prompt
			try:
				vers = based_on_versions(self._name, root=self._version_root)
				version_paths = [
					str(((self._version_root if self._version_root is not None else Path.cwd()) / ".prompt" / self._name / f"{self._name}__prompt__v{v}.json"))
					for v in vers
				]
			except Exception:
				version_paths = []

		record = {
			"ts": datetime.now(timezone.utc).isoformat(),
			"instance": self._name,
			"model": getattr(self._client, "_model", None),
			"request": {
				"system": system,
				"template": getattr(prompt_template, "_final_template", None) or getattr(prompt_template, "_template", None),
				"rendered": rendered_user,
				"variables": dict(variables),
			},
			"response": {
				"text": response_text,
			},
			"prompt_ref": {
				"type": prompt_ref_type,
				"path": prompt_ref_path,
				"version_paths": version_paths if version_paths else None,
			},
			"final_template": bool(getattr(prompt_template, "_final_template", None)),
		}

		ts_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
		out_path = target_dir / f"{ts_name}.json"
		out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


