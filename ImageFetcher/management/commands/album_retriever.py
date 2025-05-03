from django.core.management.base import BaseCommand
from ImageFetcher.models import LastFMSettings
from ImageFetcher.managers import LastFmImageFetcher

class Command(BaseCommand):
    help = 'Retrieves an album info from Last.fm'

    def add_arguments(self, parser):
        parser.add_argument('--album', type=str, help='Album name')
        parser.add_argument('--artist', type=str, help='Artist name')

    def handle(self, *args, **options):
        album = options['album']
        artist = options['artist']
        try:
            lastfm_settings = LastFMSettings.objects.first()
            if not lastfm_settings:
                self.stdout.write('LastFMSettings not found.')
            assert lastfm_settings.api_key and lastfm_settings.api_key != "", "API key is missing"
            assert lastfm_settings.api_secret and lastfm_settings.api_secret != "", "API secret is missing"
            assert lastfm_settings.app_name and lastfm_settings.app_name != "", "App name is missing"
        except AssertionError as E:
            self.stdout.write(f'Error retrieving LastFMSettings. {E}')
            api_key = input("Enter your LastFM API key: ")
            api_secret = input("Enter your LastFM API secret: ")
            app_name = input("Enter your LastFM app name: ")
            lastfm_settings = LastFMSettings.objects.create(
                api_key=api_key,
                api_secret=api_secret,
                app_name=app_name
            )
            self.stdout.write('LastFMSettings created successfully.')
        if not album or not artist:
            self.stdout.write('Album and Artist names are required.')
            album = input("Enter the album name: ")
            artist = input("Enter the artist name: ")
        fetcher = LastFmImageFetcher(lastfm_settings.api_key)
        fetcher.get_album_image(artist, album)
        self.stdout.write(f'Album: {album}, By Artist: {artist}')