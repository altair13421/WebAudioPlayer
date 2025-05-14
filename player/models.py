import base64
from tabnanny import verbose
from django.db import models
import os
from django.db.models.manager import BaseManager
from random import choice
from icecream import ic

# Create your models here.


class Artist(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    lastfm_ref = models.ForeignKey(
        "ImageFetcher.LastFMArtist",
        on_delete=models.CASCADE,
        related_name="artist",
        null=True,
        blank=True,
    )

    @property
    def cover_art(self):
        return self.lastfm_ref.any_image.image if self.lastfm_ref else ""

    def __str__(self):
        return self.name

    @property
    def album_count(self):
        return self.albums.count()

    @property
    def track_count(self):
        return self.tracks.count()

    @property
    def genres(self):
        genres = set()
        for album in self.albums.all():
            for track in album.tracks.all():
                for genre in track.genre.all():
                    genres.add(genre)
        return list(genres)

    class Meta:
        ordering = ["name"]


class Genre(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums")
    release_date = models.DateField(null=True, blank=True)
    cover_art = models.BinaryField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    @property
    def cover_art_base64(self):
        return (
            base64.b64encode(self.cover_art).decode("utf-8") if self.cover_art else ""
        )

    @property
    def count(self):
        return self.tracks.count()

    class Meta:
        ordering = ["title"]


class Track(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ManyToManyField(Artist, related_name="tracks")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="tracks")
    genre = models.ManyToManyField(Genre, related_name="tracks")
    file_path = models.FilePathField(null=True, blank=True)
    duration = models.FloatField(default=0)
    track_number = models.PositiveIntegerField(null=True, blank=True)
    times_played = models.PositiveIntegerField(default=0)
    created_at = models.DateField(null=True)
    is_valid = models.BooleanField(default=True)  # Flag to track if file still exists

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    def get_file_extension(self):
        return os.path.splitext(self.file_path)[1]

    def check_file_exists(self):
        """Check if the file still exists and update the is_valid flag"""
        exists = os.path.exists(self.file_path)
        if self.is_valid != exists:
            self.is_valid = exists
            self.save(update_fields=["is_valid"])
        return exists

    class Meta:
        ordering = ["album", "track_number", "title"]


class Playlist(models.Model):
    name = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    songs = models.ManyToManyField(Track, related_name="playlist")

    @property
    def tracks(self):
        return self.songs.all()

    @property
    def count(self):
        return self.songs.count()

    def __str__(self):
        return f"Playlist: {self.name}|{self.count}"

    class Meta:
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"
        ordering = ["-created_at"]
        # abstract = True

class PlayHistory(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True, blank=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, blank=True)
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.track.title} - {self.playlist.name} - {self.played_at}"

    def save(self, *args, **kwargs):
        count = self.get_count()
        if count >= 50:
            # Remove the oldest record if there are already 100 records
            oldest_record = self.__class__.objects.order_by("-played_at").last()
            if oldest_record:
                oldest_record.delete()
        super().save(*args, **kwargs)

    @classmethod
    def get_count(cls):
        return cls.objects.count()

    class Meta:
        ordering = ["-played_at"]
        # abstract = True
