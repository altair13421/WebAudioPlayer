from django.core.management.base import BaseCommand
from ImageFetcher.managers import ImageFetcher
from player.models import Artist

class Command(BaseCommand):
    help = 'Retrieves an album info from Last.fm'

    def add_arguments(self, parser):
        parser.add_argument('--artist', type=str, help='Artist name, would display Only')

    def handle(self, *args, **options):
        self.stdout.write('Getting All Artists\' data.')
        artist_name = options['artist']
        if artist_name:
            fetcher = ImageFetcher(artist_name)
        else:
            self.stdout.write('No artist name provided, fetching all artists.')
        artists = Artist.objects.all()
        for artist in artists:
            fetcher = ImageFetcher(artist.name)
            self.stdout.write(f'Fetching images for artist: {artist.name}')
            # Call the method to scrape images
            fetcher.scrape_images()