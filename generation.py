"""
generation.py
Phase 3: RAG Answer Generation with Groq API.

Takes a user question, retrieves relevant passages using the retrieval engine,
and generates a grounded answer with citations using Groq's LLM API.
"""

import os
from typing import List, Dict, Any, Optional

from groq import Groq
from dotenv import load_dotenv

import retrieval

# Load environment variables from .env file
load_dotenv()

# Groq client (initialized lazily)
_GROQ_CLIENT: Optional[Groq] = None

# Default model — override with GROQ_MODEL in .env to switch without editing code.
# Available on Groq: llama-3.3-70b-versatile (best quality), llama-3.1-8b-instant
# (fast, separate rate-limit pool), openai/gpt-oss-20b, openai/gpt-oss-120b,
# qwen/qwen3.6-27b. Note each model has its own daily token quota.
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _get_groq_client() -> Groq:
    """Initialize and return Groq client."""
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in your .env file or environment variables.\n"
                "Create a .env file with: GROQ_API_KEY=your_api_key_here"
            )
        _GROQ_CLIENT = Groq(api_key=api_key)
    return _GROQ_CLIENT


def _build_context(passages: List[Dict[str, Any]]) -> str:
    """Format retrieved passages into a context string for the LLM."""
    if not passages:
        return "No relevant passages found in the knowledge base."
    
    context_parts = []
    for i, p in enumerate(passages, 1):
        source_info = f"[{i}] Source: {p['source']} | Document: {p['title']} | Page: {p['page_number']}"
        context_parts.append(f"{source_info}\n{p['text']}")
    
    return "\n\n---\n\n".join(context_parts)


def _build_system_prompt() -> str:
    """Build the system prompt for climate adaptation QA."""
    return """You are My Climate CoPilot, an expert assistant for climate adaptation in agriculture.

Your role is to help agronomists, climate scientists, and farmer advisors understand climate impacts and adaptation strategies.

Guidelines:
1. Answer questions based ONLY on the provided context passages
2. If the context doesn't contain enough information, clearly state what's missing
3. Cite sources using [1], [2], etc. corresponding to the passage numbers
4. Be specific about locations, crops, and timeframes when the context provides them
5. Explain scientific concepts in accessible language
6. Acknowledge uncertainties in climate projections where appropriate
7. Structure longer answers with clear headings when helpful

If asked about something not covered in the context, say: "Based on the available documents, I don't have specific information about [topic]. However, [provide any related context if available]."
"""


def _build_user_prompt(question: str, context: str) -> str:
    """Build the user prompt with question and context."""
    return f"""Based on the following passages from climate science literature, please answer the question.

=== RETRIEVED PASSAGES ===
{context}
=== END PASSAGES ===

Question: {question}

Please provide a comprehensive answer with citations to the relevant passages."""


def generate_answer(
    question: str,
    top_k: int = 5,
    source_filter: Optional[str] = None,
    retrieval_mode: str = "hybrid",
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Generate a grounded answer to a climate adaptation question.
    
    Args:
        question: User's natural language question
        top_k: Number of passages to retrieve
        source_filter: Optional filter by source (e.g., "IPCC", "FAO")
        retrieval_mode: "dense", "bm25", or "hybrid"
        model: Groq model to use
        temperature: LLM temperature (lower = more focused)
        max_tokens: Maximum tokens in response
        verbose: Print intermediate steps
    
    Returns:
        Dict with keys: question, answer, passages, model, usage
    """
    # Resolve the model once: explicit argument wins, otherwise fall back to
    # DEFAULT_MODEL (which itself honours GROQ_MODEL from .env).
    model = model or DEFAULT_MODEL

    # Step 1: Retrieve relevant passages
    if verbose:
        print(f"[1/3] Retrieving passages (mode={retrieval_mode}, top_k={top_k})...")
    
    passages = retrieval.search(
        query=question,
        top_k=top_k,
        source_filter=source_filter,
        mode=retrieval_mode
    )
    
    if verbose:
        print(f"      Found {len(passages)} relevant passages")
    
    # Step 2: Build prompts
    if verbose:
        print("[2/3] Building context and prompts...")
    
    context = _build_context(passages)
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(question, context)
    
    # Step 3: Generate answer with Groq
    if verbose:
        print(f"[3/3] Generating answer with {model}...")
    
    client = _get_groq_client()
    
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        stream=False
    )
    
    answer = completion.choices[0].message.content
    usage = {
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens
    }
    
    return {
        "question": question,
        "answer": answer,
        "passages": passages,
        "model": model,
        "retrieval_mode": retrieval_mode,
        "usage": usage
    }


def print_answer(result: Dict[str, Any], show_passages: bool = False) -> None:
    """Pretty print the generated answer."""
    print("\n" + "=" * 70)
    print(f" MY CLIMATE COPILOT")
    print("=" * 70)
    print(f"\n📝 Question: {result['question']}")
    print(f"\n🤖 Model: {result['model']} | Retrieval: {result['retrieval_mode']}")
    print(f"📊 Tokens: {result['usage']['total_tokens']} (prompt: {result['usage']['prompt_tokens']}, completion: {result['usage']['completion_tokens']})")
    print("\n" + "-" * 70)
    print("\n📖 ANSWER:\n")
    print(result['answer'])
    print("\n" + "-" * 70)
    
    # Show source references
    print("\n📚 SOURCES REFERENCED:")
    for i, p in enumerate(result['passages'], 1):
        print(f"  [{i}] {p['title']} ({p['source']}) - Page {p['page_number']}")
    
    if show_passages:
        print("\n" + "-" * 70)
        print("\n📄 RETRIEVED PASSAGES:\n")
        for i, p in enumerate(result['passages'], 1):
            print(f"--- Passage [{i}] ---")
            print(f"Source: {p['source']} | Document: {p['title']} | Page: {p['page_number']}")
            print(f"Text: {p['text'][:500]}{'...' if len(p['text']) > 500 else ''}")
            print()
    
    print("=" * 70 + "\n")


def ask(
    question: str,
    top_k: int = 5,
    source_filter: Optional[str] = None,
    retrieval_mode: str = "hybrid",
    model: Optional[str] = None,
    show_passages: bool = False,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to ask a question and print the answer.
    
    Returns the full result dict for programmatic use.
    """
    result = generate_answer(
        question=question,
        top_k=top_k,
        source_filter=source_filter,
        retrieval_mode=retrieval_mode,
        model=model,
        verbose=verbose
    )
    print_answer(result, show_passages=show_passages)
    return result


# Available Groq models for reference
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",    # Best quality, good speed (recommended)
    "llama-3.3-70b-specdec",      # Speculative decoding variant
    "llama3-70b-8192",            # Llama 3 70B
    "llama3-8b-8192",             # Llama 3 8B (fastest)
    "mixtral-8x7b-32768",         # Mixtral MoE, 32k context
    "gemma2-9b-it",               # Google Gemma 2
]


if __name__ == "__main__":
    # Test the generation pipeline
    test_question = "How will climate change affect wheat production in the coming decades?"
    result = ask(test_question, verbose=True, show_passages=True)
