from django.http import JsonResponse
from django.shortcuts import render
from .recommender import recommend_songs
from .models import Song
from typing import List, Dict
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse

def index(request):
    """
    Render the main page with top 10 songs by popularity_trend_score.
    Passes initial_tracks to the template.
    """
    # Fetch top 10 songs ordered by popularity_trend_score (descending)
    top_songs: List[Song] = Song.objects.order_by('-popularity_trend_score')[:10]

    # Prepare data for the template
    initial_tracks: List[Dict] = [
        {
            'music_name': song.music_name,
            'artist_name': song.artist_name or 'Unknown Artist',
            'genre': song.genre or 'Unknown Genre',
            'overlapping_emotions': song.overlapping_emotions or [],
            'music_link': song.music_link if song.music_link else 'No link available',
        }
        for song in top_songs
    ]

    return render(request, 'home.html', {'initial_tracks': initial_tracks})

def get_recommendations(request):
    """
    Return song recommendations as JSON based on a query parameter.
    Default query is 'music for a peaceful meditative song'.
    """
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    query: str = request.GET.get('query', 'music for a peaceful meditative song').strip()
    
    if not query:
        return JsonResponse({'error': 'Query cannot be empty'}, status=400)

    try:
        recommendations: List[Dict] = recommend_songs(query)
    except Exception as e:
        # Return clear error if something goes wrong in recommendation logic
        return JsonResponse({'error': f'Failed to generate recommendations: {str(e)}'}, status=500)

    return JsonResponse({'recommendations': recommendations})



class SignupView(TemplateView):
    template_name = 'signup.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Passwords don't match.")
            return render(request, 'signup.html')
        # Here you'd normally create a user with Django auth
        messages.success(request, f"Account created for {username}! (This is a demo.)")
        return redirect('signup')  # Redirect back to signup page for now
    
class PlaylistView(TemplateView):
    template_name = 'playlist.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'playlist.html', {'messages': messages.get_messages(request)})