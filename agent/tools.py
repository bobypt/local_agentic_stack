"""
Tools for the support agent: call MCP server (JSON-RPC 2.0) for catalogue lookup.
"""
import os
import json
import logging

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger("agent.tools")

MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://127.0.0.1:8000")


def catalogue_retrieve(query: str, n_results: int = 5) -> str:
    """
    Look up products and prices in the catalogue. Use this when the user asks
    about price, availability, or what products exist. Search by product name,
    category, or natural language (e.g. "organic fruits", "cheapest apples").

    Args:
        query: Natural language search (e.g. product name, category, or "price of X").
        n_results: Maximum number of catalogue entries to return (default 5).
    """
    if not query or not str(query).strip():
        return "Error: query is required."
    url = f"{MCP_BASE_URL.rstrip('/')}/rpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "retrieve",
        "params": {"query": str(query).strip(), "n_results": max(1, min(int(n_results), 20))},
        "id": 1,
    }
    try:
        if httpx is None:
            import urllib.request
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        else:
            with httpx.Client(timeout=30) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
    except Exception as e:
        logger.exception("MCP retrieve failed")
        return f"Error calling catalogue: {e}"
    if "error" in data:
        err = data["error"]
        return f"Catalogue error: {err.get('message', 'Unknown')}"
    result = data.get("result", {})
    results = result.get("results", [])
    if not results:
        return "No matching products or prices found in the catalogue for that query."
    lines = [f"**Catalogue results for \"{result.get('query', query)}\"**\n"]
    for r in results:
        text = (r.get("text") or "").strip()
        doc_id = r.get("id", "")
        if text:
            lines.append(f"- [{doc_id}]\n{text}")
    return "\n\n".join(lines)
