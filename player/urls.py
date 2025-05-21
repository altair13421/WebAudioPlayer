from django.urls import path
from . import views

from rest_framework.routers import DefaultRouter
from .api import PlaylistsViewSet

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r"api/playlists", PlaylistsViewSet, basename="playlists")


urlpatterns = [
    path("", views.HomeView.as_view(), name="index"),
    path("v1/", views.v1IndexView.as_view(), name="v1-index"),
    path("scan/", views.ScanDirectoryView.as_view(), name="scan_directory"),
    path(
        "track/<int:track_id>/play/", views.PlayTrackView.as_view(), name="play_track"
    ),
    path(
        "track/<int:track_id>/update/",
        views.UpdateTrackView.as_view(),
        name="update_track",
    ),
    path(
        "track/<int:track_id>/info/",
        views.GetTrackInfoView.as_view(),
        name="get_track_info",
    ),
    path(
        "track/<int:track_id>/remove/",
        views.RemoveTrackView.as_view(),
        name="remove_track",
    ),
]

urlpatterns += router.urls
