from sentence_transformers import SentenceTransformer, util
import json

# Load songs
def load_songs():
    with open("songs.json", "r") as f:
        return json.load(f)

# Recommend songs
def recommend_songs(description, top_k=5):
    songs = load_songs()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Encode all song tags
    song_embeddings = model.encode([song["tags"] for song in songs], convert_to_tensor=True)
    
    # Encode user description
    desc_embedding = model.encode(description, convert_to_tensor=True)
    
    # Compute cosine similarities
    scores = util.cos_sim(desc_embedding, song_embeddings)[0]
    
    # Get top k scores
    top_results = scores.topk(k=top_k)
    
    recommended = [songs[idx]["title"] for idx in top_results[1].tolist()]
    return recommended
