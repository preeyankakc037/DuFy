from django.urls import path
from .views import get_recommendations, index
from .views import SignupView ,PlaylistView


urlpatterns = [
    path('', index, name='index'),
    path('api/recommend/', get_recommendations, name='get_recommendations'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('playlist/', PlaylistView.as_view(), name='playlist'),
]


