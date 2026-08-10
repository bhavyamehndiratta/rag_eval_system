from fastapi import APIRouter
from app.models.generation import GenerationRequest, GenerationResponse
from app.services.retrieval import semantic_retrieve, bm25_retrieve, hybrid_retrieve
from app.services.generation import generate_answer

router = APIRouter(prefix="/generate", tags=["generate"])

@router.post("", response_model=GenerationResponse)
def generate(request: GenerationRequest):
    if request.strategy == "semantic":
        chunks = semantic_retrieve(request.query, request.k)
    elif request.strategy == "bm25":
        chunks = bm25_retrieve(request.query, request.k)
    else:
        chunks = hybrid_retrieve(request.query, request.k, request.alpha)

    return generate_answer(request.query, chunks)
