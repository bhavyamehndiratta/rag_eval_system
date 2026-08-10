import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def generate_hypothetical_answer(query: str) -> str:
    prompt = f"""Write a short factual passage (2-3 sentences) that would directly answer this question.
Do not say you don't know. Just write the most plausible answer as if it were from a document.

Question: {query}

Passage:"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
