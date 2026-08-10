from sentence_transformers import CrossEncoder

RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
reranker = CrossEncoder(RERANK_MODEL)


def rerank(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    pairs = [(query, chunk["text"]) for chunk in chunks]
    scores = reranker.predict(pairs)
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)
    ranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]
