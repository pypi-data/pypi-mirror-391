"""
Example 3: Structured Output with Pydantic Parsing

Demonstrates:
- Type-safe output parsing with Pydantic models
- Automatic format instruction injection
- Chain composition with parsers
- Error handling and validation
"""

from typing import List
from pydantic import BaseModel, Field
from genai_forge import get_llm, PydanticOutputParser
from prompting_forge.prompting import PromptTemplate


# Define Pydantic models
class Recipe(BaseModel):
    """A cooking recipe with structured fields"""
    name: str = Field(description="Name of the dish")
    cuisine: str = Field(description="Type of cuisine")
    prep_time_minutes: int = Field(description="Preparation time in minutes")
    ingredients: List[str] = Field(description="List of ingredients")
    steps: List[str] = Field(description="Cooking steps")


class CodeReview(BaseModel):
    """Code review with structured feedback"""
    language: str = Field(description="Programming language")
    issues: List[str] = Field(description="List of issues found")
    suggestions: List[str] = Field(description="Improvement suggestions")
    rating: int = Field(description="Code quality rating from 1-10", ge=1, le=10)


class TravelPlan(BaseModel):
    """Travel itinerary for a city"""
    city: str = Field(description="City name")
    days: int = Field(description="Number of days")
    attractions: List[str] = Field(description="Must-visit attractions")
    estimated_budget: int = Field(description="Estimated budget in USD")


def example_recipe_parsing():
    """Parse recipe into structured format"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Recipe Parsing")
    print("=" * 70)
    
    # Create parser
    parser = PydanticOutputParser(Recipe)
    
    # Create template
    template = PromptTemplate(
        system="You are a culinary expert. Provide structured recipe information.",
        template="Create a recipe for {dish}."
    )
    
    # Create LLM
    llm = get_llm("openai:gpt-4o-mini", temperature=0.7)
    
    # Create elegant chain: template | llm | parser
    chain = template | llm | parser
    result = chain({"dish": "vegetarian tacos"})
    
    print(f"\nParsed Recipe:")
    print(f"  Name: {result.name}")
    print(f"  Cuisine: {result.cuisine}")
    print(f"  Prep Time: {result.prep_time_minutes} minutes")
    print(f"  Ingredients ({len(result.ingredients)}):")
    for ing in result.ingredients[:3]:
        print(f"    - {ing}")
    if len(result.ingredients) > 3:
        print(f"    ... and {len(result.ingredients) - 3} more")
    print(f"  Steps: {len(result.steps)} steps")
    print()


def example_code_review():
    """Parse code review into structured feedback"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Code Review Parsing")
    print("=" * 70)
    
    code_snippet = """
def calculate_total(items):
    total = 0
    for i in items:
        total = total + i
    return total
"""
    
    parser = PydanticOutputParser(CodeReview)
    
    template = PromptTemplate(
        system="You are a code reviewer. Analyze code and provide structured feedback.",
        template="Review this code:\n```python\n{code}\n```"
    )
    
    llm = get_llm("openai:gpt-4o-mini", temperature=0.3)
    
    # Create elegant chain: template | llm | parser
    chain = template | llm | parser
    result = chain({"code": code_snippet})
    
    print(f"\nParsed Code Review:")
    print(f"  Language: {result.language}")
    print(f"  Quality Rating: {result.rating}/10")
    print(f"  Issues Found ({len(result.issues)}):")
    for issue in result.issues:
        print(f"    - {issue}")
    print(f"  Suggestions ({len(result.suggestions)}):")
    for suggestion in result.suggestions[:2]:
        print(f"    - {suggestion}")
    print()


def example_travel_planning():
    """Parse travel plan into structured itinerary"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Travel Planning")
    print("=" * 70)
    
    parser = PydanticOutputParser(TravelPlan)
    
    template = PromptTemplate(
        system="You are a travel planning expert.",
        template="Create a {days}-day travel plan for {city}."
    )
    
    llm = get_llm("openai:gpt-4o-mini", temperature=0.5)
    
    # Create elegant chain: template | llm | parser
    chain = template | llm | parser
    result = chain({"city": "Barcelona", "days": 3})
    
    print(f"\nParsed Travel Plan:")
    print(f"  City: {result.city}")
    print(f"  Duration: {result.days} days")
    print(f"  Estimated Budget: ${result.estimated_budget}")
    print(f"  Attractions ({len(result.attractions)}):")
    for attraction in result.attractions:
        print(f"    - {attraction}")
    print()


def example_full_pipe_chain():
    """The most elegant form: query | template | llm | parser"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Full Pipe Chain (query | template | llm | parser)")
    print("=" * 70)
    
    # Define a simple query string
    query = "Suggest a healthy breakfast recipe"
    
    # Template WITHOUT {query} - it's added automatically!
    template = PromptTemplate(
        system="You are a nutritionist and chef.",
        template="Make it high in protein and under 400 calories."
    )
    
    llm = get_llm("openai:gpt-4o-mini", temperature=0.6)
    parser = PydanticOutputParser(Recipe)
    
    # THE MOST ELEGANT FORM: query pipes through everything!
    # The query is automatically prepended to the template
    chain = query | template | llm | parser
    result = chain()  # No need to pass variables - query is already in the chain!
    
    print("\nFull chain executed: query | template | llm | parser")
    print("\nParsed Recipe:")
    print(f"  Name: {result.name}")
    print(f"  Cuisine: {result.cuisine}")
    print(f"  Prep Time: {result.prep_time_minutes} minutes")
    print(f"  Ingredients ({len(result.ingredients)}):")
    for ing in result.ingredients[:5]:
        print(f"    - {ing}")
    if len(result.ingredients) > 5:
        print(f"    ... and {len(result.ingredients) - 5} more")
    print(f"  Steps: {len(result.steps)} steps")
    print()


def example_format_instructions():
    """Show what format instructions look like"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Format Instructions (Behind the Scenes)")
    print("=" * 70)
    
    parser = PydanticOutputParser(Recipe)
    instructions = parser.get_format_instructions()
    
    print("\nFormat instructions automatically injected into prompts:")
    print("-" * 70)
    print(instructions[:400] + "...")
    print("-" * 70)
    print("\nThese instructions tell the LLM how to format its response")
    print("so it can be validated against the Pydantic model.\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("         Structured Output with Pydantic Parsing")
    print("=" * 70)
    
    try:
        example_recipe_parsing()
    except Exception as e:
        print(f"[ERROR] Example 1 failed: {e}\n")
    
    try:
        example_code_review()
    except Exception as e:
        print(f"[ERROR] Example 2 failed: {e}\n")
    
    try:
        example_travel_planning()
    except Exception as e:
        print(f"[ERROR] Example 3 failed: {e}\n")
    
    try:
        example_full_pipe_chain()
    except Exception as e:
        print(f"[ERROR] Example 4 failed: {e}\n")
    
    try:
        example_format_instructions()
    except Exception as e:
        print(f"[ERROR] Example 5 failed: {e}\n")
    
    print("=" * 70)
    print("Examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

