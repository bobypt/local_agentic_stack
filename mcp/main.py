import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dependencies import embed_text, get_collection
from dotenv import load_dotenv

load_dotenv()

DOCS_DIR = os.getenv("DOCS_DIR", "./docs")
N_RESULTS = int(os.getenv("N_RESULTS", 3))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

collection = get_collection()

app = FastAPI(title="MCP RAG Retrieval Server")

@app.post("/retrieve")
async def retrieve_docs(req: Request):
    data = await req.json()
    query_text = data.get("query", "")
    if not query_text:
        return JSONResponse({"error":"Missing query"}, status_code=400)

    query_emb = embed_text(query_text)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=N_RESULTS
    )

    docs = results["documents"][0]  # list of retrieved docs
    ids = results["ids"][0]
    metas = results["metadatas"][0]

    return {"query": query_text, "results": [{"id": i, "meta": m, "text": d} for i, m, d in zip(ids, metas, docs)]}
