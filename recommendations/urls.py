from django.urls import path
from .views import get_recommendations, index

urlpatterns = [
    path('', index, name='index'),
    path('api/recommend/', get_recommendations, name='get_recommendations'),
]