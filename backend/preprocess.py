import pandas as pd
import re
from sentence_transformers import SentenceTransformer
import torch

# Load dataset
df = pd.read_csv('DuFy_cleaned.csv')

# Skip fully empty rows if any
df = df.dropna(how='all')

# Standardize column names: strip spaces, lowercase, replace spaces with underscores
df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

# Print column names to verify
print("Standardized columns in dataset:", df.columns.tolist())

# Handle missing values
df['lyrics'] = df['lyrics'].fillna('nan')
df['overlapping_emotions'] = df['overlapping_emotions'].fillna('')
df['description'] = df['description'].fillna('')
df['genre'] = df['genre'].fillna('Unknown')
df['language'] = df['language'].fillna('None')
df['instrument_type'] = df['instrument_type'].fillna('Unknown')
df['popularity_/_trend_score'] = df['popularity_/_trend_score'].fillna(1.0)
df['license_typ'] = df['license_typ'].fillna('Requires License')  # Changed to 'license_typ'

# Create combined 'text' field for NLP (per DUFy workflow)
df['text'] = df['lyrics'] + ' ' + df['overlapping_emotions'] + ' ' + df['description']

# Clean text (lowercase, remove punctuation)
df['text'] = df['text'].apply(lambda x: re.sub(r'[^\w\s]', '', x.lower()))

# Save preprocessed dataset
df.to_csv('preprocessed_music_dataset.csv', index=False)

# Generate embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['text'].tolist(), convert_to_tensor=True)

# Save embeddings
torch.save(embeddings, 'music_embeddings.pt')

print(f"Dataset shape: {df.shape}")
print(f"Embeddings shape: {embeddings.shape}")