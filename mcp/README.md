# Full MCP JSON-RPC Server (RAG + Tools)

## 1️⃣ Setup

- Install dependencies (inside venv):

```bash
uv pip install fastapi uvicorn chromadb mlx-lm python-dotenv numpy
````

* Configure `.env`:

```env
CHROMA_DB_DIR=./chroma_db
DOCS_DIR=./docs
CACHE_DIR=./embeddings_cache
EMBED_MODEL=../llm-mlx/qwen-embed-q4
N_RESULTS=3
HOST=0.0.0.0
PORT=8000
```

---

## 2️⃣ Step 1 — Vectorize Markdown KBs

```bash
python mcp/ingest.py
```

* Reads `mcp/docs/*.md`
* Stores embeddings in ChromaDB
* Caches embeddings in `embeddings_cache/`

---

## 3️⃣ Step 2 — Start MCP Server

```bash
uv run mcp.main:app --reload
```

* JSON-RPC endpoint: `POST /rpc`

---

## 4️⃣ Example: Query RAG

```bash
curl -X POST "http://localhost:8000/rpc" \
-H "Content-Type: application/json" \
-d '{
  "jsonrpc": "2.0",
  "method": "query",
  "params": {"query":"Explain transformer architecture"},
  "id": 1
}'
```

* Returns top N documents (default N=3) with metadata:

```json
{
  "jsonrpc":"2.0",
  "id":1,
  "result":[
    {"id":"file1","meta":{"path":"mcp/docs/file1.md"},"text":"..."},
    {"id":"file2","meta":{"path":"mcp/docs/file2.md"},"text":"..."}
  ]
}
```

---

## 5️⃣ Example: Tool Calls

* **List docs**

```bash
curl -X POST "http://localhost:8000/rpc" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"list_docs","params":{},"id":2}'
```

* **Read a file**

```bash
curl -X POST "http://localhost:8000/rpc" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"read_file","params":{"path":"file1.md"},"id":3}'
```

* **Vectorize docs on-demand**

```bash
curl -X POST "http://localhost:8000/rpc" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"vectorize_docs","params":{},"id":4}'
```

---

## Notes

* MCP is **LLM-free** → only handles RAG + tools
* Fully local, memory-efficient, ready for integration with a separate **LLM agent**
* Supports JSON-RPC 2.0 standard
* Use `N_RESULTS` in `.env` to control number of retrieved docs

```

---

This setup gives you:

- **Step 1:** `ingest.py` → vectorizes all docs once  
- **Step 2:** `main.py` → full JSON-RPC 2.0 MCP server  
- **Tool registry** with `read_file`, `list_docs`, `vectorize_docs`  
- `.env` for all config paths  
- `docs/` inside MCP for self-contained KBs  
- CURL examples in README for **initialize, tools, and retrieval**  

