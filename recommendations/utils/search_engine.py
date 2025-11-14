# recommendations/utils/search_engine.py
import os
import torch
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch.nn.functional as F
from sklearn.metrics.pairwise import cosine_similarity
# ==============================
# Paths
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "test.csv")
EMB_PATH = os.path.join(BASE_DIR, "data", "music_embeddings.pt")

# ==============================
# Load dataset and embeddings
# ==============================
print("🎵 Loading dataset and embeddings...")

# Load dataset
df = pd.read_csv(DATA_PATH)
embeddings = torch.load(EMB_PATH, map_location="cpu")
# Check for essential columns
required_cols = {"music_name", "artist_name", "genre", "music_link"}
missing_cols = required_cols - set(df.columns)
if missing_cols:
    raise ValueError(f"Dataset is missing columns: {missing_cols}")

# Load embeddings (Tensor)
if not os.path.exists(EMB_PATH):
    raise FileNotFoundError(f"❌ Embedding file not found: {EMB_PATH}")

embeddings = torch.load(EMB_PATH)
if isinstance(embeddings, np.ndarray):
    embeddings = torch.from_numpy(embeddings)
elif not isinstance(embeddings, torch.Tensor):
    raise TypeError("Embeddings must be a torch.Tensor or numpy.ndarray")

embeddings = F.normalize(embeddings, dim=1)  # normalize for cosine similarity

# Load embedding model for queries
model = SentenceTransformer("all-MiniLM-L6-v2")

print(f"✅ Loaded {len(df)} songs and embeddings of shape {embeddings.shape}")

# ==============================
# Search Function
# ==============================
def search_songs(query: str, top_k: int = 10):
    """
    Search similar songs using cosine similarity between query and dataset embeddings
    """
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
