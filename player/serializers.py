from rest_framework import serializers
from .models import Track, Artist, Album, Genre, Playlist

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = "__all__"


class ArtistSerializer(serializers.ModelSerializer):
    album_count = serializers.IntegerField(read_only=True)
    track_count = serializers.IntegerField(read_only=True)
    genres = serializers.ListField(child=serializers.CharField(), read_only=True)

    class Meta:
        model = Artist
        fields = "__all__"

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

class AlbumSerializer(serializers.ModelSerializer):
    cover_art_base64 = serializers.CharField(source="cover_art_base64", read_only=True)
    track_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Album
        fields = "__all__"

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = "__all__"

class PlaylistTrackSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(read_only=True, many=True)

    class Meta:
        model = Playlist
        fields = "__all__"
