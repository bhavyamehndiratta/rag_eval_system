// Shapes of the data exchanged with the FastAPI backend.

export type Strategy = 'semantic' | 'bm25' | 'hybrid' | 'reranked' | 'hyde';

export type Tab = 'ask' | 'evaluate' | 'history';

/** Body sent to POST /generate. */
export interface GenerateRequest {
  query: string;
  strategy: Strategy;
  k: number;
  alpha: number;
}

/** A retrieved chunk used as context for the answer. */
export interface Chunk {
  id?: string;
  text: string;
  metadata?: { source?: string; [key: string]: unknown };
  score?: number;
}

/** Response from POST /generate. */
export interface GenerateResponse {
  query: string;
  answer: string;
  chunks_used: Chunk[];
}

/** Response from POST /evaluate: metrics keyed by strategy name. */
export type EvalResults = Record<string, unknown>;

/** One row from GET /history. */
export interface HistoryItem {
  id?: number;
  query: string;
  strategy: string;
  answer?: string;
  latency_ms?: number;
  created_at?: string;
}

/** Error body FastAPI returns on a failed request. */
export interface ApiErrorBody {
  detail?: string;
}
