from django.db import models

class Song(models.Model):
    music_name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    overlapping_emotions = models.CharField(max_length=255)
    lyrics = models.TextField(blank=True)
    pitch_tempo = models.CharField(max_length=100)
    description = models.TextField()
    music_link = models.URLField(blank=True)
    tags = models.CharField(max_length=255)
    duration = models.CharField(max_length=50)
    language = models.CharField(max_length=50)
    instrument_type = models.CharField(max_length=100)
    popularity_trend_score = models.FloatField()
    metric_source = models.CharField(max_length=100)
    license_typ = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self):
        return self.music_name