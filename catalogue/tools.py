from tools import TOOLS

if __name__ == "__main__":
    """Step 1: Vectorize all markdown files and store embeddings in Chroma."""
    result = TOOLS["vectorize_docs"]()
    print(result)
