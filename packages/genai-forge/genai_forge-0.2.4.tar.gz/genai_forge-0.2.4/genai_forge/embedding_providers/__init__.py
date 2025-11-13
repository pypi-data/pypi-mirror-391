from __future__ import annotations

# Import all embedding providers here to trigger their @register_embedding decorators
from . import openai_emb  # noqa: F401
from . import google_emb  # noqa: F401
from . import mistral_emb  # noqa: F401
from . import cohere_emb  # noqa: F401

from .openai_emb import OpenAIEmbedding
from .google_emb import GoogleEmbedding
from .mistral_emb import MistralEmbedding
from .cohere_emb import CohereEmbedding

__all__ = [
	"OpenAIEmbedding",
	"GoogleEmbedding",
	"MistralEmbedding",
	"CohereEmbedding",
]

