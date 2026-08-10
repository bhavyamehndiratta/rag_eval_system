from fastapi import APIRouter
from app.services.ingestion import ingest_documents

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("")
def ingest():
    return ingest_documents()
