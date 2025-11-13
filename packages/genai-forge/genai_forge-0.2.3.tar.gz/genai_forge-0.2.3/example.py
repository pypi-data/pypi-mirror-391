from __future__ import annotations

from typing import List

from pydantic import BaseModel

from genai_forge import get_llm, get_embedding, PydanticOutputParser
from prompting_forge.prompting import PromptTemplate


class CityPlan(BaseModel):
	"""A travel plan for a city."""
	city: str
	attractions: List[str]
	days: int


def example_basic_usage():
	"""Basic example with a single provider."""
	print("=" * 70)
	print("EXAMPLE 1: Basic Usage with OpenAI")
	print("=" * 70)
	
	template = PromptTemplate(
		system="You are a concise assistant.",
		template="Create a weekend plan.\nCity: {city}",
	)

	llm = get_llm("openai:gpt-4o-mini", temperature=0.2)
	parser = PydanticOutputParser(CityPlan)

	query = "Generate a simple weekend plan for a city."
	chain = query | template | llm | parser
	plan = chain({"city": "Lisbon"})

	print(f"\nCity: {plan.city}")
	print(f"Days: {plan.days}")
	print(f"Attractions: {', '.join(plan.attractions)}")
	print()


def example_embeddings():
	"""Example using embeddings for semantic search."""
	print("=" * 70)
	print("EXAMPLE 2: Embeddings for Semantic Search")
	print("=" * 70)
	
	try:
		# Create embedding model
		embedding = get_embedding("openai:text-embedding-3-small")
		
		# Documents to search
		documents = [
			"Python is a popular programming language",
			"Machine learning uses algorithms to learn patterns",
			"Natural language processing analyzes text data",
			"Web development creates interactive websites",
		]
		
		# Embed documents
		print("\nEmbedding documents...")
		doc_vectors = embedding(documents)
		print(f"Created {len(doc_vectors)} document vectors")
		print(f"Each vector has {len(doc_vectors[0])} dimensions")
		
		# Query
		query = "What helps computers understand human language?"
		print(f"\nQuery: {query}")
		query_vector = embedding(query)
		
		# Compute cosine similarities (simple version)
		def dot_product(a, b):
			return sum(x * y for x, y in zip(a, b))
		
		def magnitude(v):
			return sum(x * x for x in v) ** 0.5
		
		def cosine_similarity(a, b):
			return dot_product(a, b) / (magnitude(a) * magnitude(b))
		
		similarities = [cosine_similarity(query_vector, doc) for doc in doc_vectors]
		
		# Find most similar document
		best_idx = max(range(len(similarities)), key=lambda i: similarities[i])
		print(f"\nMost relevant document:")
		print(f"  → {documents[best_idx]}")
		print(f"  Similarity: {similarities[best_idx]:.4f}")
		print()
		
	except Exception as e:
		print(f"❌ Error: {e}")
		print()


def example_multi_provider():
	"""Compare outputs from multiple providers."""
	print("=" * 70)
	print("EXAMPLE 3: Multi-Provider Comparison")
	print("=" * 70)
	
	template = PromptTemplate(
		system="You are a creative haiku poet.",
		template="Write a haiku about {topic}.",
	)

	# List of providers to try
	providers = [
		("openai:gpt-4o-mini", "OpenAI GPT-4o-mini"),
		("anthropic:claude-3-5-haiku-20241022", "Anthropic Claude 3.5 Haiku"),
		("google:gemini-1.5-flash", "Google Gemini 1.5 Flash"),
		("mistral:mistral-small-latest", "Mistral Small"),
		("cohere:command-light", "Cohere Command Light"),
	]

	context = {"topic": "artificial intelligence"}

	for provider_model, display_name in providers:
		try:
			llm = get_llm(provider_model, temperature=0.7)
			chain = template | llm
			result = chain(context)
			print(f"\n{display_name}:")
			print("-" * 50)
			print(result)
		except ImportError as e:
			print(f"\n{display_name}:")
			print("-" * 50)
			print(f"⚠️  Provider not installed. Install with: pip install genai-forge[{provider_model.split(':')[0]}]")
		except ValueError as e:
			print(f"\n{display_name}:")
			print("-" * 50)
			print(f"⚠️  {e}")
		except Exception as e:
			print(f"\n{display_name}:")
			print("-" * 50)
			print(f"❌ Error: {e}")
	
	print()


def example_structured_output():
	"""Example with structured output parsing across providers."""
	print("=" * 70)
	print("EXAMPLE 4: Structured Output with Multiple Providers")
	print("=" * 70)
	
	template = PromptTemplate(
		system="You are a helpful travel planner.",
		template="Create a {days}-day travel plan for {city}.",
	)

	parser = PydanticOutputParser(CityPlan)

	# Try with different providers
	providers = [
		"openai:gpt-4o-mini",
		"anthropic:claude-3-5-haiku-20241022",
		"google:gemini-1.5-flash",
	]

	context = {"city": "Paris", "days": 3}
	query = "Create a detailed travel plan."

	for provider_model in providers:
		try:
			llm = get_llm(provider_model, temperature=0.1)
			chain = query | template | llm | parser
			plan = chain(context)
			
			provider_name = provider_model.split(":")[1] if ":" in provider_model else provider_model
			print(f"\n{provider_name}:")
			print("-" * 50)
			print(f"City: {plan.city}")
			print(f"Days: {plan.days}")
			print(f"Attractions ({len(plan.attractions)}):")
			for i, attraction in enumerate(plan.attractions[:3], 1):  # Show first 3
				print(f"  {i}. {attraction}")
			if len(plan.attractions) > 3:
				print(f"  ... and {len(plan.attractions) - 3} more")
		except ImportError:
			provider_name = provider_model.split(":")[0]
			print(f"\n{provider_model}:")
			print("-" * 50)
			print(f"⚠️  Provider not installed. Install with: pip install genai-forge[{provider_name}]")
		except Exception as e:
			print(f"\n{provider_model}:")
			print("-" * 50)
			print(f"❌ Error: {e}")
	
	print()


def example_provider_switching():
	"""Show how easy it is to switch providers."""
	print("=" * 70)
	print("EXAMPLE 5: Easy Provider Switching")
	print("=" * 70)
	
	template = PromptTemplate(
		system="You are a helpful coding assistant.",
		template="Explain {concept} in one sentence.",
	)

	concepts = ["recursion", "polymorphism", "async/await"]
	
	# Same template, different providers
	print("\nUsing OpenAI:")
	print("-" * 50)
	try:
		llm_openai = get_llm("openai:gpt-4o-mini", temperature=0.3)
		for concept in concepts:
			chain = template | llm_openai
			result = chain({"concept": concept})
			print(f"• {concept.capitalize()}: {result}")
	except Exception as e:
		print(f"❌ OpenAI error: {e}")
	
	print("\nUsing Anthropic Claude:")
	print("-" * 50)
	try:
		llm_claude = get_llm("anthropic:claude-3-5-haiku-20241022", temperature=0.3)
		for concept in concepts:
			chain = template | llm_claude
			result = chain({"concept": concept})
			print(f"• {concept.capitalize()}: {result}")
	except ImportError:
		print("⚠️  Anthropic not installed. Install with: pip install genai-forge[anthropic]")
	except Exception as e:
		print(f"❌ Anthropic error: {e}")
	
	print()


def main() -> None:
	"""Run all examples."""
	print("\n")
	print("╔" + "=" * 68 + "╗")
	print("║" + " " * 15 + "GENAI-FORGE MULTI-PROVIDER EXAMPLES" + " " * 17 + "║")
	print("╚" + "=" * 68 + "╝")
	print()
	print("These examples demonstrate genai-forge's multi-provider support.")
	print("Make sure you have the required API keys in your .env file.")
	print()
	
	# Run examples
	try:
		example_basic_usage()
	except Exception as e:
		print(f"Example 1 failed: {e}\n")
	
	try:
		example_embeddings()
	except Exception as e:
		print(f"Example 2 failed: {e}\n")
	
	try:
		example_multi_provider()
	except Exception as e:
		print(f"Example 3 failed: {e}\n")
	
	try:
		example_structured_output()
	except Exception as e:
		print(f"Example 4 failed: {e}\n")
	
	try:
		example_provider_switching()
	except Exception as e:
		print(f"Example 5 failed: {e}\n")
	
	print("=" * 70)
	print("Examples completed!")
	print("=" * 70)
	print()


if __name__ == "__main__":
	main()

