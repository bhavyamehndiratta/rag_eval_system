import json
import time
import statistics
from pathlib import Path
from app.services.retrieval import semantic_retrieve, bm25_retrieve, hybrid_retrieve, reranked_hybrid_retrieve


STRATEGIES = {
    "semantic": lambda q, k: semantic_retrieve(q, k),
    "bm25": lambda q, k: bm25_retrieve(q, k),
    "hybrid": lambda q, k: hybrid_retrieve(q, k),
    "reranked": lambda q, k: reranked_hybrid_retrieve(q, k),
}


def precision_at_k(retrieved_ids: list, relevant_ids: list, k: int) -> float:
    retrieved_k = retrieved_ids[:k]
    hits = sum(1 for id_ in retrieved_k if id_ in relevant_ids)
    return hits / k if k > 0 else 0.0


def recall_at_k(retrieved_ids: list, relevant_ids: list, k: int) -> float:
    retrieved_k = retrieved_ids[:k]
    hits = sum(1 for id_ in retrieved_k if id_ in relevant_ids)
    return hits / len(relevant_ids) if relevant_ids else 0.0


def run_evaluation(testset_path: str, k: int = 5) -> dict:
    testset = json.loads(Path(testset_path).read_text())
    results = {strategy: {"precision": [], "recall": [], "latencies": []} for strategy in STRATEGIES}

    for item in testset:
        question = item["question"]
        relevant_ids = item["relevant_chunk_ids"]

        for strategy_name, retrieve_fn in STRATEGIES.items():
            start = time.time()
            chunks = retrieve_fn(question, k)
            latency = time.time() - start

            retrieved_ids = [c["id"] for c in chunks]
            p = precision_at_k(retrieved_ids, relevant_ids, k)
            r = recall_at_k(retrieved_ids, relevant_ids, k)

            results[strategy_name]["precision"].append(p)
            results[strategy_name]["recall"].append(r)
            results[strategy_name]["latencies"].append(latency)

    summary = {}
    precision_scores = {}
    for strategy, data in results.items():
        summary[strategy] = {
            "precision_at_5": round(statistics.mean(data["precision"]), 4),
            "recall_at_5": round(statistics.mean(data["recall"]), 4),
            "latency_median_ms": round(statistics.median(data["latencies"]) * 1000, 2),
        }
        precision_scores[strategy] = data["precision"]

    diffs = [r - s for r, s in zip(precision_scores["reranked"], precision_scores["semantic"])]
    if any(d != 0 for d in diffs):
        from scipy import stats
        t_stat, p_value = stats.ttest_rel(precision_scores["reranked"], precision_scores["semantic"])
        summary["statistical_test"] = {
            "test": "paired t-test reranked vs semantic precision@5",
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_value), 4),
            "significant": bool(p_value < 0.05),
        }
    else:
        summary["statistical_test"] = {
            "test": "paired t-test reranked vs semantic precision@5",
            "note": "no variance between strategies on this corpus — scores identical",
        }

    return summary
