from django.core.management.base import BaseCommand
from player.models import Playlist


class Command(BaseCommand):
    help = 'cleans Existing playlist data'

    def handle(self, *args, **options):
        Playlist.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleaned all playlists'))
