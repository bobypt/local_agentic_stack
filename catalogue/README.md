# MCP JSON-RPC 2.0 Server (RAG Catalogue)

HTTP server exposing catalogue/RAG over **JSON-RPC 2.0**: single or batch requests, plus streamable NDJSON.

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

* Reads `catalogue/docs/*.md`
* Stores embeddings and docs in ChromaDB (idempotent: skips docs already in DB)

---

## 3️⃣ Step 2 — Start MCP Server

```bash
uv run uvicorn main:app --reload
```

* **JSON-RPC 2.0:** `POST /rpc` (from project root: `make api` or `make start-mcp-server`)
* **Streamable:** `POST /rpc/stream` (NDJSON: one request per line, one response per line)

---

## 4️⃣ JSON-RPC 2.0: Query catalogue

**Single request** — `POST /rpc`:

```bash
curl -X POST "http://localhost:8000/rpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"retrieve","params":{"query":"what organic fruits do you have?"},"id":1}'
```

Example response:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "query": "what organic fruits do you have?",
    "results": [
      {"id": "grocery-products", "meta": {"path": "..."}, "text": "..."}
    ]
  },
  "id": 1
}
```

**List methods** — `tools/list`:

```bash
curl -X POST "http://localhost:8000/rpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}'
```

**Streamable** — `POST /rpc/stream` (body and response: one JSON object per line, NDJSON):

```bash
echo '{"jsonrpc":"2.0","method":"retrieve","params":{"query":"apples"},"id":1}' | \
  curl -X POST "http://localhost:8000/rpc/stream" \
    -H "Content-Type: application/x-ndjson" \
    -d @-
```

**Legacy** — plain JSON (no JSON-RPC): `POST /retrieve` with body `{"query": "..."}` still works.

---

## Notes

* MCP is **LLM-free** → RAG retrieval only; use with a separate **LLM agent** for generation
* Fully local (ChromaDB + local embedding model)
* Use `N_RESULTS` in `.env` to control number of retrieved docs  

