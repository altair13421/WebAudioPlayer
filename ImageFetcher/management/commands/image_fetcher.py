from django.core.management.base import BaseCommand
from ImageFetcher.managers import ImageFetcher

class Command(BaseCommand):
    help = 'Retrieves an album info from Last.fm'

    def add_arguments(self, parser):
        parser.add_argument('--artist', type=str, help='Artist name', default='Aimer')

    def handle(self, *args, **options):
        artist = options['artist']
        self.stdout.write(f'Artist: {artist}')
        fetcher = ImageFetcher(artist)
        fetcher.scrape_images()