import logging
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv

from dependencies import embed_text, get_collection, CHROMA_DB_DIR
from rpc import (
    JSONRPC_VERSION,
    parse_request,
    validate_single_request,
    dispatch,
    is_notification,
    jsonrpc_error,
    INVALID_REQUEST,
)

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("mcp")
logger.info("Chroma DB path: %s", CHROMA_DB_DIR)

DOCS_DIR = os.getenv("DOCS_DIR", "./docs")
N_RESULTS = int(os.getenv("N_RESULTS", 3))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

collection = get_collection()
try:
    coll_count = collection.count()
except Exception as e:
    coll_count = -1
    logger.warning("Could not get collection count: %s", e)
logger.info("Collection 'docs' loaded: %d documents (if 0, run: make vectorise-data)", coll_count)

app = FastAPI(title="MCP JSON-RPC 2.0 Server (RAG Catalogue)")


# ---------- JSON-RPC method handlers ----------

async def retrieve(query: str, n_results: int | None = None) -> dict[str, Any]:
    """Search the catalogue by semantic query. Returns matching docs with id, meta, text."""
    if not query or not query.strip():
        raise ValueError("Missing or empty query")
    n = n_results if n_results is not None else N_RESULTS
    n = max(1, min(n, 100))
    query_emb = embed_text(query.strip())
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=n,
    )
    docs = results["documents"][0]
    ids = results["ids"][0]
    metas = results["metadatas"][0]
    return {
        "query": query.strip(),
        "results": [
            {"id": i, "meta": m, "text": d}
            for i, m, d in zip(ids, metas, docs)
        ],
    }


async def tools_list() -> dict[str, Any]:
    """List available JSON-RPC methods (MCP tools)."""
    return {
        "methods": [
            {
                "name": "retrieve",
                "description": "Search the catalogue by semantic query. Returns matching documents (e.g. products, prices).",
                "params": {
                    "query": {"type": "string", "description": "Natural language query (e.g. product name, category, price)"},
                    "n_results": {"type": "integer", "description": "Max number of results (default from env N_RESULTS)"},
                },
            },
            {
                "name": "tools/list",
                "description": "List available RPC methods.",
                "params": {},
            },
        ],
    }


RPC_HANDLERS = {
    "retrieve": retrieve,
    "tools/list": tools_list,
}


# ---------- JSON-RPC 2.0 endpoint ----------

@app.post("/rpc")
async def rpc(request: Request):
    """
    JSON-RPC 2.0 endpoint. Single request or batch (array of requests).
    Body: {"jsonrpc":"2.0","method":"retrieve","params":{"query":"..."},"id":1}
    """
    body = await request.body()
    parsed, parse_err = parse_request(body)
    if parse_err is not None:
        return JSONResponse(parse_err, status_code=200)

    # Single request
    if isinstance(parsed, dict):
        err = validate_single_request(parsed)
        if err is not None:
            return JSONResponse(err, status_code=200)
        if is_notification(parsed):
            return JSONResponse(content=None, status_code=204)
        method = parsed.get("method")
        params = parsed.get("params")
        req_id = parsed.get("id")
        response = await dispatch(method, params, req_id, RPC_HANDLERS)
        return JSONResponse(response, status_code=200)

    # Batch
    responses = []
    for req in parsed:
        err = validate_single_request(req)
        if err is not None:
            responses.append(err)
            continue
        if is_notification(req):
            continue
        method = req.get("method")
        params = req.get("params")
        req_id = req.get("id")
        resp = await dispatch(method, params, req_id, RPC_HANDLERS)
        responses.append(resp)
    if not responses:
        return JSONResponse(content=None, status_code=204)
    return JSONResponse(responses, status_code=200)


# ---------- Streamable JSON-RPC (NDJSON) ----------

@app.post("/rpc/stream")
async def rpc_stream(request: Request):
    """
    JSON-RPC 2.0 over NDJSON: one request per line, stream back one response per line.
    Content-Type: application/x-ndjson for both request and response.
    """
    body = await request.body()
    # Accept single line (one JSON object) or multiple lines
    lines = body.decode("utf-8").strip().split("\n")
    if not lines or (len(lines) == 1 and not lines[0].strip()):
        return JSONResponse(
            jsonrpc_error(INVALID_REQUEST, "Invalid Request"),
            status_code=200,
        )

    async def generate():
        import json
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parsed, parse_err = parse_request(line.encode("utf-8"))
            if parse_err is not None:
                yield json.dumps(parse_err) + "\n"
                continue
            if not isinstance(parsed, dict):
                yield json.dumps(jsonrpc_error(INVALID_REQUEST, "Invalid Request")) + "\n"
                continue
            err = validate_single_request(parsed)
            if err is not None:
                yield json.dumps(err) + "\n"
                continue
            if is_notification(parsed):
                continue
            method = parsed.get("method")
            params = parsed.get("params")
            req_id = parsed.get("id")
            response = await dispatch(method, params, req_id, RPC_HANDLERS)
            yield json.dumps(response) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        status_code=200,
    )


# ---------- Legacy plain POST (optional) ----------

@app.post("/retrieve")
async def retrieve_legacy(request: Request):
    """Legacy: plain JSON { \"query\": \"...\" }. Prefer POST /rpc with method \"retrieve\"."""
    data = await request.json()
    query_text = data.get("query", "")
    if not query_text:
        return JSONResponse({"error": "Missing query"}, status_code=400)
    result = await retrieve(query=query_text)
    return result
