from django.db import models

# Create your models here.python manage.py makemigrations

class Music(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    mood = models.CharField(max_length=100)

    def __str__(self):
        return self.title
