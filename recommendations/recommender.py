import torch
from sentence_transformers import SentenceTransformer
from recommendations.models import Song
import numpy as np

# Load the precomputed embeddings
embeddings = torch.load('c:/Users/ASUS/Desktop/DuFy/music_embeddings.pt')
print(f"Embeddings shape: {embeddings.shape}")

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def recommend_songs(query, top_k=5):
    # Generate embedding for the query
    query_embedding = model.encode(query, convert_to_tensor=True)
    print(f"Query embedding shape: {query_embedding.shape}")
    
    # Compute cosine similarity
    similarities = torch.nn.functional.cosine_similarity(query_embedding.unsqueeze(0), embeddings)
    print(f"Similarities shape: {similarities.shape}")
    
    # Get all songs and convert to list
    all_songs = list(Song.objects.all())
    song_ids = [song.id for song in all_songs]
    top_k_indices = similarities.argsort(descending=True)[:top_k].tolist()
    valid_indices = [i for i in top_k_indices if i < len(song_ids)]
    
    # Retrieve the corresponding songs
    recommended_songs = []
    for idx in valid_indices[:top_k]:
        if idx < len(all_songs):
            recommended_songs.append(all_songs[idx])
    print(f"Number of recommended songs: {len(recommended_songs)}")
    print(f"Recommendations raw: {[(song.music_name, song.overlapping_emotions) for song in recommended_songs]}")  # Debug: Print raw data
    
    # Return a list of dictionaries with song details
    return [
        {
            'music_name': song.music_name,
            'artist_name': song.artist_name,
            'genre': song.genre,
            'overlapping_emotions': song.overlapping_emotions,
            'music_link': song.music_link if song.music_link else 'No link available',
            'similarity_score': float(similarities[valid_indices.index(i)].item()) if i in valid_indices else 0.0  # Use valid_indices to map similarity
        }
        for i, song in enumerate(recommended_songs)
    ]

if __name__ == "__main__":
    query = "music for a peaceful meditative song"
    recommendations = recommend_songs(query)
    for rec in recommendations:
        print(f"Song: {rec['music_name']} by {rec['artist_name']} - Emotions: {rec['overlapping_emotions']} - Score: {rec['similarity_score']:.4f}")