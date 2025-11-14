# recommendations/utils/search_engine.py
import os
import torch
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch.nn.functional as F

# ==============================
# Paths
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "test.csv")
EMB_PATH = os.path.join(BASE_DIR, "data", "music_embeddings.pt")

# ==============================
# Global variables (singletons)
# ==============================
df = None
embeddings = None
model = None

# ==============================
# Load resources
# ==============================
def load_resources():
    """
    Load dataset, embeddings, and model once.
    Reuse globally for all searches.
    """
    global df, embeddings, model

    if df is None:
        print("🎵 Loading dataset...")
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Dataset file not found: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)

        # Ensure essential columns exist
        required_cols = {"music_name", "artist_name", "genre", "music_link"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise ValueError(f"Dataset is missing columns: {missing_cols}")

    if embeddings is None:
        print("🎵 Loading embeddings...")
        if not os.path.exists(EMB_PATH):
            raise FileNotFoundError(f"Embedding file not found: {EMB_PATH}")

        embeddings_loaded = torch.load(EMB_PATH, map_location="cpu")
        # Convert numpy array to tensor if needed
        if isinstance(embeddings_loaded, np.ndarray):
            embeddings_loaded = torch.from_numpy(embeddings_loaded)
        elif not isinstance(embeddings_loaded, torch.Tensor):
            raise TypeError("Embeddings must be a torch.Tensor or numpy.ndarray")

        # Normalize for cosine similarity
        embeddings = F.normalize(embeddings_loaded, dim=1)

    if model is None:
        print("🎵 Loading embedding model for queries...")
        model = SentenceTransformer("all-MiniLM-L6-v2")

    print(f"✅ Loaded {len(df)} songs and embeddings of shape {embeddings.shape}")

# ==============================
# Search Function
# ==============================
def search_songs(query: str, top_k: int = 10):
    """
    Search similar songs using cosine similarity between query and dataset embeddings.
    Lazy-loads resources if not already loaded.
    """
    load_resources()  # Ensures embeddings, df, and model are loaded

    if not query:
        return []

    # Encode query to vector
    query_embedding = model.encode([query], convert_to_tensor=True)
    query_embedding = F.normalize(query_embedding, dim=1)

    # Compute cosine similarity
    similarities = torch.matmul(embeddings, query_embedding.T).squeeze(1)

    # Get top-k most similar
    top_k_indices = torch.topk(similarities, k=min(top_k, len(similarities))).indices

    results = []
    for idx in top_k_indices:
        idx = idx.item()
        row = df.iloc[idx]
        results.append({
            "music_name": row.get("music_name", ""),
            "artist_name": row.get("artist_name", ""),
            "genre": row.get("genre", ""),
            "music_link": row.get("music_link", ""),
        })

    return results

# ==============================
# Manual reload (optional)
# ==============================
def reload_embeddings():
    """
    Manually reload dataset and embeddings if they are updated.
    """
    global df, embeddings, model
    print("🔄 Reloading dataset and embeddings...")
    df = None
    embeddings = None
    model = None
    load_resources()
    print("✅ Reload complete!")
