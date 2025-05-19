from django.core.management.base import BaseCommand
from ImageFetcher.models import LastFMArtist
from player.models import Artist

class Command(BaseCommand):
    help = 'Retrieves an album info from Last.fm'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning All Artists\' data.')
        # Get all LastFMArtist objects
        artists = Artist.objects.all()
        for artist in artists:
            # Get the corresponding LastFMArtist object
            lastfm_artist: LastFMArtist = LastFMArtist.objects.filter(name=artist.name).first()
            if lastfm_artist:
                # Delete all images related to the LastFMArtist
                lastfm_artist.images.all().delete()
                # Delete the LastFMArtist object itself
                lastfm_artist.delete()
                self.stdout.write(f'Deleted images and LastFMArtist for {artist.name}')
            else:
                self.stdout.write(f'No LastFMArtist found for {artist.name}')
        self.stdout.write('All artists\' data has been cleaned.')
