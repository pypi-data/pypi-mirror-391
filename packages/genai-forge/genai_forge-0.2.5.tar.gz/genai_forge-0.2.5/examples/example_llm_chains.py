"""
Example 1: LLM Chains with Multiple Providers

Demonstrates:
- Using different LLM providers (OpenAI, Anthropic, Google, Mistral)
- Composable chains with pipe operators
- Integration with prompting-forge templates
"""

from genai_forge import get_llm
from prompting_forge.prompting import PromptTemplate


def example_simple_chain():
    """Simple chain with template and LLM"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple LLM Chain")
    print("=" * 70)
    
    # Create a prompt template
    template = PromptTemplate(
        system="You are a helpful AI assistant. Be concise.",
        template="Tell me an interesting fact about {topic}."
    )
    
    # Use OpenAI
    llm = get_llm("openai:gpt-4o-mini", temperature=0.7)
    
    # Create and execute chain: template | llm
    chain = template | llm
    result = chain({"topic": "quantum computing"})
    
    print(f"\nResult:\n{result}\n")


def example_multi_provider():
    """Compare responses from different providers"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multiple Providers Comparison")
    print("=" * 70)
    
    template = PromptTemplate(
        system="You are a creative writing assistant.",
        template="Write a one-sentence story about {subject}."
    )
    
    # Different providers
    providers = [
        ("openai:gpt-4o-mini", "OpenAI"),
        ("anthropic:claude-3-haiku-20240307", "Anthropic"),
        ("google:gemini-1.5-flash", "Google"),
    ]
    
    context = {"subject": "a robot learning to paint"}
    
    for model, name in providers:
        try:
            llm = get_llm(model, temperature=0.8)
            chain = template | llm
            result = chain(context)
            print(f"\n{name}:")
            print(f"  {result}")
        except Exception as e:
            print(f"\n{name}: [SKIP] {e}")


def example_query_template_llm():
    """Full workflow: query + template + LLM"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Query + Template + LLM")
    print("=" * 70)
    
    # Define a query
    query = "Give me a coding tip for beginners."
    
    # Template expects context variables including query
    template = PromptTemplate(
        system="You are an expert programming instructor.",
        template="{query}\nLanguage: {language}\nExperience: {experience}"
    )
    
    llm = get_llm("openai:gpt-4o-mini", temperature=0.5)
    
    # Create chain and execute
    context = {
        "query": query,
        "language": "Python",
        "experience": "beginner"
    }
    chain = template | llm
    result = chain(context)
    
    print(f"\nTip:\n{result}\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("            LLM Chains with Multiple Providers")
    print("=" * 70)
    
    try:
        example_simple_chain()
    except Exception as e:
        print(f"[ERROR] Example 1 failed: {e}\n")
    
    try:
        example_multi_provider()
    except Exception as e:
        print(f"[ERROR] Example 2 failed: {e}\n")
    
    try:
        example_query_template_llm()
    except Exception as e:
        print(f"[ERROR] Example 3 failed: {e}\n")
    
    print("=" * 70)
    print("Examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

