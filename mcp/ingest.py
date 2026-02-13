import os
from pathlib import Path
import numpy as np
from dependencies import embed_text, get_collection
from dotenv import load_dotenv

load_dotenv()

DOCS_DIR = Path(os.getenv("DOCS_DIR", "./docs"))
CACHE_DIR = Path(os.getenv("CACHE_DIR", "./embeddings_cache"))
DOCS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

collection = get_collection()

def vectorize_file(file_path: Path):
    cache_file = CACHE_DIR / (file_path.stem + ".npy")
    if cache_file.exists():
        return  # Already vectorized
    text = file_path.read_text(encoding="utf-8")
    emb = embed_text(text)
    collection.add(
        ids=[file_path.stem],
        embeddings=[emb],
        documents=[text],
        metadatas=[{"path": str(file_path)}]
    )
    np.save(cache_file, emb)

def vectorize_all_docs():
    files = list(DOCS_DIR.glob("*.md"))
    for md_file in files:
        vectorize_file(md_file)
    print(f"Vectorized {len(files)} docs")

if __name__ == "__main__":
    vectorize_all_docs()
