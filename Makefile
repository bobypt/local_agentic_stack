.PHONY: install llm-convert llm-quantize llm-run web api dev clean

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

# -------- WEB --------
web:
	cd web && npm run dev

# -------- API --------
api:
	cd api && npm run dev

# -------- FULL DEV --------
dev:
	make -j3 llm-run web api
