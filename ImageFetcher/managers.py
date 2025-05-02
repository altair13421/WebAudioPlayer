import requests
from icecream import ic
import re
from bs4 import BeautifulSoup


class ImageFetcher:
    def __init__(self, artist):
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

    def scrape_images(self):
        for i in range(1, 4):
            html_file = requests.get(f"{self.url}{i}")
            if html_file.status_code == 200:
                print(f"Page {i} loaded successfully.")
                bs = BeautifulSoup(html_file.content, "html.parser")
                images_a_s = bs.find_all("li", class_="image-list-item-wrapper")
                print(f"Found images, {len(images_a_s)}")
                images = []
                for image_a in images_a_s:
                    image = image_a.find("img")
                    if image:
                        image_url = image["src"]
                        if image_url:
                            images.append(image_url)

    def get_albums(self):
        """
        Scrapes the Last.fm page for the artist and retrieves album names.
        :return: List of album names
        """
        ...

    @staticmethod
    def write_images(image_list: list[str] | str):
        if isinstance(image_list, str):
            image_list = [image_list]


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

    def _save_image(self, url, filename, artist, album=None):
        """
        Saves the image from the URL to a local file.
        :param url: The URL of the image
        :param filename: The name of the file to save the image as
        :param album: The album name
        :param artist: The artist name

        :return: The filename if successful, None otherwise
        """

        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
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
            "format": "json",
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            ic(data.keys(), data["artist"].keys())
            if "artist" in data and "image" in data["artist"]:
                images = data["artist"]["image"]
                for img in images:
                    if (
                        img["size"] == "large"
                    ):  # You can change the size to your preference
                        return img["#text"]
        return None


# Example usage:
# api_key = "api_key_here"
# fetcher = LastFmImageFetcher(api_key)
# album_image = fetcher.get_album_image("Coldplay", "Parachutes")
# artist_image = fetcher.get_artist_image("Coldplay")
# print("Album Image URL:", album_image)
# print("Artist Image URL:", artist_image)
