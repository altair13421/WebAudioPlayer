import requests
from icecream import ic
import re

class LastFmImageFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://ws.audioscrobbler.com/2.0/"
        self.pattern = r'/i/u/[^/]+/'

    def _clean_url(self, url, pattern = None):
        """
        Cleans the URL by removing any unwanted characters.
        :param url: The URL to clean
        :return: Cleaned URL
        """
        if url:
            if pattern is None:
                pattern = self.pattern
            # Remove unwanted characters from the URL
            return re.sub(pattern, '/i/u/', url)
        return None

    def get_album_image(self, artist, album):
        """
        Fetches the album image URL from Last.fm.
        :param artist: Name of the artist
        :param album: Name of the album
        :return: URL of the album image or None if not found
        """
        params = {
            "method": "album.getinfo",
            "api_key": self.api_key,
            "artist": artist,
            "album": album,
            "format": "json"
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "album" in data and "image" in data["album"]:
                images = data["album"]["image"]
                if any(images):
                    return self._clean_url(images[0]["#text"])
        return None

    def get_artist_image(self, artist):
        """
        Fetches the artist image URL from Last.fm.
        :param artist: Name of the artist
        :return: URL of the artist image or None if not found
        """
        params = {
            "method": "artist.getinfo",
            "api_key": self.api_key,
            "artist": artist,
            "format": "json"
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            ic(data)
            if "artist" in data and "image" in data["artist"]:
                images = data["artist"]["image"]
                for img in images:
                    if img["size"] == "large":  # You can change the size to your preference
                        return img["#text"]
        return None

# Example usage:
# api_key = "api_key_here"
# fetcher = LastFmImageFetcher(api_key)
# album_image = fetcher.get_album_image("Coldplay", "Parachutes")
# artist_image = fetcher.get_artist_image("Coldplay")
# print("Album Image URL:", album_image)
# print("Artist Image URL:", artist_image)