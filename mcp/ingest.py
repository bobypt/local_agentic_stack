import os
from pathlib import Path
from dependencies import embed_text, get_collection
from dotenv import load_dotenv

load_dotenv()

DOCS_DIR = Path(os.getenv("DOCS_DIR", "./docs"))
DOCS_DIR.mkdir(parents=True, exist_ok=True)

collection = get_collection()

def vectorize_file(file_path: Path):
    doc_id = file_path.stem
    # Skip if already in Chroma (single source of truth)
    existing = collection.get(ids=[doc_id], include=[])
    if existing["ids"]:
        return
    text = file_path.read_text(encoding="utf-8")
    emb = embed_text(text)
    collection.add(
        ids=[doc_id],
        embeddings=[emb],
        documents=[text],
        metadatas=[{"path": str(file_path)}]
    )

def vectorize_all_docs():
    files = list(DOCS_DIR.glob("*.md"))
    for md_file in files:
        vectorize_file(md_file)
    print(f"Vectorized {len(files)} docs")

if __name__ == "__main__":
    vectorize_all_docs()
