import time
from fastapi import APIRouter
from app.models.generation import GenerationRequest, GenerationResponse
from app.services.retrieval import semantic_retrieve, bm25_retrieve, hybrid_retrieve, reranked_hybrid_retrieve, hyde_retrieve
from app.services.generation import generate_answer
from app.db.queries import save_query

router = APIRouter(prefix="/generate", tags=["generate"])

@router.post("", response_model=GenerationResponse)
def generate(request: GenerationRequest):
    start = time.time()

    if request.strategy == "semantic":
        chunks = semantic_retrieve(request.query, request.k)
    elif request.strategy == "bm25":
        chunks = bm25_retrieve(request.query, request.k)
    elif request.strategy == "reranked":
        chunks = reranked_hybrid_retrieve(request.query, request.k, request.alpha)
    elif request.strategy == "hyde":
        chunks = hyde_retrieve(request.query, request.k, request.alpha)
    else:
        chunks = hybrid_retrieve(request.query, request.k, request.alpha)

    result = generate_answer(request.query, chunks)
    latency_ms = (time.time() - start) * 1000

    save_query(
        query=request.query,
        strategy=request.strategy,
        alpha=request.alpha,
        k=request.k,
        chunks=[c["id"] for c in chunks],
        answer=result["answer"],
        latency_ms=latency_ms,
    )

    return result
