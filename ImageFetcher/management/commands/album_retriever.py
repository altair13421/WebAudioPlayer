from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Retrieves an album info from Last.fm'

    def add_arguments(self, parser):
        parser.add_argument('--album', type=str, help='Album name')
        parser.add_argument('--artist', type=str, help='Artist name')

    def handle(self, *args, **options):
        album = options['album']
        artist = options['artist']
        self.stdout.write(f'Album: {album}, By Artist: {artist}')