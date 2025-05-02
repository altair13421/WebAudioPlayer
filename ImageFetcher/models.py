from django.db import models

class LastFMSettings(models.Model):
    api_key = models.CharField(max_length=127)
    api_secret = models.CharField(max_length=127)
    


# Create your models here.
class LastFMArtist(models.Model):
    mbid = models.CharField(max_length=127)
    artist_name = models.CharField(max_length=255)
    about_artist = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    lastfm_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Artist: {self.artist_name.title()}, Image Path: {self.image_path}"


class LastFMAlbum(models.Model):
    album = models.CharField(max_length=255)
    album_release_date = models.DateField()
    album_artist = models.ForeignKey(LastFMArtist, on_delete=models.CASCADE, related_name='albums')
    album_genre = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Album: {self.album.title}, Image Path: {self.image_path}"

class LastFMImages(models.Model):
    image = models.FilePathField()
    artist_ref = models.ForeignKey(LastFMArtist, on_delete=models.CASCADE, related_name='images')
    album_ref = models.ForeignKey(LastFMAlbum, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)