import os
import json
import tiktoken
import chromadb
from pathlib import Path
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma"
CORPUS_PATH = "data/corpus"
CHUNK_SIZE = 256
CHUNK_OVERLAP = 50
EMBED_MODEL = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(EMBED_MODEL)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("documents")

tokenizer = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(tokenizer.decode(chunk_tokens))
        start += chunk_size - overlap
    return chunks


def ingest_documents() -> dict:
    corpus_dir = Path(CORPUS_PATH)
    files = list(corpus_dir.glob("*.txt")) + list(corpus_dir.glob("*.md"))
    
    if not files:
        return {"status": "no files found", "chunks_added": 0}

    all_chunks = []
    all_ids = []
    all_metadata = []
    bm25_corpus = []

    for file in files:
        text = file.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file.stem}_chunk_{i}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadata.append({"source": file.name, "chunk_index": i})
            bm25_corpus.append(chunk.lower().split())

    embeddings = embedding_model.encode(all_chunks, show_progress_bar=True).tolist()

    collection.upsert(
        documents=all_chunks,
        embeddings=embeddings,
        ids=all_ids,
        metadatas=all_metadata,
    )

    bm25_index = BM25Okapi(bm25_corpus)
    Path("data/bm25_corpus.json").write_text(
        json.dumps({"corpus": all_chunks, "ids": all_ids, "metadata": all_metadata})
    )

    return {"status": "ok", "chunks_added": len(all_chunks), "files": [f.name for f in files]}
