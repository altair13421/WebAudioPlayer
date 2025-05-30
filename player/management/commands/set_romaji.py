from django.core.management.base import BaseCommand
from player.utils import set_existing_track_romajis

class Command(BaseCommand):
    help = 'Sets romaji for existing tracks'

    def handle(self, *args, **options):
        set_existing_track_romajis()
        self.stdout.write(self.style.SUCCESS('Successfully set romaji for existing tracks'))
