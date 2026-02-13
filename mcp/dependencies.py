import os
from dotenv import load_dotenv
from chromadb import Client
from chromadb.config import Settings
from mlx_lm import generate_embedding

load_dotenv()

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
EMBED_MODEL = os.getenv("EMBED_MODEL", "../llm-mlx/qwen-embed-q4")

os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# Chroma DB client
chroma_client = Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=CHROMA_DB_DIR
))

def get_collection(name="docs"):
    return chroma_client.get_or_create_collection(name=name)

# Embedding helper
def embed_text(text: str):
    return generate_embedding(EMBED_MODEL, text)
