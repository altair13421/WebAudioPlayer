# making a REST API for the ImageFetcher app
from sys import prefix
from django.urls import path

from rest_framework.routers import DefaultRouter
from .views import (
    LastFMArtistModelViewSet,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"lastfm/artist", LastFMArtistModelViewSet)

urlpatterns = []
urlpatterns += router.urls

