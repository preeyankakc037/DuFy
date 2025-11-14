import os
import pandas as pd
from recommendations.models import Song

def load_songs_from_csv():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(BASE_DIR, "data", "test.csv")

    if not os.path.exists(csv_path):
        print(f"❌ CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print(f"📄 Loaded {len(df)} songs from CSV")

    for _, row in df.iterrows():
        song, created = Song.objects.get_or_create(
            music_name=row.get("music_name"),
            artist_name=row.get("artist_name"),
            defaults={
                "genre": row.get("genre", ""),
                "description": row.get("description", ""),
                "tags": row.get("tags", ""),
                "music_link": row.get("music_link", ""),
            },
        )
        if created:
            print(f"✅ Added: {song.music_name}")
        else:
            print(f"⚠️ Skipped (already exists): {song.music_name}")

    print("🎵 Song loading complete.")
