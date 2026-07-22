# mycart

AI Fashion Shopping Assistant

A chatbot built on Django e-commerce site that lets users search for products, or by uploading a photo of something similar to what they want. Built as a way to actually learn how agentic RAG systems work in practice, but build something with real routing, retrieval, and failure handling.

What the shopping assistant does - 
Ask for products something like "formal shoes for men under 1500" and get recommendations pulled from the actual product catalog, not made up.
Upload a photo of an item and get similar products, using the same underlying filter pipeline as text search.
Chat history persists per session and reloads correctly, including any product cards shown earlier.

How it works

The core of this is a LangGraph state graph:
- filter_extractor node - it takes the user's message and pulls out structured filters — category, colour, usage, price range — into a Pydantic schema (ProductMetadata). This gets turned into a Chroma metadata filter.
- vision_extract node - does the same job, but from an uploaded image, using a vision-language model (qwen2.5vl:3b). Text and image search end up feeding the same retrieval and filtering logic.
- product_retriever node - runs the actual vector similarity search against Chroma, using the extracted filter.
- generate_answer node - writes the final response, but only from what was actually retrieved it's explicitly told never to invent a product, price, or ID, and if nothing relevant came back from retrieval, it just says so instead of trying to answer anyway.

Chat state (including multi-turn context) is handled by LangGraph's checkpointer, keyed by the Django session ID.

Tech Stack
1. Backend: Django, Django REST Framework,
2. RAG: LangGraph, LangChain, ChromaDB, HuggingFace sentence-transformers for embeddings,
3. LLMs: Ollama running locally — llama3.2:3b for routing/extraction/generation, qwen2.5vl:3b for the vision,
4. Frontend: Vanilla JavaScript,
5. Database: PostgreSQL

What I will do next
1. Cut down the number of sequential LLM calls per turn (currently up to 4–5 — contextual rewrite, routing, extraction, generation) since that's the main latency cost right now, making the RAG with more optimized code.
2. For storing conversation will use Postgres-backed LangGraph checkpointer instead of memory so conversation state survives after a server restart, not just runs in memory.
3. Fine tuning of local model, as I had observed that some of the product which is unfamiliar for model not fetching the results correctly.
