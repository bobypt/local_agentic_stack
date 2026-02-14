# MCP RAG Retrieval Server

## 1️⃣ Setup

- Install dependencies (inside venv):

```bash
uv pip install fastapi uvicorn chromadb sentence-transformers python-dotenv numpy
````

* Configure `.env`:

```env
CHROMA_DB_DIR=./chroma_db
DOCS_DIR=./docs
EMBED_MODEL=../llm-mlx/qwen-embed-q4
N_RESULTS=3
HOST=0.0.0.0
PORT=8000
```

---

## 2️⃣ Step 1 — Vectorize Markdown KBs

```bash
uv run python ingest.py
```

* Reads `mcp/docs/*.md`
* Stores embeddings and docs in ChromaDB (idempotent: skips docs already in DB)

---

## 3️⃣ Step 2 — Start MCP Server

```bash
uv run uvicorn main:app --reload
```

* RAG endpoint: `POST /retrieve` (from project root: `make api` or `make start-mcp-server`)

---

## 4️⃣ Example: Query RAG

Request body is plain JSON with a `query` field (no JSON-RPC wrapper):

```bash
curl -X POST "http://localhost:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query": "what organic fruits do you have?"}'
```

Example response (top N docs, N from `N_RESULTS` in `.env`):

```json
{
  "query": "Explain transformer architecture",
  "results": [
    {"id": "file1", "meta": {"path": "mcp/docs/file1.md"}, "text": "..."},
    {"id": "file2", "meta": {"path": "mcp/docs/file2.md"}, "text": "..."}
  ]
}
```

* Missing or empty `query` returns `400` with `{"error": "Missing query"}`.

---

## Notes

* MCP is **LLM-free** → RAG retrieval only; use with a separate **LLM agent** for generation
* Fully local (ChromaDB + local embedding model)
* Use `N_RESULTS` in `.env` to control number of retrieved docs  

