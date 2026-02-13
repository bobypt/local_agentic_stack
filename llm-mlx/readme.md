# Running local LLM with MLX on Apple Silicon (M3 16GB)

This guide shows how to:

* Install dependencies using `uv`
* Download Llama 3.1 8B / Qwen
* Convert to MLX format
* Quantize to 4-bit
* Run locally on Apple Silicon

Works well on 16GB unified memory (M3/M2/M1).

---

## Model Used

We’ll use:

**Meta Llama 3.1 8B Instruct**

Hosted on:

**Hugging Face**

ML runtime:

**MLX**

---

# 1. Install uv (if not installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal after install.

---

# 2. Create Project

```bash
mkdir llm-mlx
cd llm-mlx

uv venv
source .venv/bin/activate
```

---

# 3. Install MLX + MLX-LM

```bash
uv pip install mlx mlx-lm
```

Verify install:

```bash
python -c "import mlx; print('MLX installed')"
```

---

# 4. Get Hugging Face Token

1. Create account on Hugging Face
2. Go to Settings → Access Tokens
3. Create a **Read** token
4. Accept the Llama 3.1 license on the model page

Export token:

```bash
export HF_TOKEN=hf_your_token_here
```

(Optional) Add to `~/.zshrc` for persistence.

---

# 5. Download + Convert to MLX Format

```bash
# llama3.1_8B
mlx_lm.convert \
  --hf-path meta-llama/Meta-Llama-3.1-8B-Instruct \
  --mlx-path ./llama3.1-mlx

mlx_lm.convert \
  --hf-path Qwen/Qwen2.5-7B-Instruct \
  --mlx-path ./qwen-mlx  
```

This will:

* Authenticate
* Download model weights
* Convert to MLX format

---

# 6. Quantize (Recommended for 16GB)

Use 4-bit quantization with `mlx_lm convert` and `-q`:

**From existing MLX model** (e.g. after step 5):

```bash
cd llm-mlx
source .venv/bin/activate

cd llm-mlx
   source .venv/bin/activate
   python -m mlx_lm convert --hf-path ./qwen-mlx --mlx-path ./qwen-q4 -q --q-bits 4


```


Expected model size:
~4–5GB

This leaves room for:

* Context window
* macOS
* Other apps

---

# 7. Run Chat

```bash
mlx_lm.chat --model ./llama3.1-q4

mlx_lm.chat --model ./qwen-q4


```

Or single prompt:

```bash
mlx_lm.generate \
  --model ./llama3.1-q4 \
  --prompt "Explain transformer architecture simply"

mlx_lm.generate \
  --model ./qwen-q4 \
  --prompt "Explain transformer architecture simply"  
```

---

# Recommended Settings for M3 16GB

| Setting        | Value |
| -------------- | ----- |
| Quantization   | 4-bit |
| Context Length | 4096  |
| Temperature    | 0.7   |
| Top-p          | 0.9   |

---

# Performance Expectations (M3 16GB)

* ~25–45 tokens/sec
* Smooth interactive chat
* No swap if memory is free

Close heavy apps for best performance.

---

# Folder Structure After Setup

```
llama-mlx/
│
├── llama3.1-mlx/      # Converted MLX model
├── llama3.1-q4/       # Quantized model (used for inference)
└── .venv/
```



---

# Notes

* Always use the **Instruct** version for chat.
* 8-bit works, but 4-bit is optimal for 16GB machines.
* Larger models (14B+) are not recommended on 16GB.




## Download embedding model

```bash

uv pip install huggingface_hub

hf download sentence-transformers/all-MiniLM-L6-v2 --local-dir ./qwen-embed-q4


```
