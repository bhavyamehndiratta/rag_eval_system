from fastapi import APIRouter
from app.models.retrieval import RetrievalRequest, RetrievalResponse, ChunkResult
from app.services.retrieval import semantic_retrieve, bm25_retrieve, hybrid_retrieve

router = APIRouter(prefix="/retrieve", tags=["retrieve"])

@router.post("", response_model=RetrievalResponse)
def retrieve(request: RetrievalRequest):
    if request.strategy == "semantic":
        results = semantic_retrieve(request.query, request.k)
    elif request.strategy == "bm25":
        results = bm25_retrieve(request.query, request.k)
    else:
        results = hybrid_retrieve(request.query, request.k, request.alpha)

    return RetrievalResponse(
        query=request.query,
        strategy=request.strategy,
        results=[ChunkResult(**r) for r in results],
    )
