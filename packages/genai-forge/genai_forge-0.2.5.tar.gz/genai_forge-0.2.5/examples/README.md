# genai-forge Examples

Three concise examples demonstrating all major features of genai-forge with **elegant pipe operator syntax**.

## ✨ Pipe Operator Support

All examples showcase the beautiful pipe operator (`|`) for composable chains:

```python
# Simple chain
chain = template | llm
result = chain(context)

# With parser
chain = template | llm | parser  
result = chain(context)  # Returns typed Pydantic object!

# FULL CHAIN - The most elegant form!
query = "Suggest a healthy breakfast"
chain = query | template | llm | parser
result = chain()  # Query already embedded - no variables needed!
```

## Prerequisites

1. Install genai-forge with required extras:
```bash
pip install genai-forge[all]
```

2. Set up your `.env` file in the project root:
```bash
# Add at least one provider API key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

## Examples

### 1. LLM Chains with Multiple Providers
**File:** `example_llm_chains.py`

**Features demonstrated:**
- ✅ **Pipe operator:** `template | llm`
- Simple chain composition
- Using different LLM providers (OpenAI, Anthropic, Google)
- Integration with prompting-forge templates

**Run:**
```bash
python examples/example_llm_chains.py
```

**Example code:**
```python
template = PromptTemplate(
    system="You are a helpful AI assistant.",
    template="Tell me about {topic}."
)
llm = get_llm("openai:gpt-4o-mini")

# Elegant pipe operator!
chain = template | llm
result = chain({"topic": "quantum computing"})
```

### 2. RAG Pipeline with Document Chunking
**File:** `example_rag_pipeline.py`

**Features demonstrated:**
- Different chunking strategies (character, token, sentence, semantic)
- Creating embeddings for document chunks
- Building a simple vector store
- Query-based retrieval with cosine similarity

**Run:**
```bash
python examples/example_rag_pipeline.py
```

### 3. Structured Output with Pydantic Parsing
**File:** `example_structured_output.py`

**Features demonstrated:**
- ✅ **Full pipe chain:** `query | template | llm | parser` ⭐ **NEW!**
- ✅ Standard pipe chain: `template | llm | parser`
- Type-safe output parsing with Pydantic models
- Automatic format instruction injection
- Validation and error handling

**Run:**
```bash
python examples/example_structured_output.py
```

**Example code (standard):**
```python
class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    steps: List[str]

template = PromptTemplate(
    system="You are a chef.",
    template="Create a recipe for {dish}."
)
llm = get_llm("openai:gpt-4o-mini")
parser = PydanticOutputParser(Recipe)

# Beautiful pipe composition!
chain = template | llm | parser
recipe = chain({"dish": "pasta"})  # Returns Recipe object!
```

**Example code (full chain - most elegant!):**
```python
# THE MOST ELEGANT FORM!
query = "Suggest a healthy breakfast recipe"

# Template WITHOUT {query} - it's added automatically!
template = PromptTemplate(
    system="You are a nutritionist.",
    template="Make it high in protein."
)
llm = get_llm("openai:gpt-4o-mini")
parser = PydanticOutputParser(Recipe)

# Query pipes through everything and is auto-added to template!
chain = query | template | llm | parser
recipe = chain()  # No variables needed - query is in the chain!
```

## Running All Examples

Each example can be run independently:

```bash
# Run individual examples
python examples/example_llm_chains.py
python examples/example_rag_pipeline.py
python examples/example_structured_output.py
```

## Key Features Showcased

### Pipe Operator Chaining ✨
The most elegant feature - compose your AI workflows naturally:
- `template | llm` → Create LLM chains
- `template | llm | parser` → Add type-safe parsing
- `query | template | llm | parser` → **The ultimate form!** ⭐
  - Query string embedded in chain
  - No variables needed when calling
  - Pure functional composition
- Format instructions automatically injected
- Clean, readable, composable code

### Multi-Provider Support
Switch between providers with a single line:
```python
llm = get_llm("openai:gpt-4o-mini")
llm = get_llm("anthropic:claude-3-haiku")
llm = get_llm("google:gemini-1.5-flash")
```

### Type-Safe Outputs
Parse LLM responses into validated Pydantic models automatically.

### Smart Document Processing
Multiple chunking strategies for RAG pipelines with embeddings.

## Notes

- Examples gracefully handle missing API keys
- All examples are concise (<200 lines) and self-contained
- Windows-compatible (no Unicode encoding errors)
- Fully tested and verified working
- Zero linter errors
