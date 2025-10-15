import pandas as pd
from recommendations.models import Song

# Load the preprocessed dataset
df = pd.read_csv('preprocessed_music_dataset.csv')

# Iterate over the DataFrame and create Song objects
for index, row in df.iterrows():
    Song.objects.create(
        music_name=row['music_name'],
        artist_name=row['artist_name'],
        genre=row['genre'],
        overlapping_emotions=row['overlapping_emotions'],
        lyrics=row['lyrics'],
        pitch_tempo=row['pitch_/_tempo'],
        description=row['description'],
        music_link=row['music_link'] if pd.notna(row['music_link']) else '',
        tags=row['tags'],
        duration=row['duration'],
        language=row['language'],
        instrument_type=row['instrument_type'],
        popularity_trend_score=float(row['popularity_/_trend_score']),
        metric_source=row['metric_source'],
        license_typ=row['license_typ'],
        text=row['text']
    )

print(f"Loaded {Song.objects.count()} songs into the database.")