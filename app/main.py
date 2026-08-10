from fastapi import FastAPI
from app.api.routes import health, ingest, retrieve

app = FastAPI(title="RAG Eval", version="0.1.0")
app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(retrieve.router)
