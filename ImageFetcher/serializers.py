from rest_framework import serializers
from .models import LastFMArtist, LastFMImages


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the LastFMImages model.
    """

    class Meta:
        model = LastFMImages
        fields = ["image", "artist_ref"]


class LastFMArtistSerializer(serializers.ModelSerializer):
    """
    Serializer for the LastFMArtist model.
    """

    any_image = ImageSerializer(many=False, read_only=True)


    class Meta:
        model = LastFMArtist
        fields = "__all__"
        # fields = ['name', 'artist', 'image_url']


class LastFMArtistGallerySerializer(serializers.ModelSerializer):
    """
    Serializer for the LastFMArtist model with a gallery of images.
    """

    all_images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = LastFMArtist
        # fields = "__all__"
