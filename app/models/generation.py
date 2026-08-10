from pydantic import BaseModel

class GenerationRequest(BaseModel):
    query: str
    k: int = 5
    strategy: str = "hybrid"
    alpha: float = 0.5

class GenerationResponse(BaseModel):
    query: str
    answer: str
    chunks_used: list[dict]
