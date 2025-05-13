from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
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
