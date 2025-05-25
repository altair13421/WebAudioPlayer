from rest_framework import serializers
from .models import Track, Artist, Album, Genre, Playlist


class TrackSerializer(serializers.ModelSerializer):
    artists = serializers.ListField(child=serializers.JSONField(), read_only=True)
    genres = serializers.ListField(child=serializers.CharField(), read_only=True)
    album_cover = serializers.CharField(read_only=True)

    class Meta:
        model = Track
        exclude = ["file_path"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AlbumSerializer(serializers.ModelSerializer):
    cover_art_base64 = serializers.CharField(source="cover_art_base64", read_only=True)
    track_count = serializers.IntegerField(read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)
    artist = serializers.CharField(source="artist.name", read_only=True)

    class Meta:
        model = Album
        fields = "__all__"


class ArtistSerializer(serializers.ModelSerializer):
    album_count = serializers.IntegerField(read_only=True)
    track_count = serializers.IntegerField(read_only=True)
    genres = serializers.ListField(child=serializers.CharField(), read_only=True)
    albums = AlbumSerializer(many=True, read_only=True)
    cover_art = serializers.CharField(read_only=True)

    class Meta:
        model = Artist
        fields = "__all__"


# only for the artist info
# used in the artist detail view
class ArtistInfoSerializer(serializers.ModelSerializer):
    album_count = serializers.IntegerField(read_only=True)
    track_count = serializers.IntegerField(read_only=True)
    genres = serializers.ListField(child=serializers.CharField(), read_only=True)
    albums = AlbumSerializer(many=True, read_only=True)
    cover_art = serializers.CharField(read_only=True)
    info = serializers.JSONField(read_only=True)

    class Meta:
        model = Artist
        fields = ["name", "id"]
        read_only_fields = ["id", "name", "album_count", "track_count", "genres"]


class PlaylistSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Playlist
        fields = "__all__"


class PlaylistTrackSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(read_only=True, many=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Playlist
        fields = "__all__"
