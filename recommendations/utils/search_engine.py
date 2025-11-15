# recommendations/utils/search_engine.py
import os
import torch
import pandas as pd
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

# ==============================
# Paths
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "test.csv")
EMB_PATH = os.path.join(BASE_DIR, "data", "music_embeddings.pt")

# ==============================
# Global variables
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

    # -------------------------
    # Load dataset
    # -------------------------
    if df is None:
        print("🎵 Loading dataset...")
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Dataset file not found: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)

        required_cols = {"music_name", "artist_name", "genre", "music_link"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise ValueError(f"Dataset is missing columns: {missing_cols}")

    # -------------------------
    # Load embeddings
    # -------------------------
    if embeddings is None:
        print("📦 Loading precomputed embeddings (float16)...")
        loaded = torch.load(EMB_PATH, map_location="cpu")
        if not isinstance(loaded, torch.Tensor):
            loaded = torch.from_numpy(loaded)
        embeddings = F.normalize(loaded.to(torch.float16), dim=1)

    # -------------------------
    # Load model (quantized)
    # -------------------------
    if model is None:
        print("🤖 Loading all-MiniLM-L6-v2 model with dynamic quantization...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        model = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear}, dtype=torch.qint8
        )

    print(f"✅ Loaded {len(df)} songs and embeddings of shape {embeddings.shape}")


# ==============================
# Search function
# ==============================
def search_songs(query: str, top_k: int = 10):
    """
    Search similar songs using cosine similarity between query and dataset embeddings.
    Lazy-loads resources if not already loaded.
    """
    load_resources()

    if not query:
        return []

    # Encode query using full transformer (quantized)
    query_embedding = model.encode(
        [query],
        convert_to_tensor=True,
        normalize_embeddings=True
    )
    query_embedding = query_embedding.to(torch.float16)  # save memory

    # Cosine similarity with embeddings on CPU
    similarities = torch.matmul(
        embeddings.to(torch.float32),
        query_embedding.to(torch.float32).T
    ).squeeze(1)

    # Get top-k results
    top_idx = torch.topk(similarities, k=min(top_k, len(similarities))).indices.tolist()

    results = []
    for i in top_idx:
        row = df.iloc[int(i)]
        results.append({
            "music_name": row.get("music_name", ""),
            "artist_name": row.get("artist_name", ""),
            "genre": row.get("genre", ""),
            "music_link": row.get("music_link", "")
        })

    return results


# ==============================
# Manual reload (optional)
# ==============================
def reload_embeddings():
    """
    Manually reload dataset, embeddings, and model if they are updated.
    """
    global df, embeddings, model
    print("🔄 Reloading dataset, embeddings, and model...")
    df = None
    embeddings = None
    model = None
    load_resources()
    print("✅ Reload complete!")
