# genai-forge Architecture

## Overview

`genai-forge` is a lightweight, provider-agnostic library for calling Large Language Models (LLMs) and parsing their structured outputs. It provides a unified interface for multiple LLM providers while maintaining flexibility and simplicity.

## Core Design Principles

1. **Provider Agnostic**: Support multiple LLM providers with a unified interface
2. **Simple & Composable**: Chain operations with the pipe (`|`) operator
3. **Type-Safe Parsing**: Validate LLM outputs with Pydantic models
4. **Minimal Dependencies**: Core library has minimal requirements; providers are optional
5. **Integration Ready**: Seamlessly integrates with `prompting-forge` for prompt management

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Application                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ uses
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      genai-forge Public API                      │
│  • get_llm(model, **kwargs) -> LLM                              │
│  • get_embedding(model, **kwargs) -> Embedding                  │
│  • PydanticOutputParser(model_class)                            │
│  • LLMCall(query, template, client)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┬──────────────┐
              │              │              │              │
              ▼              ▼              ▼              ▼
┌─────────────────┐  ┌───────────────┐  ┌─────────────┐  ┌──────────────┐
│  LLM Registry   │  │ Emb Registry  │  │   Parsing   │  │   LLM Call   │
│  • register_llm │  │ • register_   │  │  • Base     │  │  • Execute   │
│  • get_llm      │  │   embedding   │  │  • Pydantic │  │  • Version   │
└────────┬────────┘  │ • get_embed.  │  └─────────────┘  └──────────────┘
         │            └───────┬───────┘
         │
         │ dispatches to
         │
┌────────┴─────────────────────────────────────────────┐
│                  Provider Registry                    │
│  Maps provider names to implementation classes       │
└────────┬─────────────────────────────────────────────┘
         │
         │ instantiates
         │
    ┌────┴────┬────────┬────────┬────────┬────────┐
    ▼         ▼        ▼        ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
│ OpenAI │ │Anthropic│ │Google│ │Mistral │ │Cohere│
│Provider│ │Provider│ │Provider│ │Provider│ │Provider│
└────┬───┘ └────┬───┘ └───┬──┘ └────┬───┘ └───┬──┘
     │          │          │         │         │
     │ All implement BaseLLM: __call__(prompt) -> str
     │          │          │         │         │
     └──────────┴──────────┴─────────┴─────────┘
```

## Core Components

### 1. LLM Registry (`genai_forge.llm.registry`)

The registry is the heart of the provider system, enabling dynamic provider registration and instantiation.

**Key Functions:**
- `register_llm(provider: str)`: Decorator to register a provider class
- `get_llm(model: str, **kwargs)`: Factory function to instantiate LLMs

### 2. Embedding Registry (`genai_forge.embeddings.registry`)

Similar to the LLM registry, but for embedding models.

**Key Functions:**
- `register_embedding(provider: str)`: Decorator to register an embedding provider class
- `get_embedding(model: str, **kwargs)`: Factory function to instantiate embedding models

**Model String Format:**
```
provider:model_name
```

Examples:
- `"openai:gpt-4o-mini"`
- `"anthropic:claude-3-5-sonnet-20241022"`
- `"google:gemini-1.5-pro"`
- `"mistral:mistral-large-latest"`
- `"cohere:command-r-plus"`

If no provider is specified, defaults to OpenAI for backward compatibility.

### 3. Base LLM (`genai_forge.llm.base`)

**`BaseLLM` (Abstract Base Class):**
- Defines the contract all providers must implement
- Core method: `__call__(prompt: Any) -> str`
- Provides prompt normalization utilities
- Supports `ChatPrompt` objects from `prompting-forge`

**`LLM` (Protocol):**
- Runtime-checkable protocol for duck typing
- Any callable that takes a prompt and returns a string is a valid LLM

### 4. Base Embedding (`genai_forge.embeddings.base`)

**`BaseEmbedding` (Abstract Base Class):**
- Defines the contract all embedding providers must implement
- Core method: `__call__(text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]`
- Provides text normalization utilities

**`Embedding` (Protocol):**
- Runtime-checkable protocol for embedding models
- Any callable that takes text and returns vectors is a valid Embedding

### 5. LLM Providers (`genai_forge.providers`)

Each provider implements `BaseLLM` and registers itself using the `@register_llm` decorator.

#### Provider Implementations

**OpenAI Provider** (`openai.py`)
- Models: GPT-4, GPT-4o, GPT-4o-mini, GPT-3.5-turbo, etc.
- API Key: `OPENAI_API_KEY`
- Native support for chat completions

**Anthropic Provider** (`anthropic.py`)
- Models: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus, etc.
- API Key: `ANTHROPIC_API_KEY`
- Handles system messages separately (Anthropic API requirement)

**Google Provider** (`google.py`)
- Models: Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash, etc.
- API Key: `GOOGLE_API_KEY`
- Supports multi-turn conversations and system instructions

**Mistral Provider** (`mistral.py`)
- Models: Mistral Large, Mistral Medium, Mistral Small, Open Mixtral, etc.
- API Key: `MISTRAL_API_KEY`
- OpenAI-compatible chat completions API

**Cohere Provider** (`cohere.py`)
- Models: Command R+, Command R, Command, Command Light
- API Key: `COHERE_API_KEY`
- Uses Cohere's ClientV2 API

### 6. Embedding Providers (`genai_forge.embedding_providers`)

Each embedding provider implements `BaseEmbedding` and registers itself using the `@register_embedding` decorator.

**OpenAI Embeddings** (`openai_emb.py`)
- Models: text-embedding-3-large, text-embedding-3-small, text-embedding-ada-002
- Dimensions: 3072 (large), 1536 (small/ada)

**Google Embeddings** (`google_emb.py`)
- Models: text-embedding-004, embedding-001
- Dimensions: 768

**Mistral Embeddings** (`mistral_emb.py`)
- Models: mistral-embed
- Dimensions: 1024

**Cohere Embeddings** (`cohere_emb.py`)
- Models: embed-english-v3.0, embed-multilingual-v3.0, etc.
- Dimensions: 1024 (standard), 384 (light)

### 7. Output Parsing (`genai_forge.parsing`)

**`BaseOutputParser[TModel]`:**
- Generic parser for validating LLM outputs against Pydantic models
- Extracts JSON from various formats (raw, fenced code blocks, embedded text)
- Supports strict and non-strict validation modes

**`PydanticOutputParser[TModel]`:**
- Concrete implementation of `BaseOutputParser`
- Key methods:
  - `get_format_instructions() -> str`: Generates schema instructions for the LLM
  - `parse(text: str) -> TModel`: Validates and parses LLM output

**Error Handling:**
- `OutputParserException`: Raised when parsing or validation fails
- Tolerant parsing: handles markdown fences, extra text, etc.

### 8. LLM Call (`genai_forge.llm.llm_call`)

**`LLMCall`:**
Orchestrates prompt rendering, LLM execution, and optional versioning.

**Constructor Parameters:**
- `query`: User query string
- `prompt_template`: A `PromptTemplate` from `prompting-forge`
- `client`: An LLM instance (from `create_llm`)
- `output_parser`: Optional parser for structured outputs
- `name`: Instance name for versioning (default: "assistant1")
- `enable_versioning`: Whether to save call records (default: True)
- `version_root`: Root directory for versioning (default: current working directory)

**Execution Flow:**
1. Render prompt with context variables
2. Inject parser format instructions (if parser provided)
3. Execute LLM call
4. Optionally parse output
5. Save call record to `.llm_call/{name}/` (if versioning enabled)

**Call Record Format:**
```json
{
  "ts": "2025-11-12T15:00:00+00:00",
  "instance": "assistant1",
  "model": "gpt-4o-mini",
  "request": {
    "system": "System message",
    "template": "Template string",
    "rendered": "Fully rendered prompt",
    "query": "User query",
    "variables": {"key": "value"}
  },
  "response": {
    "text": "LLM response"
  },
  "prompt_ref": "path/to/prompt/version.json"
}
```

## Chaining with the Pipe Operator

`genai-forge` supports intuitive chaining using the `|` operator (via `prompting-forge`):

```python
chain = query | template | llm | parser
result = chain(context_variables)
```

**Chaining Flow:**
1. `query | template` → Function that renders prompt with context
2. `template | llm` → Function that renders and calls LLM
3. `llm | parser` → Function that calls LLM and parses output
4. `template | llm | parser` → Full pipeline with automatic format instruction injection

## Integration with prompting-forge

`genai-forge` is designed to work seamlessly with `prompting-forge`:

```
┌──────────────────────────────────────────────────────────────┐
│                     prompting-forge                           │
│  • PromptTemplate: Versioned prompt templates                │
│  • FinalPromptTemplate: LLM-synthesized prompts              │
│  • ChatPrompt: System + user message format                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ provides templates to
                         │
┌────────────────────────┴─────────────────────────────────────┐
│                     genai-forge                               │
│  • LLMCall: Executes templates with LLMs                     │
│  • create_llm: Creates LLM clients                           │
│  • Parsers: Validate LLM outputs                             │
└──────────────────────────────────────────────────────────────┘
```

**Key Integration Points:**
- `LLMCall` accepts `PromptTemplate` or `FinalPromptTemplate`
- `ChatPrompt` objects are natively supported by all LLM providers
- `FinalPromptTemplate` uses `LLMCall` internally for synthesis
- Embedding models work independently and can be used alongside LLMs

## File Structure

```
genai_forge/
├── __init__.py                    # Public API exports
├── llm/
│   ├── __init__.py               # LLM module exports
│   ├── base.py                   # BaseLLM, LLM protocol
│   ├── registry.py               # Provider registry & factory
│   └── llm_call.py               # LLMCall orchestrator
├── embeddings/
│   ├── __init__.py               # Embedding exports
│   ├── base.py                   # BaseEmbedding, Embedding protocol
│   └── registry.py               # Embedding registry & factory
├── parsing/
│   ├── __init__.py               # Parsing exports
│   └── output_parser.py          # BaseOutputParser, PydanticOutputParser
├── providers/
│   ├── __init__.py               # Import all LLM providers
│   ├── openai.py                 # OpenAI LLM provider
│   ├── anthropic.py              # Anthropic provider
│   ├── google.py                 # Google provider
│   ├── mistral.py                # Mistral provider
│   └── cohere.py                 # Cohere provider
└── embedding_providers/
    ├── __init__.py               # Import all embedding providers
    ├── openai_emb.py             # OpenAI embeddings
    ├── google_emb.py             # Google embeddings
    ├── mistral_emb.py            # Mistral embeddings
    └── cohere_emb.py             # Cohere embeddings
```

## Provider Registration Flow

1. **Import Time**: When `genai_forge` is imported, `providers/__init__.py` imports all provider modules
2. **Decoration**: Each provider class has `@register_llm("provider_name")` decorator
3. **Registration**: The decorator adds the provider class to `_LLM_REGISTRY` dict
4. **Factory**: `create_llm()` looks up the provider in the registry and instantiates it

## Environment Variables

Each provider requires an API key via environment variable:

```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
MISTRAL_API_KEY=...
COHERE_API_KEY=...
```

All providers use `python-dotenv` to automatically load `.env` files.

## Extensibility

### Adding a New Provider

1. Create `genai_forge/providers/new_provider.py`:

```python
from genai_forge.llm.base import BaseLLM
from genai_forge.llm.registry import register_llm

@register_llm("newprovider")
class NewProviderLLM(BaseLLM):
    def __init__(self, *, model: str, temperature: float = 0.3, 
                 api_key: str | None = None, logger: Any = None):
        # Initialize provider client
        self._client = ...
        self._model = model
        self._temperature = temperature
    
    def __call__(self, prompt: Any) -> str:
        # Handle ChatPrompt or plain text
        # Call provider API
        # Return response text
        return response_text
```

2. Import in `genai_forge/providers/__init__.py`:

```python
from . import new_provider  # noqa: F401
```

3. Add to `pyproject.toml` optional dependencies:

```toml
[project.optional-dependencies]
newprovider = ["newprovider-sdk>=1.0.0"]
```

4. Use it:

```python
llm = get_llm("newprovider:model-name")
```

### Adding a New Embedding Provider

Follow the same pattern in `genai_forge/embedding_providers/`:

```python
from genai_forge.embeddings.base import BaseEmbedding
from genai_forge.embeddings.registry import register_embedding

@register_embedding("newprovider")
class NewProviderEmbedding(BaseEmbedding):
    def __call__(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        # Implement embedding logic
        ...
```

## API Stability

**Stable APIs** (guaranteed backward compatibility):
- `get_llm(model: str, **kwargs) -> LLM`
- `get_embedding(model: str, **kwargs) -> Embedding`
- `LLMCall.__init__(...)`
- `LLMCall.run(context: Mapping) -> Tuple[str, Any]`
- `BaseLLM.__call__(prompt: Any) -> str`
- `BaseEmbedding.__call__(text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]`
- `PydanticOutputParser.__init__(model: Type[T])`
- `PydanticOutputParser.parse(text: str) -> T`

**Internal APIs** (may change):
- Provider implementation details
- Registry internals
- Parsing extraction logic

## Performance Considerations

- **Lazy Loading**: Providers are only imported when `genai_forge` is imported
- **Minimal Overhead**: Direct API calls, no unnecessary abstractions
- **Caching**: Version checking uses file system, no database overhead
- **Async Support**: Not yet implemented (future consideration)

## Security Considerations

1. **API Keys**: Never commit API keys; use environment variables
2. **Input Validation**: Context variables are validated against prompt templates
3. **Output Validation**: Pydantic models provide type-safe parsing
4. **File System**: Versioning records are saved locally; be mindful of sensitive data

## Testing Strategy

- **Unit Tests**: Test each provider independently with mocked APIs
- **Integration Tests**: Test with real API keys (CI/CD with secrets)
- **Contract Tests**: Ensure all providers return strings and handle `ChatPrompt`
- **Compatibility Tests**: Verify integration with `prompting-forge`

## Future Enhancements

Potential future features:
- **Async Support**: `async def __call__(...)` for concurrent requests
- **Streaming**: Token-by-token streaming responses
- **Caching**: Cache LLM responses to reduce API costs
- **Retries**: Automatic retry logic with exponential backoff
- **Rate Limiting**: Built-in rate limiting per provider
- **Observability**: Logging, tracing, and metrics
- **Batch Processing**: Process multiple prompts in a single API call
- **Function Calling**: Support for tool/function calling APIs
- **Vision Models**: Support for multimodal inputs

## Versioning

`genai-forge` follows semantic versioning:
- **Major**: Breaking API changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

Current version: `0.2.0` (added multi-provider support)

## License

See `LICENSE` file in the repository.


