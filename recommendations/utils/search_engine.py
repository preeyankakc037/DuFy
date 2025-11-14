# recommendations/utils/search_engine.py
import os
import torch
import pandas as pd
import torch.nn.functional as F

# ==============================
# Paths
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "test.csv")
EMB_PATH = os.path.join(BASE_DIR, "data", "music_embeddings.pt")

# ==============================
# Global singletons
# ==============================
_df = None
_embeddings = None
_model = None

# ==============================
# Lazy Load Resources
# ==============================
def load_resources():
    global _df, _embeddings, _model

    if _df is None:
        print("Loading dataset...")
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
        _df = pd.read_csv(DATA_PATH)
        required = {"music_name", "artist_name", "genre", "music_link"}
        missing = required - set(_df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

    if _model is None:
        print("Loading SentenceTransformer (lazy)...")
        # LAZY IMPORT — ONLY HERE!
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    if _embeddings is None:
        print("Loading float16 embeddings...")
        if not os.path.exists(EMB_PATH):
            raise FileNotFoundError(f"Embeddings not found: {EMB_PATH}")
        _embeddings = torch.load(EMB_PATH, map_location="cpu")
        _embeddings = _embeddings.to(torch.float16)
        _embeddings = F.normalize(_embeddings, dim=1)

    print(f"Loaded {_df.shape[0]} songs | Embeddings: {_embeddings.shape}")

# ==============================
# Search Function
# ==============================
def search_songs(query: str, top_k: int = 10):
    if not query.strip():
        return []

    load_resources()  # Ensures everything is loaded

    # Encode query
    query_emb = _model.encode(
        [query],
        convert_to_tensor=True,
        normalize_embeddings=True
    ).to(torch.float16)

    # Cosine similarity
    sims = torch.matmul(
        _embeddings.to(torch.float32),
        query_emb.to(torch.float32).T
    ).squeeze(1)

    # Top-K
    top_k = min(top_k, len(sims))
    indices = torch.topk(sims, k=top_k).indices.cpu().numpy()

    results = []
    for idx in indices:
        row = _df.iloc[idx]
        results.append({
            "music_name": str(row.get("music_name", "")),
            "artist_name": str(row.get("artist_name", "")),
            "genre": str(row.get("genre", "")),
            "music_link": str(row.get("music_link", ""))
        })

    return results

# ==============================
# Manual Reload
# ==============================
def reload_embeddings():
    global _df, _embeddings, _model
    print("Reloading resources...")
    _df = _embeddings = _model = None
    load_resources()
    print("Reload complete!")