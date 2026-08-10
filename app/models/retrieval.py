from pydantic import BaseModel
from typing import Optional

class RetrievalRequest(BaseModel):
    query: str
    k: int = 5
    strategy: str = "hybrid"
    alpha: float = 0.5

class ChunkResult(BaseModel):
    id: str
    text: str
    metadata: dict
    score: float

class RetrievalResponse(BaseModel):
    query: str
    strategy: str
    results: list[ChunkResult]
