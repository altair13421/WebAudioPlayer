from django.db import models
from random import choice
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet


class LastFMSettings(models.Model):
    api_key = models.CharField(max_length=127)
    api_secret = models.CharField(max_length=127)
    app_name = models.CharField(max_length=127)


# Create your models here.
class LastFMArtist(models.Model):
    mbid = models.UUIDField(max_length=127, null=True, blank=True)
    name = models.CharField(max_length=255)
    about_artist = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    lastfm_url = models.URLField(max_length=255, blank=True, null=True)
    listeners = models.PositiveBigIntegerField(default=0)
    playcount = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"Artist: {self.name.title()}"

    @property
    def all_images(self) -> BaseManager["LastFMImages"]:
        return self.images.all()

    @property
    def any_image(self):
        try:
            img_choice = choice(self.all_images)
        except:
            img_choice = ""
        return img_choice


class LastFMAlbum(models.Model):
    mbid = models.UUIDField()
    album = models.CharField(max_length=255)
    album_release_date = models.DateField()
    album_artist = models.ForeignKey(
        LastFMArtist, on_delete=models.CASCADE, related_name="albums"
    )
    album_genre = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Album: {self.album.title}"

    class Meta:
        abstract = True
        verbose_name = "LastFM Album"
        verbose_name_plural = "LastFM Albums"


class LastFMTrack(models.Model):
    mbid = models.UUIDField()
    track_name = models.CharField(max_length=255)
    track_duration = models.IntegerField()
    track_artist = models.ForeignKey(
        LastFMArtist, on_delete=models.CASCADE, related_name="tracks"
    )
    track_album = models.ForeignKey(
        LastFMAlbum, on_delete=models.CASCADE, related_name="tracks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Track: {self.track_name.title}"

    class Meta:
        abstract = True
        verbose_name = "LastFM Track"
        verbose_name_plural = "LastFM Tracks"


class LastFMImages(models.Model):
    image = models.CharField(max_length=255)
    artist_ref = models.ForeignKey(
        LastFMArtist,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
