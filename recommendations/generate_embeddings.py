# recommendations/generate_embeddings.py
import os, json, numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

BASE_DIR = os.path.dirname(__file__)
SONGS_FILE = os.path.join(BASE_DIR, "songs.json")
EMB_FILE = os.path.join(BASE_DIR, "song_embeddings.npy")
META_FILE = os.path.join(BASE_DIR, "songs_meta.json")

def load_songs():
    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_text_for_song(song):
    # combine title, artist, tags, and lyrics (if present) into one string
    parts = []
    for k in ("title", "artist", "tags", "lyrics"):
        v = song.get(k)
        if v:
            parts.append(str(v))
    return " | ".join(parts)

def main():
    songs = load_songs()
    corpus = [build_text_for_song(s) for s in songs]

    print("Loading model (this may download the model the first time)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Encoding corpus (this may take a while)...")
    embeddings = model.encode(corpus, show_progress_bar=True, convert_to_numpy=True)

    # Normalize embeddings so cosine similarity = dot product
    embeddings = normalize(embeddings)

    print(f"Saving embeddings to {EMB_FILE}")
    np.save(EMB_FILE, embeddings)

    # Save the songs meta (ensures indexes align)
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

    print("Done. You can now use the embeddings for similarity search.")

if __name__ == "__main__":
    main()
