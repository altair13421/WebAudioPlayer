import django.urls
import requests
from icecream import ic
import re
import os
from bs4 import BeautifulSoup
from django.conf import settings
from .models import LastFMArtist, LastFMSettings, LastFMImages
from player.models import Artist


class ImageFetcher:
    def __init__(self, artist):
        self.artist = artist
        try:
            lastfm_settings = LastFMSettings.objects.first()
            if not lastfm_settings:
                assert False, "LastFMSettings not found."
            assert (
                lastfm_settings.api_key and lastfm_settings.api_key != ""
            ), "API key is missing"
            assert (
                lastfm_settings.api_secret and lastfm_settings.api_secret != ""
            ), "API secret is missing"
            assert (
                lastfm_settings.app_name and lastfm_settings.app_name != ""
            ), "App name is missing"
        except AssertionError as E:
            ic(E)
            api_key = input("Enter your LastFM API key: ")
            api_secret = input("Enter your LastFM API secret: ")
            app_name = input("Enter your LastFM app name: ")
            lastfm_settings = LastFMSettings.objects.create(
                api_key=api_key, api_secret=api_secret, app_name=app_name
            )
            ic("LastFMSettings created successfully.")
        finally:
            self.api_key = lastfm_settings.api_key
            self.base_url = "http://ws.audioscrobbler.com/2.0/"
        self.artist_obj = self.get_artist_info()
        self.url = self.create_url(artist)

    def create_url(self, artist):
        """
        Creates a URL for the given artist and album.
        :param artist: Name of the artist
        :return: Formatted URL
        """
        self.url_prefix = "https://www.last.fm/music/"
        self.url_suffix = "+images/?page="
        return f"{self.url_prefix}{artist}/{self.url_suffix}"

    def clean_url(self, url):
        return re.sub(r"/i/u/[^/]+/", "/i/u/", url)

    def _create_artist_obj(self, artist):
        """
        Creates a LastFMArtist object if it doesn't exist.
        :return: LastFMArtist object
        """
        artist_obj, created = LastFMArtist.objects.get_or_create(
            name=artist.get("name"),
            mbid=artist.get("mbid"),
            defaults={
                "about_artist": artist.get("about_artist"),
                "lastfm_url": artist.get("lastfm_url"),
                "listeners": artist.get("listeners"),
                "playcount": artist.get("playcount"),
            },
        )
        if created:
            print(f"Artist created: {artist_obj.name}")
            artist = Artist.objects.filter(name=artist_obj.name).first()
            if artist:
                artist.lastfm_ref = artist_obj
                artist.save()
                print(f"Artist reference updated: {artist.name}")
        return artist_obj

    def get_artist_info(self):
        """
        Fetches artist information from Last.fm.
        :return: None
        """
        params = {
            "method": "artist.getinfo",
            "api_key": self.api_key,
            "artist": self.artist,
            "format": "json",
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            artist_data: dict = data.get("artist", {})
            if artist_data != {}:
                obj_data = {
                    "mbid": artist_data.get("mbid"),
                    "name": artist_data.get("name"),
                    "about_artist": artist_data.get("bio", {}).get("content", ""),
                    "lastfm_url": artist_data.get("bio", {})
                    .get("links")
                    .get("link", {})
                    .get("href", ""),
                    "listeners": artist_data.get("stats", {}).get("listeners", 0),
                    "playcount": artist_data.get("stats", {}).get("playcount", 0),
                }
                return self._create_artist_obj(obj_data)

    def scrape_images(self):
        images = []
        for i in range(1, 2):
            html_file = requests.get(f"{self.url}{i}")
            if html_file.status_code == 200:
                bs = BeautifulSoup(html_file.content, "html.parser")
                images_a_s = bs.find_all("li", class_="image-list-item-wrapper")
                for image_a in images_a_s:
                    image = image_a.find("img")
                    if image:
                        image_url = image["src"]
                        if image_url:
                            images.append(self.clean_url(image_url))
        self.write_images(images, self.artist_obj)

    def get_albums(self):
        """
        Scrapes the Last.fm page for the artist and retrieves album names.
        :return: List of album names
        """
        ...

    @staticmethod
    def write_images(
        image_list: list[str] | str, artist_obj: LastFMArtist = None, album: str = None
    ):
        """
        Writes the image URLs to a file.
        :param image_list: List of image URLs or a single URL
        :param artist: Name of the artist
        :param album: Name of the album
        """
        if isinstance(image_list, str):
            image_list = [image_list]
        for image in image_list:
            if image:
                filename = f""
                if album:
                    filename += os.path.join(
                        settings.MEDIA_ROOT,
                        artist_obj.name,
                        album,
                        image.split("/")[-1],
                    )
                else:
                    filename += os.path.join(
                        settings.MEDIA_ROOT, artist_obj.name, image.split("/")[-1]
                    )
                # check if Extension is in the filename
                if not filename.endswith((".jpg", ".jpeg", ".png")):
                    filename += ".png"
                filepath = os.path.dirname(filename)
                if not os.path.exists(filepath):
                    os.makedirs(filepath, exist_ok=True)
                # check if file already exists
                if os.path.exists(filename):
                    print(f"File already exists: {filename}")
                    continue
                with open(filename, "wb") as f:
                    response = requests.get(image)
                    if response.status_code == 200:
                        f.write(response.content)
                        image_created, created = LastFMImages.objects.get_or_create(
                            image=filename.removeprefix(f"{settings.MEDIA_ROOT}/"),
                            artist_ref=artist_obj,
                        )
                        if created:
                            print(f"Image saved: {filename}")
                        else:
                            print(f"Image already exists in the database: {filename}")
                    else:
                        print(f"Failed to fetch image: {image}")
            else:
                print("No image URL found.")


class LastFmImageFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://ws.audioscrobbler.com/2.0/"
        self.pattern = r"/i/u/[^/]+/"

    def _clean_url(self, url, pattern=None):
        """
        Cleans the URL by removing any unwanted characters.
        :param url: The URL to clean
        :param pattern: The regex pattern to use for cleaning
        :return: Cleaned URL
        """
        if url:
            if pattern is None:
                pattern = self.pattern
            # Remove unwanted characters from the URL
            return re.sub(pattern, "/i/u/", url)
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
            "format": "json",
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            ic(data.keys(), data["album"].keys())
            if "album" in data and "image" in data["album"]:
                images = data["album"]["image"]
                if any(images):
                    return self._clean_url(images[0]["#text"])
        return None
