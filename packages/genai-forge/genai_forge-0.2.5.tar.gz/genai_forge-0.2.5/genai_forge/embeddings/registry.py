from __future__ import annotations

"""
Embedding provider registry + factory.
Exposes:
  - register_embedding(provider: str)
  - get_embedding(model: str, **kwargs)
"""

from typing import Any, Callable, Dict, Optional, Tuple

from .base import Embedding
from dotenv import load_dotenv

_EMBEDDING_REGISTRY: Dict[str, Callable[..., Embedding]] = {}


def register_embedding(provider: str) -> Callable[[Callable[..., Embedding]], Callable[..., Embedding]]:
	"""
	Decorator to register an Embedding provider class or factory.
	Usage:
		@register_embedding("openai")
		class OpenAIEmbedding(BaseEmbedding):
			...
	"""
	prov = provider.lower().strip()

	def _wrap(cls_or_factory: Callable[..., Embedding]) -> Callable[..., Embedding]:
		_EMBEDDING_REGISTRY[prov] = cls_or_factory
		return cls_or_factory

	return _wrap


def get_embedding(
	model: str,
	*,
	api_key: Optional[str] = None,
	provider: Optional[str] = None,
	logger: Any = None,
) -> Embedding:
	"""
	Factory to create an Embedding instance from a model string.
	Args:
		model: Either "provider:model_id" (e.g., "openai:text-embedding-3-small")
			   or just "model_id" (provider inferred/overridden by `provider`).
		api_key: Optional explicit key override.
		provider: Optional explicit provider if not in `model`.
		logger: Optional logger.
	Returns:
		An initialized Embedding instance.
	Raises:
		ValueError: Unknown/unsupported provider.
	"""
	# Ensure environment variables from .env are available for any provider
	load_dotenv()

	prov, model_id = _split_provider_model(model, provider)
	prov_norm = prov.lower().strip()
	factory = _EMBEDDING_REGISTRY.get(prov_norm)
	if factory is None:
		raise ValueError(
			f"Unknown Embedding provider '{prov_norm}'. Registered: {sorted(_EMBEDDING_REGISTRY.keys())}"
		)
	return factory(model=model_id, api_key=api_key, logger=logger)


def _split_provider_model(model: str, provider: Optional[str]) -> Tuple[str, str]:
	"""
	Split a model string into (provider, model_id).
	Examples:
		"openai:text-embedding-3-small" -> ("openai", "text-embedding-3-small")
		"text-embedding-3-small" + provider="openai" -> ("openai", "text-embedding-3-small")
		"text-embedding-3-small" (no provider) -> defaults to ("openai", "text-embedding-3-small")
	"""
	if ":" in model:
		p, _, m = model.partition(":")
		return p, m
	if provider:
		return provider, model
	# default provider for bare model strings
	return "openai", model

