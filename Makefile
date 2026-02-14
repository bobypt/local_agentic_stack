.PHONY: install llm-convert llm-quantize llm-run web api dev vectorise-data start-mcp-server clean

LLM_DIR := llm-mlx
CONVERT_SENTINEL := $(LLM_DIR)/qwen-mlx/.done
QUANTIZE_SENTINEL := $(LLM_DIR)/qwen-q4/.done

# -------- INSTALL --------
install:
	cd $(LLM_DIR) && (test -d .venv || uv venv) && . .venv/bin/activate && uv pip install mlx mlx-lm

# -------- LLM --------
$(CONVERT_SENTINEL):
	cd $(LLM_DIR) && . .venv/bin/activate && python -m mlx_lm convert \
		--hf-path Qwen/Qwen2.5-7B-Instruct \
		--mlx-path ./qwen-mlx && touch qwen-mlx/.done

llm-convert: $(CONVERT_SENTINEL)

# Quantize existing MLX model to 4-bit (uses convert with -q on local path)
$(QUANTIZE_SENTINEL): $(CONVERT_SENTINEL)
	cd $(LLM_DIR) && . .venv/bin/activate && python -m mlx_lm convert \
		--hf-path ./qwen-mlx \
		--mlx-path ./qwen-q4 \
		-q --q-bits 4 && touch qwen-q4/.done

llm-quantize: $(QUANTIZE_SENTINEL)

llm-run: llm-quantize
	cd $(LLM_DIR) && . .venv/bin/activate && python -m mlx_lm server \
		--model ./qwen-q4 \
		--port 8001

# -------- VECTORISE DATA (MCP ingest) --------
vectorise-data:
	cd mcp && (test -d .venv || uv venv) && . .venv/bin/activate && \
	uv pip install fastapi uvicorn chromadb sentence-transformers python-dotenv numpy && \
	uv run python ingest.py

# -------- WEB --------
web:
	cd web && npm run dev

# -------- MCP server (RAG) --------
start-mcp-server: vectorise-data
	cd mcp && . .venv/bin/activate && uv run uvicorn main:app --reload

# -------- FULL DEV --------
dev:
	make -j3 llm-run start-mcp-server
