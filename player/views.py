from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from .models import Artist, Album, Genre, Track
import os
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from pathlib import Path
import mimetypes
from .forms import FolderSelectForm
from icecream import ic


class IndexView(ListView):
    model = Track
    template_name = "player/index.html"
    context_object_name = "tracks"

    def get_queryset(self):
        # Check file existence for all tracks
        tracks = Track.objects.all().select_related("artist", "album", "genre")
        for track in tracks:
            track.check_file_exists()

        # Filter out invalid tracks
        return tracks.filter(is_valid=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["folder_form"] = FolderSelectForm()
        context["artists"] = Artist.objects.all()
        context["albums"] = Album.objects.all().select_related("artist")
        context["genres"] = Genre.objects.all()
        return context


class ScanDirectoryView(View):

    def post(self, request, *args, **kwargs):
        directory_path = request.POST.get("directory_path")
        if not directory_path or not os.path.exists(directory_path):
            messages.error(request, "Invalid directory path")
            return redirect("index")

        audio_extensions = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}
        scanned_files = 0
        new_tracks = 0

        for root, _, files in os.walk(directory_path):
            for file in files:
                if Path(file).suffix.lower() in audio_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        audio = MutagenFile(file_path)
                        if audio is None:
                            continue

                        # Try to get metadata
                        if isinstance(audio, EasyID3):
                            title = audio.get("title", [file])[0]
                            artist_name = audio.get("artist", ["Unknown Artist"])[0]
                            album_title = audio.get("album", ["Unknown Album"])[0]
                            genre_name = audio.get("genre", ["Unknown"])[0]
                        else:
                            title = file
                            artist_name = "Unknown Artist"
                            album_title = "Unknown Album"
                            genre_name = "Unknown"

                        # Get or create artist
                        artist, _ = Artist.objects.get_or_create(name=artist_name)

                        # Get or create genre
                        genre, _ = Genre.objects.get_or_create(name=genre_name)

                        # Get or create album
                        album, _ = Album.objects.get_or_create(
                            title=album_title, artist=artist, defaults={"genre": genre}
                        )

                        # Create track if it doesn't exist
                        track, created = Track.objects.get_or_create(
                            title=title,
                            artist=artist,
                            album=album,
                            defaults={
                                "genre": genre,
                                "file_path": file_path,
                                "duration": (
                                    audio.info.length
                                    if hasattr(audio.info, "length")
                                    else None
                                ),
                                "is_valid": True,
                            },
                        )

                        if created:
                            new_tracks += 1
                        scanned_files += 1

                    except Exception as e:
                        ic(e)
                        messages.warning(request, f"Error processing {file}: {str(e)}")

        messages.success(
            request, f"Scanned {scanned_files} files, added {new_tracks} new tracks"
        )
        return redirect("index")


class PlayTrackView(View):
    def get(self, request, track_id, *args, **kwargs):
        track = get_object_or_404(Track, id=track_id)

        # Check if file exists
        if not track.check_file_exists():
            return JsonResponse({"error": "File not found"}, status=404)

        # Get the MIME type
        mime_type, _ = mimetypes.guess_type(track.file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Stream the file
        response = FileResponse(open(track.file_path, "rb"), content_type=mime_type)
        response["Content-Disposition"] = (
            f'inline; filename="{os.path.basename(track.file_path)}"'
        )
        return response


class UpdateTrackView(View):
    def post(self, request, track_id, *args, **kwargs):
        track = get_object_or_404(Track, id=track_id)

        track.title = request.POST.get("title", track.title)
        track.track_number = request.POST.get("track_number", track.track_number)

        # Update artist
        artist_name = request.POST.get("artist")
        if artist_name:
            artist, _ = Artist.objects.get_or_create(name=artist_name)
            track.artist = artist

        # Update album
        album_title = request.POST.get("album")
        if album_title:
            album, _ = Album.objects.get_or_create(
                title=album_title, artist=track.artist
            )
            track.album = album

        # Update genre
        genre_name = request.POST.get("genre")
        if genre_name:
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            track.genre = genre

        track.save()
        return JsonResponse({"status": "success"})


class GetTrackInfoView(View):
    def get(self, request, track_id, *args, **kwargs):
        track = get_object_or_404(Track, id=track_id)

        # Check if file exists
        if not track.check_file_exists():
            return JsonResponse({"error": "File not found"}, status=404)

        return JsonResponse(
            {
                "id": track.id,
                "title": track.title,
                "artist": track.artist.name,
                "album": track.album.title,
                "genre": track.genre.name if track.genre else None,
                "duration": str(track.duration) if track.duration else None,
                "track_number": track.track_number,
            }
        )


class RemoveTrackView(View):
    def post(self, request, track_id, *args, **kwargs):
        track = get_object_or_404(Track, id=track_id)
        track.delete()
        return JsonResponse({"status": "success"})
