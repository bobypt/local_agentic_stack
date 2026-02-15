import os
from pathlib import Path
from dotenv import load_dotenv
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

load_dotenv()

# Resolve Chroma path relative to this file (mcp/) so ingest and server use the same DB
_MCP_DIR = Path(__file__).resolve().parent
_chroma_default = _MCP_DIR / "chroma_db"
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", str(_chroma_default))
if not Path(CHROMA_DB_DIR).is_absolute():
    CHROMA_DB_DIR = str(_MCP_DIR / CHROMA_DB_DIR)
# Local path or HuggingFace model name for sentence-transformers
EMBED_MODEL = os.getenv("EMBED_MODEL", "/Users/boby/repos/local_agentic_stack/llm-mlx/qwen-embed-q4")

os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# Chroma DB client (PersistentClient is the current API for local persistence)
chroma_client = PersistentClient(path=CHROMA_DB_DIR)

_embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)


def get_collection(name="docs"):
    return chroma_client.get_or_create_collection(name=name, embedding_function=_embed_fn)


def embed_text(text: str):
    """Return embedding vector for text (list of floats)."""
    return _embed_fn([text])[0]
