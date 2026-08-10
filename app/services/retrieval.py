import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_PATH = "data/chroma"
EMBED_MODEL = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(EMBED_MODEL)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("documents")


def load_bm25():
    from rank_bm25 import BM25Okapi
    data = json.loads(Path("data/bm25_corpus.json").read_text())
    corpus = [doc.lower().split() for doc in data["corpus"]]
    bm25 = BM25Okapi(corpus)
    return bm25, data["corpus"], data["ids"], data["metadata"]


def semantic_retrieve(query: str, k: int = 5) -> list[dict]:
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)
    return [
        {"id": id_, "text": doc, "metadata": meta, "score": float(1 - dist)}
        for id_, doc, meta, dist in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def bm25_retrieve(query: str, k: int = 5) -> list[dict]:
    bm25, corpus, ids, metadata = load_bm25()
    scores = bm25.get_scores(query.lower().split())
    top_k = np.argsort(scores)[::-1][:k]
    return [
        {"id": ids[i], "text": corpus[i], "metadata": metadata[i], "score": float(scores[i])}
        for i in top_k
    ]


def hybrid_retrieve(query: str, k: int = 5, alpha: float = 0.5) -> list[dict]:
    bm25, corpus, ids, metadata = load_bm25()

    # BM25 scores
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_max = bm25_scores.max() or 1.0
    bm25_norm = bm25_scores / bm25_max

    # Semantic scores — fetch all docs
    query_embedding = embedding_model.encode([query]).tolist()
    n_results = min(len(corpus), max(k, 20))
    results = collection.query(query_embeddings=query_embedding, n_results=n_results)

    semantic_scores = np.zeros(len(corpus))
    id_to_index = {id_: i for i, id_ in enumerate(ids)}
    for id_, dist in zip(results["ids"][0], results["distances"][0]):
        if id_ in id_to_index:
            semantic_scores[id_to_index[id_]] = 1 - dist

    sem_max = semantic_scores.max() or 1.0
    sem_norm = semantic_scores / sem_max

    combined = alpha * sem_norm + (1 - alpha) * bm25_norm
    top_k = np.argsort(combined)[::-1][:k]

    return [
        {"id": ids[i], "text": corpus[i], "metadata": metadata[i], "score": float(combined[i])}
        for i in top_k
    ]


def reranked_hybrid_retrieve(query: str, k: int = 5, alpha: float = 0.5, fetch_n: int = 20) -> list[dict]:
    from app.services.reranking import rerank
    candidates = hybrid_retrieve(query, k=fetch_n, alpha=alpha)
    return rerank(query, candidates, top_k=k)


def hyde_retrieve(query: str, k: int = 5, alpha: float = 0.5) -> list[dict]:
    from app.services.hyde import generate_hypothetical_answer
    from app.services.reranking import rerank
    hypothetical = generate_hypothetical_answer(query)
    candidates = hybrid_retrieve(hypothetical, k=20, alpha=alpha)
    return rerank(query, candidates, top_k=k)
