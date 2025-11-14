# recommendations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.discover_view, name='discover'),
    path('genre/', views.genre_view, name='genre'),
    path('top-charts/', views.top_charts_view, name='top_charts'),
    path('trending/', views.trending_view, name='trending'),
    path('favourites/', views.favourites_view, name='favourites'),
    path('playlist/', views.playlist_view, name='playlist'),
    path('signup/', views.signup_view, name='signup'),

    # APIs
    path('api/search/', views.search_api, name='search_api'),
    path('api/recommend/', views.get_recommendations, name='get_recommendations'),  # ✅ fixed endpoint
    path('recommend_songs/', views.get_recommendations),  # ← added alias

]
