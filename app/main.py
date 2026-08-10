from fastapi import FastAPI
from app.api.routes import health, ingest, retrieve, generate, evaluate, history
from app.db.database import init_db

app = FastAPI(title="RAG Eval", version="0.1.0")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(retrieve.router)
app.include_router(generate.router)
app.include_router(evaluate.router)
app.include_router(history.router)
