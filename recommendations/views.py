import logging
import os
import random
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils.search_engine import search_songs

logger = logging.getLogger(__name__)

# =========================================
# 📂 LOAD DATASET
# =========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "recommendations", "data", "test.csv")

try:
    dataset = pd.read_csv(DATASET_PATH)
    dataset.fillna("", inplace=True)
    logger.info(f"Dataset loaded successfully with {len(dataset)} rows.")
except Exception as e:
    dataset = pd.DataFrame()
    logger.error(f"Error loading dataset: {e}")

# =========================================
# 🔍 RECOMMENDATION API
# =========================================
def get_recommendations(request):
    query = request.GET.get("query", "").strip().lower()

    # ✅ Case 1: No query or "popular" → return 10 songs across genres
    if not query or query in ["popular", "default", ""]:
        if dataset.empty:
            return JsonResponse({"recommendations": []}, status=200)

        songs_by_genre = []
        grouped = dataset.groupby("genre")

        # Pick 1 random from each genre (up to 10)
        for genre, group in grouped:
            if not group.empty:
                songs_by_genre.append(group.sample(1).to_dict(orient="records")[0])
            if len(songs_by_genre) >= 10:
                break

        # Fill remaining if needed
        if len(songs_by_genre) < 10:
            remaining = dataset.sample(10 - len(songs_by_genre)).to_dict(orient="records")
            songs_by_genre.extend(remaining)

        return JsonResponse({"recommendations": songs_by_genre}, safe=False)

    # ✅ Case 2: Normal search
    try:
        results = search_songs(query)
        return JsonResponse({"recommendations": results}, safe=False)
    except Exception as e:
        logger.exception(f"Recommendation error: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)

# =========================================
# 🎧 SEARCH API
# =========================================
@api_view(['GET'])
def search_api(request):
    query = request.GET.get('query', '').strip()

    if not query:
        # Return random 10 if no query
        if not dataset.empty:
            random_songs = dataset.sample(min(10, len(dataset))).to_dict(orient="records")
            return Response({"results": random_songs})
        return Response({"results": []})

    try:
        results = search_songs(query, top_k=20)
        return Response({"results": results})
    except Exception as e:
        logger.exception(f"Search error: {str(e)}")
        return Response({"error": "Search failed"}, status=500)

# =========================================
# 🌐 PAGE VIEWS
# =========================================
def discover_view(request):
    """Render the Discover page with default recommendations."""
    if dataset.empty:
        songs = []
    else:
        songs_by_genre = []
        grouped = dataset.groupby("genre")

        for genre, group in grouped:
            if not group.empty:
                songs_by_genre.append(group.sample(1).to_dict(orient="records")[0])
            if len(songs_by_genre) >= 10:
                break

        if len(songs_by_genre) < 10:
            extra = dataset.sample(10 - len(songs_by_genre)).to_dict(orient="records")
            songs_by_genre.extend(extra)

        songs = songs_by_genre

    return render(request, 'discover.html', {"songs": songs})


def genre_view(request):
    return render(request, 'genre.html')


def top_charts_view(request):
    return render(request, 'top_charts.html')


def trending_view(request):
    return render(request, 'trending.html')


def favourites_view(request):
    return render(request, 'favourites.html')


def playlist_view(request):
    return render(request, 'playlist.html')


def signup_view(request):
    return render(request, 'signup.html')
