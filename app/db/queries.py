import json
from app.db.database import get_connection


def save_query(query: str, strategy: str, alpha: float, k: int, chunks: list, answer: str, latency_ms: float):
    conn = get_connection()
    conn.execute("""
        INSERT INTO queries (query, strategy, alpha, k, chunks_retrieved, answer, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (query, strategy, alpha, k, json.dumps(chunks), answer, latency_ms))
    conn.commit()
    conn.close()


def get_recent_queries(limit: int = 20) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM queries ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
