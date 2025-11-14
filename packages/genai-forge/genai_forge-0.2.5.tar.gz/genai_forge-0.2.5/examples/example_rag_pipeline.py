"""
Example 2: RAG Pipeline with Document Chunking

Demonstrates:
- Different chunking strategies (character, token, sentence, semantic)
- Creating embeddings for chunks
- Building a simple retrieval system
- Query-based document retrieval
"""

from genai_forge import get_chunker, get_embedding
import math


# Sample document for RAG
DOCUMENT = """
Python is a high-level programming language known for its simplicity and readability.
It was created by Guido van Rossum and first released in 1991. Python's design 
philosophy emphasizes code readability with significant indentation.

Python supports multiple programming paradigms including procedural, object-oriented,
and functional programming. It has a comprehensive standard library that provides 
tools for file I/O, system calls, networking, and more.

The language is widely used in web development, data science, artificial intelligence,
scientific computing, and automation. Popular frameworks include Django and Flask for
web development, and NumPy and Pandas for data analysis.

Python's ecosystem includes package managers like pip and conda, which make it easy
to install and manage third-party libraries. The Python Package Index (PyPI) hosts
hundreds of thousands of packages for various purposes.
"""


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (magnitude1 * magnitude2) if magnitude1 and magnitude2 else 0


def example_chunking_strategies():
    """Compare different chunking strategies"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Chunking Strategies Comparison")
    print("=" * 70)
    
    strategies = [
        ("character", {"chunk_size": 200, "chunk_overlap": 50}),
        ("sentence", {"chunk_size": 200, "chunk_overlap": 50}),
        ("token", {"chunk_size": 50, "chunk_overlap": 10, "encoding_name": "cl100k_base"}),
    ]
    
    for strategy_name, params in strategies:
        try:
            chunker = get_chunker(strategy_name, **params)
            chunks = chunker.chunk(DOCUMENT)
            
            print(f"\n{strategy_name.upper()} Chunker:")
            print(f"  Total chunks: {len(chunks)}")
            print(f"  Avg size: {sum(len(c.text) for c in chunks) / len(chunks):.0f} chars")
            print(f"  First chunk: {chunks[0].text[:80]}...")
        except ImportError as e:
            print(f"\n{strategy_name.upper()} Chunker: [SKIP] Requires additional dependencies")
        except Exception as e:
            print(f"\n{strategy_name.upper()} Chunker: [ERROR] {e}")


def example_semantic_chunking():
    """Semantic chunking with embeddings"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Semantic Chunking")
    print("=" * 70)
    
    try:
        # Get embedding model
        embedding = get_embedding("openai:text-embedding-3-small")
        
        # Create semantic chunker
        chunker = get_chunker(
            "semantic",
            embedding=embedding,
            chunk_size=300,
            similarity_threshold=0.75,
            min_chunk_size=50
        )
        
        chunks = chunker.chunk(DOCUMENT)
        
        print(f"\nCreated {len(chunks)} semantic chunks")
        print("Chunks are grouped by semantic similarity:\n")
        
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i + 1}:")
            print(f"  Length: {len(chunk.text)} chars")
            print(f"  Preview: {chunk.text[:100]}...")
            print()
    
    except Exception as e:
        print(f"\n[SKIP] Semantic chunking requires OpenAI API key")
        print(f"Error: {e}\n")


def example_rag_retrieval():
    """Complete RAG pipeline: chunk, embed, and retrieve"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Simple RAG Retrieval System")
    print("=" * 70)
    
    try:
        # 1. Chunk the document
        chunker = get_chunker("sentence", chunk_size=250, chunk_overlap=50)
        chunks = chunker.chunk(DOCUMENT)
        print(f"\n1. Chunked document into {len(chunks)} chunks")
        
        # 2. Create embeddings
        embedding = get_embedding("openai:text-embedding-3-small")
        chunk_texts = [chunk.text for chunk in chunks]
        chunk_embeddings = embedding(chunk_texts)
        print(f"2. Created {len(chunk_embeddings)} embeddings")
        
        # 3. Store in simple vector store
        vector_store = [
            {"chunk": chunk, "embedding": emb}
            for chunk, emb in zip(chunks, chunk_embeddings)
        ]
        print(f"3. Built vector store with {len(vector_store)} entries")
        
        # 4. Query the system
        queries = [
            "What is Python used for?",
            "Who created Python?",
            "What are Python package managers?"
        ]
        
        print("\n4. Querying the system:\n")
        
        for query in queries:
            # Embed query
            query_embedding = embedding(query)
            
            # Calculate similarities
            similarities = [
                (i, cosine_similarity(query_embedding, doc["embedding"]))
                for i, doc in enumerate(vector_store)
            ]
            
            # Get most relevant chunk
            best_idx, best_score = max(similarities, key=lambda x: x[1])
            best_chunk = vector_store[best_idx]["chunk"]
            
            print(f"Query: '{query}'")
            print(f"  Similarity: {best_score:.4f}")
            print(f"  Answer: {best_chunk.text[:150]}...")
            print()
    
    except Exception as e:
        print(f"\n[SKIP] RAG pipeline requires OpenAI API key")
        print(f"Error: {e}\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("            RAG Pipeline with Document Chunking")
    print("=" * 70)
    
    example_chunking_strategies()
    example_semantic_chunking()
    example_rag_retrieval()
    
    print("=" * 70)
    print("Examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

