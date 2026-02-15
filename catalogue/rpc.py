"""
JSON-RPC 2.0 over HTTP for MCP.
Single request/response and batch; optional streaming via NDJSON.
"""
import json
import logging
from typing import Any, Callable

logger = logging.getLogger("mcp.rpc")

JSONRPC_VERSION = "2.0"

# Standard JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def jsonrpc_error(code: int, message: str, data: Any = None) -> dict:
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": JSONRPC_VERSION, "error": err, "id": None}


def jsonrpc_result(result: Any, req_id: Any) -> dict:
    return {"jsonrpc": JSONRPC_VERSION, "result": result, "id": req_id}


def parse_request(body: bytes) -> tuple[dict | list | None, dict | None]:
    """Parse JSON body. Returns (parsed, error_response)."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        return None, jsonrpc_error(PARSE_ERROR, "Parse error", str(e))
    if data is None:
        return None, jsonrpc_error(INVALID_REQUEST, "Invalid Request")
    if isinstance(data, list):
        if len(data) == 0:
            return None, jsonrpc_error(INVALID_REQUEST, "Invalid Request")
        return data, None
    if isinstance(data, dict):
        return data, None
    return None, jsonrpc_error(INVALID_REQUEST, "Invalid Request")


def validate_single_request(req: dict) -> dict | None:
    """Validate single request object. Returns error response or None."""
    if not isinstance(req, dict):
        return jsonrpc_error(INVALID_REQUEST, "Invalid Request")
    if req.get("jsonrpc") != JSONRPC_VERSION:
        return jsonrpc_error(INVALID_REQUEST, "Invalid Request")
    method = req.get("method")
    if not isinstance(method, str) or not method:
        return jsonrpc_error(INVALID_REQUEST, "Invalid Request")
    return None


async def dispatch(
    method: str,
    params: dict | list | None,
    req_id: Any,
    handlers: dict[str, Callable],
) -> dict:
    """Dispatch to handler; returns JSON-RPC response dict."""
    if method not in handlers:
        return jsonrpc_error(METHOD_NOT_FOUND, "Method not found", method)
    handler = handlers[method]
    try:
        if isinstance(params, list):
            result = await handler(*params) if params else await handler()
        elif isinstance(params, dict):
            result = await handler(**params)
        else:
            result = await handler()
    except TypeError as e:
        logger.exception("Invalid params for %s", method)
        return jsonrpc_error(INVALID_PARAMS, "Invalid params", str(e))
    except Exception as e:
        logger.exception("Internal error in %s", method)
        return jsonrpc_error(INTERNAL_ERROR, "Internal error", str(e))
    return jsonrpc_result(result, req_id)


def is_notification(req: dict) -> bool:
    return "id" not in req or req["id"] is None
