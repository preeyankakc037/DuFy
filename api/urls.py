from django.urls import path, include
from rest_framework import routers
from music.views import MusicViewSet

router = routers.DefaultRouter()
router.register(r'music', MusicViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
