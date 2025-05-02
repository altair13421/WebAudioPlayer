import base64
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

    @property
    def cover_art(self):
        i = 0
        albums: BaseManager[Album] = self.albums.all()
        ic(self, self.albums.all())
        if albums.exist():
            if albums.count() < 2:
                return albums.first().cover_art_base64
            rand_album = choice(albums)
            if rand_album.cover_art_base64 not in [None, ""]:
                return rand_album.cover_art_base64
        return ""

    def __str__(self):
        return self.name

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

    class Meta:
        abstract = True
