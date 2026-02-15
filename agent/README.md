# Support agent (ADK)

Support agent that checks **price and catalogue** by calling the MCP server (JSON-RPC 2.0). Follows the [poet](../../references/poet) pattern: single ADK `Agent` with one tool that calls the MCP server.

## Setup

1. **MCP server** must be running (catalogue RAG):

   ```bash
   make vectorise-data   # if needed
   make start-mcp-server # or make api
   ```

2. **Agent env** (optional): create `agent/.env` or export:

   - `MCP_BASE_URL` — MCP server URL (default `http://127.0.0.1:8000`)
   - `SUPPORT_AGENT_MODEL` — ADK model (default `gemini-2.0-flash-exp`)
   - Google ADK / Gemini API key as required by ADK

3. **Install and run** (from repo root or `agent/`):

   ```bash
   cd agent
   uv venv && . .venv/bin/activate
   uv pip install -r requirements.txt
   # Set GOOGLE_API_KEY or ADK auth; then run your ADK app/session with root_agent
   ```

## Usage

Import and use the agent in your ADK app:

```python
from agent import support_agent  # or root_agent

# Use support_agent in your ADK session / runner.
# The agent will call catalogue_retrieve(query, n_results) to look up products/prices on the MCP server.
```

The agent uses the **catalogue_retrieve** tool, which sends JSON-RPC 2.0 `retrieve` requests to the MCP server and returns catalogue results (e.g. product text and prices) to the LLM.
