import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dependencies import embed_text, get_collection, CHROMA_DB_DIR
from dotenv import load_dotenv

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

app = FastAPI(title="MCP RAG Retrieval Server")

@app.post("/retrieve")
async def retrieve_docs(req: Request):
    data = await req.json()
    query_text = data.get("query", "")
    logger.info("POST /retrieve query=%r", query_text)

    if not query_text:
        logger.warning("Missing query, returning 400")
        return JSONResponse({"error":"Missing query"}, status_code=400)

    logger.info("Computing query embedding...")
    query_emb = embed_text(query_text)
    dim = len(query_emb) if query_emb is not None else 0
    logger.info("Query embedding computed (dim=%d), requesting n_results=%d", dim, N_RESULTS)


    results = collection.query(
        query_embeddings=[query_emb],
        n_results=N_RESULTS
    )

    docs = results["documents"][0]
    ids = results["ids"][0]
    metas = results["metadatas"][0]
    num_returned = len(docs)
    logger.info("Chroma returned %d docs, ids=%s", num_returned, ids)

    payload = {"query": query_text, "results": [{"id": i, "meta": m, "text": d} for i, m, d in zip(ids, metas, docs)]}
    logger.info("Responding with %d results", num_returned)
    return payload
