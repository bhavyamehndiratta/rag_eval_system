import { useState } from "react";
import axios, { AxiosError } from "axios";
import type {
  Strategy,
  Tab,
  GenerateRequest,
  GenerateResponse,
  Chunk,
  EvalResults,
  HistoryItem,
  ApiErrorBody,
} from "./types";

const API = "http://localhost:8000";

const TABS: Tab[] = ["ask", "evaluate", "history"];

/** Turns an axios failure into a message the user can act on. */
function describeError(err: unknown, networkMessage: string): string {
  const e = err as AxiosError<ApiErrorBody>;
  if (e.code === "ERR_NETWORK") return networkMessage;
  return e.response?.data?.detail || e.message || "Unexpected error.";
}

function App() {
  const [query, setQuery] = useState<string>("");
  const [strategy, setStrategy] = useState<Strategy>("hybrid");
  const [answer, setAnswer] = useState<string>("");
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [evalResults, setEvalResults] = useState<EvalResults | null>(null);
  const [evalError, setEvalError] = useState<string>("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [tab, setTab] = useState<Tab>("ask");

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setAnswer("");
    setChunks([]);
    try {
      const body: GenerateRequest = { query, strategy, k: 5, alpha: 0.5 };
      const res = await axios.post<GenerateResponse>(`${API}/generate`, body);
      setAnswer(res.data.answer);
      setChunks(res.data.chunks_used);
    } catch (e) {
      setError(describeError(e, "Cannot connect to backend. Make sure the FastAPI server is running on port 8000."));
    }
    setLoading(false);
  };

  const handleEval = async () => {
    setLoading(true);
    setEvalError("");
    setEvalResults(null);
    try {
      const res = await axios.post<EvalResults>(`${API}/evaluate`);
      setEvalResults(res.data);
    } catch (e) {
      setEvalError(describeError(e, "Cannot connect to backend."));
    }
    setLoading(false);
  };

  const handleHistory = async () => {
    try {
      const res = await axios.get<HistoryItem[]>(`${API}/history`);
      setHistory(res.data);
    } catch {
      setHistory([]);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 32, fontFamily: "sans-serif" }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>RAG Eval System</h1>
      <p style={{ color: "#666", marginBottom: 24 }}>
        Retrieval-Augmented Generation with rigorous evaluation across retrieval strategies.
      </p>

      <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => { setTab(t); if (t === "history") handleHistory(); }}
            style={{
              padding: "8px 20px",
              background: tab === t ? "#2A6FDB" : "#f0f0f0",
              color: tab === t ? "white" : "#333",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === "ask" && (
        <div>
          <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleAsk(); }}
              placeholder="Ask a question..."
              style={{ flex: 1, padding: "10px 14px", borderRadius: 6, border: "1px solid #ddd", fontSize: 15 }}
            />
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value as Strategy)}
              style={{ padding: "10px 14px", borderRadius: 6, border: "1px solid #ddd" }}
            >
              <option value="semantic">Semantic</option>
              <option value="bm25">BM25</option>
              <option value="hybrid">Hybrid</option>
              <option value="reranked">Reranked</option>
              <option value="hyde">HyDE</option>
            </select>
            <button
              onClick={handleAsk}
              disabled={loading}
              style={{ padding: "10px 20px", background: "#2A6FDB", color: "white", border: "none", borderRadius: 6, cursor: "pointer", fontWeight: 600 }}
            >
              {loading ? "Thinking..." : "Ask"}
            </button>
          </div>

          {error && (
            <div style={{ background: "#fff0f0", border: "1px solid #ffcccc", borderRadius: 6, padding: 12, marginBottom: 12, color: "#cc0000", fontSize: 14 }}>
              {error}
            </div>
          )}

          {!answer && !error && !loading && (
            <p style={{ color: "#aaa", fontSize: 14 }}>Ask a question to see the answer and retrieved chunks.</p>
          )}

          {loading && (
            <p style={{ color: "#888", fontSize: 14 }}>Retrieving and generating answer...</p>
          )}

          {answer && (
            <div style={{ background: "#f8f9fa", borderRadius: 8, padding: 20, marginBottom: 16 }}>
              <h3 style={{ marginBottom: 8, fontSize: 15, fontWeight: 600 }}>Answer</h3>
              <p style={{ lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{answer}</p>
            </div>
          )}

          {chunks.length > 0 && (
            <div>
              <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Retrieved Chunks</h3>
              {chunks.map((chunk, i) => (
                <div key={i} style={{ border: "1px solid #e0e0e0", borderRadius: 6, padding: 12, marginBottom: 8 }}>
                  <div style={{ fontSize: 12, color: "#888", marginBottom: 4 }}>
                    [{i + 1}] {chunk.metadata?.source} · score: {chunk.score?.toFixed(3)}
                  </div>
                  <p style={{ fontSize: 13, lineHeight: 1.5, margin: 0 }}>{chunk.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "evaluate" && (
        <div>
          <p style={{ color: "#666", fontSize: 14, marginBottom: 16 }}>
            Runs all 5 retrieval strategies against the labeled test set and computes Precision@K, Recall@K, and latency.
          </p>
          <button
            onClick={handleEval}
            disabled={loading}
            style={{ padding: "10px 24px", background: "#2A6FDB", color: "white", border: "none", borderRadius: 6, cursor: "pointer", fontWeight: 600, marginBottom: 20 }}
          >
            {loading ? "Running evaluation..." : "Run Evaluation"}
          </button>

          {evalError && (
            <div style={{ background: "#fff0f0", border: "1px solid #ffcccc", borderRadius: 6, padding: 12, marginBottom: 12, color: "#cc0000", fontSize: 14 }}>
              {evalError}
            </div>
          )}

          {evalResults && (
            <div>
              {Object.entries(evalResults).map(([key, data]) => (
                <div key={key} style={{ border: "1px solid #e0e0e0", borderRadius: 8, padding: 16, marginBottom: 12 }}>
                  <h3 style={{ fontWeight: 700, marginBottom: 8, textTransform: "capitalize" }}>{key}</h3>
                  <pre style={{ fontSize: 13, margin: 0, background: "#f8f9fa", padding: 10, borderRadius: 4 }}>{JSON.stringify(data, null, 2)}</pre>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "history" && (
        <div>
          {history.length === 0 && <p style={{ color: "#aaa", fontSize: 14 }}>No queries yet. Ask a question first.</p>}
          {history.map((item, i) => (
            <div key={i} style={{ border: "1px solid #e0e0e0", borderRadius: 8, padding: 16, marginBottom: 12 }}>
              <div style={{ fontSize: 12, color: "#888", marginBottom: 4 }}>
                {item.strategy} · {item.latency_ms?.toFixed(0)}ms · {item.created_at}
              </div>
              <p style={{ fontWeight: 600, marginBottom: 4 }}>{item.query}</p>
              <p style={{ fontSize: 13, color: "#444" }}>{item.answer?.slice(0, 200)}...</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
