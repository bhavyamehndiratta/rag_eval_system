from fastapi import FastAPI
from app.api.routes import health, ingest, retrieve, generate, evaluate

app = FastAPI(title="RAG Eval", version="0.1.0")
app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(retrieve.router)
app.include_router(generate.router)
app.include_router(evaluate.router)
