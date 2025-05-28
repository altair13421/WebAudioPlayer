from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from player.utils import generate_playlist, generate_top_played, top_artist_mix, generate_playlist_from_artist
from .models import Playlist, Track, Album, Artist, Genre
from .serializers import (
    ArtistInfoSerializer,
    PlaylistSerializer,
    TrackSerializer,
    AlbumSerializer,
    ArtistSerializer,
    GenreSerializer,
    PlaylistTrackSerializer,
)


class PlaylistsViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing playlists.
    """

    # Define your queryset and serializer_class here
    queryset = Playlist.objects.all()  # Replace with your actual queryset
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
        count = request.data.get("count", 40)
        playlist = generate_playlist(count)
        serializer = PlaylistTrackSerializer(playlist)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def generate_top_played(self, request, pk=None):
        """
        Generate a list of the most played tracks.
        """
        count = request.data.get("count", 40)
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


class ArtistViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing artists.
    """

    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

    def retrieve(self, request, *args, **kwargs):
        artist = self.get_object()
        serializer = ArtistInfoSerializer(artist)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def tracks(self, request, pk=None):
        artist: Artist = self.get_object()
        serializer = TrackSerializer(artist.tracks.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def albums(self, request, pk=None):
        artist: Artist = self.get_object()
        serializer = AlbumSerializer(artist.albums.all(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="top")
    def top_artists_mix(self, request):
        """
        Generate a playlist with the top artists.
        """
        count = request.data.get("count", 40)
        playlist = top_artist_mix(count)
        serializer = PlaylistTrackSerializer(playlist)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="generate")
    def generate_playlist_from_artist(self, request, pk=None):
        """
        Generate a playlist from a specific artist.
        """
        artist = self.get_object()
        count = request.data.get("count", 40)
        if artist.tracks.count() < 6:
            return Response({"error": "Not enough tracks for this artist"}, status=400)
        else:
            if count < artist.tracks.count():
                count = artist.tracks.count()
        playlist = generate_playlist_from_artist(artist, count)
        serializer = PlaylistTrackSerializer(playlist)
        return Response(serializer.data)
