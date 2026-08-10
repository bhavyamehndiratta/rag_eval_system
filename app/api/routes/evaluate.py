from fastapi import APIRouter
from app.services.evaluation import run_evaluation

router = APIRouter(prefix="/evaluate", tags=["evaluate"])

@router.post("")
def evaluate(testset: str = "evals/testsets/rag_basics.json", k: int = 5):
    return run_evaluation(testset, k)
