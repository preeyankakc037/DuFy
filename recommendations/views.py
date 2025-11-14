# recommendations/views.py
import logging
import os
import random
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# =========================================
# LOAD DATASET (STATIC, NO ML)
# =========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "recommendations", "data", "test.csv")

try:
    dataset = pd.read_csv(DATASET_PATH)
    dataset.fillna("", inplace=True)
    logger.info(f"Dataset loaded: {len(dataset)} songs")
except Exception as e:
    dataset = pd.DataFrame()
    logger.error(f"Failed to load dataset: {e}")

# =========================================
# RECOMMENDATION API (LAZY SEARCH)
# =========================================
def get_recommendations(request):
    query = request.GET.get("query", "").strip().lower()

    # No query → return diverse popular songs
    if not query or query in ["popular", "default", ""]:
        if dataset.empty:
            return JsonResponse({"recommendations": []})

        songs = []
        for genre, group in dataset.groupby("genre"):
            if not group.empty and len(songs) < 10:
                songs.append(group.sample(1).to_dict("records")[0])
            if len(songs) >= 10:
                break
        if len(songs) < 10:
            songs.extend(dataset.sample(10 - len(songs)).to_dict("records"))
        return JsonResponse({"recommendations": songs[:10]})

    # Search with ML
    try:
        # LAZY IMPORT — ONLY WHEN NEEDED
        from .utils.search_engine import search_songs
        results = search_songs(query, top_k=10)
        return JsonResponse({"recommendations": results})
    except Exception as e:
        logger.exception(f"Search failed: {e}")
        return JsonResponse({"error": "Search unavailable"}, status=500)

# =========================================
# SEARCH API (DRF)
# =========================================
@api_view(['GET'])
def search_api(request):
    query = request.GET.get('query', '').strip()

    if not query:
        if dataset.empty:
            return Response({"results": []})
        return Response({
            "results": dataset.sample(min(10, len(dataset))).to_dict("records")
        })

    try:
        from .utils.search_engine import search_songs  # LAZY
        results = search_songs(query, top_k=20)
        return Response({"results": results})
    except Exception as e:
        logger.exception(f"Search API error: {e}")
        return Response({"error": "Search failed"}, status=500)

# =========================================
# PAGE VIEWS
# =========================================
def discover_view(request):
    if dataset.empty:
        songs = []
    else:
        songs = []
        for genre, group in dataset.groupby("genre"):
            if len(songs) >= 10:
                break
            if not group.empty:
                songs.append(group.sample(1).to_dict("records")[0])
        if len(songs) < 10:
            songs.extend(dataset.sample(10 - len(songs)).to_dict("records"))
    return render(request, 'discover.html', {"songs": songs[:10]})

def genre_view(request): return render(request, 'genre.html')
def top_charts_view(request): return render(request, 'top_charts.html')
def trending_view(request): return render(request, 'trending.html')
def favourites_view(request): return render(request, 'favourites.html')
def playlist_view(request): return render(request, 'playlist.html')
def signup_view(request): return render(request, 'signup.html')