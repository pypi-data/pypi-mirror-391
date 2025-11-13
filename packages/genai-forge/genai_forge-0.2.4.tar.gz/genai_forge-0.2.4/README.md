# genai-forge

Lightweight, provider-agnostic utilities to call LLMs and parse their outputs with Pydantic. Build once, run on any LLM provider.

## Features

- 🔄 **Multi-Provider Support**: OpenAI, Anthropic (Claude), Google (Gemini), Mistral AI, Cohere
- 🔗 **Composable Chains**: Pipe operators for elegant prompt → LLM → parser workflows
- ✅ **Type-Safe Parsing**: Validate LLM outputs with Pydantic models
- 📦 **Minimal Core**: Only install what you need with optional provider dependencies
- 🔧 **Integration Ready**: Seamless integration with `prompting-forge` for prompt versioning

## Installation

### Basic Installation (OpenAI only)

```bash
pip install genai-forge
```

### With Specific Providers

```bash
# Anthropic (Claude)
pip install genai-forge[anthropic]

# Google (Gemini)
pip install genai-forge[google]

# Mistral AI
pip install genai-forge[mistral]

# Cohere
pip install genai-forge[cohere]

# All providers
pip install genai-forge[all]
```

## Requirements

- Python 3.10+
- API keys for your chosen provider(s)

## Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in your project root:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Google (Gemini)
GOOGLE_API_KEY=AIza...

# Mistral AI
MISTRAL_API_KEY=...

# Cohere
COHERE_API_KEY=...
```

`genai-forge` automatically loads `.env` files via `python-dotenv`.

### 2. Basic Usage

```python
from genai_forge import get_llm
from prompting_forge.prompting import PromptTemplate

# Create a prompt template
template = PromptTemplate(
    system="You are a concise expert assistant.",
    template="Generate one actionable tip.\nAudience: {audience}\nTime: {time}",
)

# Create an LLM (choose your provider)
llm = get_llm("openai:gpt-4o-mini", temperature=0.2)

# Chain: query | template | llm
query = "Provide a short productivity tip."
chain = query | template | llm
result = chain({"audience": "Backend Python developer", "time": "30 minutes"})
print(result)
```

## Supported Providers & Models

### OpenAI

```python
# GPT-4o models
llm = get_llm("openai:gpt-4o", temperature=0.3)
llm = get_llm("openai:gpt-4o-mini", temperature=0.3)

# GPT-4 models
llm = get_llm("openai:gpt-4-turbo", temperature=0.3)
llm = get_llm("openai:gpt-4", temperature=0.3)

# GPT-3.5 models
llm = get_llm("openai:gpt-3.5-turbo", temperature=0.3)
```

**Environment Variable**: `OPENAI_API_KEY`

### Anthropic (Claude)

```python
# Claude 3.5 models
llm = get_llm("anthropic:claude-3-5-sonnet-20241022", temperature=0.3)
llm = get_llm("anthropic:claude-3-5-haiku-20241022", temperature=0.3)

# Claude 3 models
llm = get_llm("anthropic:claude-3-opus-20240229", temperature=0.3)
llm = get_llm("anthropic:claude-3-sonnet-20240229", temperature=0.3)
llm = get_llm("anthropic:claude-3-haiku-20240307", temperature=0.3)
```

**Environment Variable**: `ANTHROPIC_API_KEY`

### Google (Gemini)

```python
# Gemini 2.0 models
llm = get_llm("google:gemini-2.0-flash-exp", temperature=0.3)

# Gemini 1.5 models
llm = get_llm("google:gemini-1.5-pro", temperature=0.3)
llm = get_llm("google:gemini-1.5-flash", temperature=0.3)
llm = get_llm("google:gemini-1.5-flash-8b", temperature=0.3)
```

**Environment Variable**: `GOOGLE_API_KEY`

### Mistral AI

```python
# Mistral models
llm = get_llm("mistral:mistral-large-latest", temperature=0.3)
llm = get_llm("mistral:mistral-medium-latest", temperature=0.3)
llm = get_llm("mistral:mistral-small-latest", temperature=0.3)

# Open models
llm = get_llm("mistral:open-mistral-7b", temperature=0.3)
llm = get_llm("mistral:open-mixtral-8x7b", temperature=0.3)
llm = get_llm("mistral:open-mixtral-8x22b", temperature=0.3)
```

**Environment Variable**: `MISTRAL_API_KEY`

### Cohere

```python
# Command R models
llm = get_llm("cohere:command-r-plus", temperature=0.3)
llm = get_llm("cohere:command-r", temperature=0.3)

# Command models
llm = get_llm("cohere:command", temperature=0.3)
llm = get_llm("cohere:command-light", temperature=0.3)
```

**Environment Variable**: `COHERE_API_KEY`

## Parsing Structured Outputs with Pydantic

Use `PydanticOutputParser` to have the LLM return valid JSON validated into a Pydantic model. Format instructions are automatically injected into your prompt.

```python
from typing import List
from pydantic import BaseModel
from genai_forge import get_llm, PydanticOutputParser
from prompting_forge.prompting import PromptTemplate

class CityPlan(BaseModel):
    city: str
    attractions: List[str]
    days: int

template = PromptTemplate(
    system="You are a helpful travel planner.",
    template="Create a city plan.\nCity: {city}\nDays: {days}",
)

# Use any provider you want
llm = get_llm("anthropic:claude-3-5-haiku-20241022", temperature=0.1)
parser = PydanticOutputParser(CityPlan)

# Chain: query | template | llm | parser
query = "Create a 3-day city plan for Tokyo."
chain = query | template | llm | parser
result = chain({"city": "Tokyo", "days": 3})  # -> CityPlan instance
print(f"City: {result.city}")
print(f"Days: {result.days}")
print(f"Attractions: {', '.join(result.attractions)}")
```

### How Parsing Works

`PydanticOutputParser`:
- Accepts tolerant output formats (e.g., extra text or ```json fences)
- Extracts JSON from the LLM response
- Validates against your Pydantic model
- Automatically injects format instructions when used in a chain

API surface:

```python
from genai_forge import PydanticOutputParser, BaseOutputParser, OutputParserException

parser = PydanticOutputParser(YourModel)
instructions = parser.get_format_instructions()  # JSON schema for the LLM
validated_obj = parser.parse(llm_output_text)    # Parsed & validated model
```

## Chaining with the Pipe Operator

The `|` operator builds elegant pipelines:

```python
# Simple chain
chain = template | llm

# With parser
chain = template | llm | parser

# With query
chain = query | template | llm | parser

# Execute
result = chain(context_variables)
```

**What happens:**
1. `query` + `template` → renders prompt with context variables
2. `llm` → sends prompt to LLM provider
3. `parser` → validates and parses response (format instructions auto-injected)

## Embedding Models

`genai-forge` also supports embedding models for generating vector representations of text.

### Basic Embedding Usage

```python
from genai_forge import get_embedding

# Create an embedding model
embedding = get_embedding("openai:text-embedding-3-small")

# Embed a single text
vector = embedding("Hello, world!")
print(f"Embedding dimension: {len(vector)}")

# Embed multiple texts
texts = ["First document", "Second document", "Third document"]
vectors = embedding(texts)
print(f"Number of vectors: {len(vectors)}")
```

### Supported Embedding Models

#### OpenAI

```python
# Latest V3 models
emb = get_embedding("openai:text-embedding-3-large")  # 3072 dimensions
emb = get_embedding("openai:text-embedding-3-small")  # 1536 dimensions

# Legacy V2 model
emb = get_embedding("openai:text-embedding-ada-002")  # 1536 dimensions
```

**Environment Variable**: `OPENAI_API_KEY`

#### Google (Gemini)

```python
emb = get_embedding("google:text-embedding-004")  # 768 dimensions
emb = get_embedding("google:embedding-001")       # 768 dimensions (legacy)
```

**Environment Variable**: `GOOGLE_API_KEY`

#### Mistral AI

```python
emb = get_embedding("mistral:mistral-embed")  # 1024 dimensions
```

**Environment Variable**: `MISTRAL_API_KEY`

#### Cohere

```python
# Standard models
emb = get_embedding("cohere:embed-english-v3.0")       # 1024 dimensions
emb = get_embedding("cohere:embed-multilingual-v3.0")  # 1024 dimensions

# Lightweight models
emb = get_embedding("cohere:embed-english-light-v3.0")       # 384 dimensions
emb = get_embedding("cohere:embed-multilingual-light-v3.0")  # 384 dimensions
```

**Environment Variable**: `COHERE_API_KEY`

### Embedding Use Cases

#### Semantic Search

```python
from genai_forge import get_embedding
import numpy as np

# Initialize embedding model
embedding = get_embedding("openai:text-embedding-3-small")

# Documents to search
documents = [
    "Python is a programming language",
    "Machine learning uses algorithms",
    "Natural language processing analyzes text",
]

# Embed documents
doc_vectors = embedding(documents)

# Query
query = "What is NLP?"
query_vector = embedding(query)

# Compute cosine similarities
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

similarities = [cosine_similarity(query_vector, doc) for doc in doc_vectors]

# Find most similar document
best_idx = np.argmax(similarities)
print(f"Most relevant: {documents[best_idx]}")
print(f"Similarity: {similarities[best_idx]:.4f}")
```

#### Document Clustering

```python
from genai_forge import get_embedding
from sklearn.cluster import KMeans

embedding = get_embedding("openai:text-embedding-3-small")

docs = [
    "Python programming tutorial",
    "Java development guide",
    "Cooking recipes for beginners",
    "Advanced Python techniques",
    "Italian cuisine recipes",
]

# Get embeddings
vectors = embedding(docs)

# Cluster
kmeans = KMeans(n_clusters=2, random_state=0)
labels = kmeans.fit_predict(vectors)

for doc, label in zip(docs, labels):
    print(f"Cluster {label}: {doc}")
```

## Multi-Provider Comparison Example

Compare outputs from different providers on the same prompt:

```python
from genai_forge import get_llm
from prompting_forge.prompting import PromptTemplate

template = PromptTemplate(
    system="You are a creative writer.",
    template="Write a haiku about {topic}.",
)

providers = [
    "openai:gpt-4o-mini",
    "anthropic:claude-3-5-haiku-20241022",
    "google:gemini-1.5-flash",
    "mistral:mistral-small-latest",
    "cohere:command-light",
]

context = {"topic": "artificial intelligence"}

for provider_model in providers:
    try:
        llm = get_llm(provider_model, temperature=0.7)
        chain = template | llm
        result = chain(context)
        print(f"\n{provider_model}:")
        print(result)
    except Exception as e:
        print(f"\n{provider_model}: ERROR - {e}")
```

## Advanced Usage: LLMCall with Versioning

`LLMCall` provides advanced features like prompt versioning and call logging:

```python
from genai_forge import get_llm
from genai_forge.llm import LLMCall
from prompting_forge.prompting import PromptTemplate

template = PromptTemplate(
    system="You are a helpful assistant.",
    template="Explain {concept} in simple terms.",
)

llm = get_llm("openai:gpt-4o-mini")

# Create an LLMCall with versioning
call = LLMCall(
    query="Explain the concept clearly",
    prompt_template=template,
    client=llm,
    name="explainer_assistant",
    enable_versioning=True,  # Saves call records to .llm_call/
)

# Execute
rendered_prompt, response = call.run({"concept": "quantum computing"})

print("Rendered:", rendered_prompt)
print("Response:", response)
```

Call records are saved to `.llm_call/{name}/{timestamp}.json` with full request/response details.

## Integration with prompting-forge

`genai-forge` works seamlessly with `prompting-forge` for prompt versioning and synthesis:

```python
from prompting_forge.prompting import PromptTemplate, FinalPromptTemplate
from genai_forge import get_llm
from genai_forge.llm import LLMCall

# Create versioned prompts
v1 = PromptTemplate(
    system="You are a helpful assistant.",
    template="Translate: {text}",
    instance_name="translator"
)

v2 = PromptTemplate(
    system="You are a professional translator.",
    template="Translate the following text to {language}:\n{text}",
    instance_name="translator"
)

# Synthesize final prompt from versions
llm = get_llm("openai:gpt-4o")
final = FinalPromptTemplate(
    instance_name="translator",
    variables=["text", "language"],
    llm_client=llm
)

# Use final prompt in production
call = LLMCall(
    query="Translate this text",
    prompt_template=final,
    client=llm,
    name="production_translator"
)

result = call.run({"text": "Hello, world!", "language": "Spanish"})
```

See the [prompting-forge documentation](https://github.com/ToolForge-AI/prompting-forge) for more details.

## Provider Configuration

### Default Provider

If you don't specify a provider, OpenAI is used by default:

```python
llm = get_llm("gpt-4o-mini")  # Same as "openai:gpt-4o-mini"
```

### Explicit Provider

Always recommended for clarity:

```python
llm = get_llm("openai:gpt-4o-mini")
llm = get_llm("anthropic:claude-3-5-sonnet-20241022")
```

### Override API Key

Pass the API key directly instead of using environment variables:

```python
llm = get_llm(
    "anthropic:claude-3-5-haiku-20241022",
    api_key="sk-ant-your-key-here",
    temperature=0.2
)
```

## Error Handling

```python
from genai_forge import get_llm, OutputParserException

try:
    llm = get_llm("unknown:model")
except ValueError as e:
    print(f"Unknown provider: {e}")

try:
    result = parser.parse(invalid_json)
except OutputParserException as e:
    print(f"Parsing failed: {e}")
```

## Running the Example

An `example.py` is included in the repository demonstrating:
- Multiple provider usage
- PromptTemplate with system prompts
- PydanticOutputParser for structured outputs
- Error handling

Ensure you have a `.env` with your API keys, then:

```bash
python example.py
```

## Project Structure

```
genai_forge/
├── __init__.py              # Public API
├── llm/                     # LLM core
│   ├── base.py             # BaseLLM, LLM protocol
│   ├── registry.py         # Provider registry & factory
│   └── llm_call.py         # LLMCall with versioning
├── parsing/                # Output parsers
│   └── output_parser.py   # PydanticOutputParser
└── providers/              # LLM providers
    ├── openai.py          # OpenAI
    ├── anthropic.py       # Anthropic (Claude)
    ├── google.py          # Google (Gemini)
    ├── mistral.py         # Mistral AI
    └── cohere.py          # Cohere
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

## API Reference

### Core Functions

**`get_llm(model: str, **kwargs) -> LLM`**
- `model`: Provider and model name (e.g., "openai:gpt-4o-mini")
- `temperature`: Sampling temperature (default: 0.3)
- `api_key`: Optional API key override
- `provider`: Optional explicit provider name
- `logger`: Optional logger instance
- Returns: LLM instance (callable)

**`get_embedding(model: str, **kwargs) -> Embedding`**
- `model`: Provider and model name (e.g., "openai:text-embedding-3-small")
- `api_key`: Optional API key override
- `provider`: Optional explicit provider name
- `logger`: Optional logger instance
- Returns: Embedding instance (callable that takes text and returns vectors)

**`PydanticOutputParser(model: Type[T], strict: bool = True)`**
- `model`: Pydantic model class
- `strict`: Whether to enforce strict validation
- Methods:
  - `get_format_instructions() -> str`
  - `parse(text: str) -> T`

**`LLMCall(query, prompt_template, client, **kwargs)`**
- `query`: User query string
- `prompt_template`: PromptTemplate instance
- `client`: LLM instance
- `output_parser`: Optional parser
- `name`: Instance name for versioning
- `enable_versioning`: Save call records
- `version_root`: Root directory for versioning
- Methods:
  - `run(context: dict) -> tuple[str, Any]`

## FAQ

### Can I use multiple providers in the same application?

Yes! Each `get_llm()` call creates an independent LLM instance:

```python
openai_llm = get_llm("openai:gpt-4o-mini")
claude_llm = get_llm("anthropic:claude-3-5-sonnet-20241022")
gemini_llm = get_llm("google:gemini-1.5-pro")
```

### Do I need all provider packages installed?

No. Only install the providers you need:

```bash
pip install genai-forge[anthropic,google]  # Only Anthropic and Google
```

### What if a provider API changes?

`genai-forge` abstracts provider differences. Update the library version, and your code should continue working.

### How do I add a custom provider?

See [ARCHITECTURE.md § Extensibility](ARCHITECTURE.md#extensibility) for a guide on implementing custom providers.

### Can I use this with async code?

Not yet. Async support is planned for a future release.

## Contributing

Contributions are welcome! Areas for improvement:
- Additional providers (Hugging Face, AI21, etc.)
- Async support
- Streaming responses
- Enhanced error handling
- More examples

## Changelog

### 0.2.0 (2025-11-12)
- ✨ Added multi-provider support: Anthropic, Google, Mistral, Cohere
- 📚 Comprehensive ARCHITECTURE.md documentation
- 🔧 Optional provider dependencies
- 📦 Improved package structure

### 0.1.17
- 🚀 Initial release with OpenAI support
- ✅ Pydantic output parsing
- 🔗 Chaining with pipe operator
- 📝 Prompt versioning with LLMCall

## License

See [LICENSE](LICENSE).

## Links

- **Repository**: [github.com/ToolForge-AI/genai-forge](https://github.com/ToolForge-AI/genai-forge)
- **Issues**: [github.com/ToolForge-AI/genai-forge/issues](https://github.com/ToolForge-AI/genai-forge/issues)
- **Related**: [prompting-forge](https://github.com/ToolForge-AI/prompting-forge) - Prompt versioning and synthesis
