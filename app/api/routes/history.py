from fastapi import APIRouter
from app.db.queries import get_recent_queries

router = APIRouter(prefix="/history", tags=["history"])

@router.get("")
def history(limit: int = 20):
    return get_recent_queries(limit)
