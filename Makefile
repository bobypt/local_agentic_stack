.PHONY: install llm-convert llm-quantize llm-run web api dev clean

# -------- WEB --------
web:
	cd web && npm run dev

# -------- API --------
api:
	cd api && npm run dev

# -------- FULL DEV --------
dev:
	make -j3 llm-run web api
