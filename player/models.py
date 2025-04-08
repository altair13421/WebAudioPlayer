from django.db import models
from django.core.validators import FileExtensionValidator
import os

# Create your models here.

class Artist(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Genre(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    cover_art = models.ImageField(upload_to='album_covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    class Meta:
        ordering = ['title']

class Track(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='tracks')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    file_path = models.CharField(max_length=1000)  # Store the absolute path to the file
    duration = models.DurationField(null=True, blank=True)
    track_number = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
            self.save(update_fields=['is_valid'])
        return exists

    class Meta:
        ordering = ['album', 'track_number', 'title']
