import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
MODEL = "claude-sonnet-4-6"


def generate_answer(query: str, chunks: list[dict]) -> dict:
    context_blocks = []
    for i, chunk in enumerate(chunks):
        context_blocks.append(f"[{i+1}] (source: {chunk['metadata']['source']})\n{chunk['text']}")
    
    context = "\n\n".join(context_blocks)
    
    prompt = f"""You are a helpful assistant. Answer the question using ONLY the context provided below.
For every claim you make, cite the source chunk number inline like [1] or [2].
If the context does not contain enough information to answer, say so explicitly.

Context:
{context}

Question: {query}

Answer:"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = message.content[0].text
    return {
        "query": query,
        "answer": answer,
        "chunks_used": chunks,
    }
