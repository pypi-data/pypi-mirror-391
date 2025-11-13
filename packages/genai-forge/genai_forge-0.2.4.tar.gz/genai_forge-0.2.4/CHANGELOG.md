# Changelog

All notable changes to genai-forge will be documented in this file.

## [0.2.0] - 2025-11-12

### Breaking Changes
- **Renamed `create_llm` to `get_llm`**: The main factory function for creating LLM instances has been renamed for consistency with the new embedding API. Update all imports and calls from `create_llm` to `get_llm`.

### Added
- **Embedding Model Support**: New `get_embedding()` function for creating embedding model instances
  - OpenAI embeddings: `text-embedding-3-large`, `text-embedding-3-small`, `text-embedding-ada-002`
  - Google embeddings: `text-embedding-004`, `embedding-001`
  - Mistral embeddings: `mistral-embed`
  - Cohere embeddings: `embed-english-v3.0`, `embed-multilingual-v3.0`, light variants
- **Multi-Provider LLM Support**: Added providers for popular LLM services
  - Anthropic (Claude): Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus, and more
  - Google (Gemini): Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash
  - Mistral AI: Mistral Large, Medium, Small, and Open Mixtral models
  - Cohere: Command R+, Command R, Command, Command Light
- **Comprehensive Documentation**:
  - New `ARCHITECTURE.md` with detailed design documentation
  - Expanded `README.md` with examples for all providers
  - Added embedding usage examples (semantic search, clustering)
- **Enhanced Example**: Updated `example.py` with 5 comprehensive examples including embeddings

### Changed
- **API Naming**: `create_llm` → `get_llm` (breaking change)
- **Version**: Bumped from 0.1.17 to 0.2.0
- **Dependencies**: Made provider dependencies optional via `[anthropic]`, `[google]`, `[mistral]`, `[cohere]`, `[all]` extras
- **Project Structure**: Added `embeddings/` and `embedding_providers/` directories

### Infrastructure
- **New Modules**:
  - `genai_forge.embeddings.base`: Base classes for embedding models
  - `genai_forge.embeddings.registry`: Embedding provider registry
  - `genai_forge.embedding_providers.*`: Provider implementations
- **Registry Pattern**: Consistent `@register_llm` and `@register_embedding` decorators

### Migration Guide

#### For genai-forge users:

**Before (0.1.x):**
```python
from genai_forge import create_llm
llm = create_llm("openai:gpt-4o-mini")
```

**After (0.2.0):**
```python
from genai_forge import get_llm
llm = get_llm("openai:gpt-4o-mini")
```

#### For prompting-forge users:

prompting-forge has been updated to use `get_llm`. Update to `genai-forge>=0.2.0` in your dependencies.

### Notes
- All LLM functionality remains unchanged except for the function name
- OpenAI remains the default provider if none is specified
- Backward compatibility maintained for all provider implementations
- No changes to `LLMCall`, `PydanticOutputParser`, or other core APIs

## [0.1.17] - 2025-11-11

### Initial Release
- OpenAI LLM support
- Pydantic output parsing
- Chain composition with pipe operator (`|`)
- LLMCall with versioning
- Integration with prompting-forge

