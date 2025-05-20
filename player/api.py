from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from player.utils import generate_playlist, generate_top_played
from .models import Playlist, Track, Album, Artist, Genre
from .serializers import PlaylistSerializer, TrackSerializer, AlbumSerializer, ArtistSerializer, GenreSerializer, PlaylistTrackSerializer

class PlaylistsViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing playlists.
    """
    # Define your queryset and serializer_class here
    queryset = Playlist  # Replace with your actual queryset
    serializer_class = PlaylistSerializer  # Replace with your actual serializer class

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a playlist by its ID.
        """
        instance = self.get_object()
        serializer = PlaylistTrackSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def generate_playlist(self, request, pk=None):
        """
        Generate a playlist of random tracks.
        """
        count = request.data.get("count", 20)
        playlist = generate_playlist(count)
        serializer = PlaylistTrackSerializer(playlist)
        return Response(serializer.data)


    @action(detail=False, methods=["post"])
    def generate_top_played(self, request, pk=None):
        """
        Generate a list of the most played tracks.
        """
        count = request.data.get("count", 20)
        playlist = generate_top_played(count)
        serializer = PlaylistTrackSerializer(playlist)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_track(self, request, pk=None):
        """
        Add a track to a playlist.
        """
        playlist = self.get_object()
        track_id = request.data.get("track_id")
        try:
            track = Track.objects.get(id=track_id)
            playlist.songs.add(track)
            return Response({"status": "Track added"})
        except Track.DoesNotExist:
            return Response({"error": "Track not found"}, status=404)
