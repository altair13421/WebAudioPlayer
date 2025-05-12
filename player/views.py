import base64
import json
import os

from django.http import JsonResponse

from django.db.models.manager import BaseManager
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, StreamingHttpResponse
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from django.conf import settings

from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from pathlib import Path
from icecream import ic
import mimetypes
from urllib.parse import quote
import time

from .forms import FolderSelectForm
from .models import Artist, Album, Genre, Track
from .utils import build_node, build_tree


def album_art_writer(artist, album, file_data):
    file_route = settings.MEDIA_ROOT / artist / f"{album}.png"
    with open(file_route, "wb") as file_write:
        file_write.write(file_data)


class IndexView(ListView):
    model = Track
    template_name = "player/index.html"
    context_object_name = "tracks"

    def get_queryset(self):
        # Check file existence for all tracks
        tracks: BaseManager[Track] = Track.objects.all().select_related("album")
        for track in tracks:
            track.check_file_exists()

        # Filter out invalid tracks
        return tracks.filter(is_valid=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["folder_form"] = FolderSelectForm()
        context["artists"] = Artist.objects.all()
        context["albums"] = Album.objects.all()
        context["genres"] = Genre.objects.all()
        # context["tree"] = []
        # tree_dict = build_tree(self.get_queryset())
        # for node in tree_dict:
        #     context["tree"].append(build_node(node))
        # with open(
        #     os.path.join(settings.BASE_DIR, "player", "tree.json"),
        #     "w",
        # ) as file:
        #     file.write(json.dumps(context["tree"], indent=2))
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

        def processor_generator(directory_path):
            nonlocal scanned_files
            nonlocal new_tracks
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if Path(file).suffix.lower() in audio_extensions:
                        file_path = os.path.join(root, file)
                        try:
                            audio = MutagenFile(file_path)
                            if Track.objects.filter(file_path=file_path).exists():
                                yield f"data: Processed File {root}{os.sep}{file}. File Already Exists\n"
                                continue
                            if audio is None:
                                continue
                            # ['TIT2', 'TPE1', 'TRCK', 'TALB', 'TPOS', 'TDRC', 'TCON', 'POPM:',
                            # 'TPE2', 'TSRC', 'TSSE', 'TENC', 'WOAS', 'TCOP', 'COMM::XXX', 'APIC:Cover']

                            title_mtg = audio.get("TIT2", "")
                            title = title_mtg.text[0] if title_mtg != "" else ""
                            artist_name_mtg = audio.get("TPE1", "")
                            artist_names = (
                                artist_name_mtg.text[0] if artist_name_mtg != "" else ""
                            )
                            orig_artist_mtg = audio.get("TPE2", "")
                            orig_artist_name = (
                                orig_artist_mtg.text[0] if orig_artist_mtg != "" else ""
                            )
                            album_title_mtg = audio.get("TALB", "")
                            album = (
                                album_title_mtg.text[0] if album_title_mtg != "" else ""
                            )
                            genres_mtg = audio.get("TCON", "")
                            genres = (
                                genres_mtg.text[0].split() if genres_mtg != "" else ""
                            )
                            cover_art_mtg = audio.get("APIC:Cover", "")
                            cover_art = (
                                cover_art_mtg.data if cover_art_mtg != "" else ""
                            )
                            date_mtg = audio.get("TDRC", "")
                            release_date = (
                                date_mtg.text[0] if date_mtg != "" else "0000-00-00"
                            )

                            # Get or create artist
                            artist_list = []
                            if artist_names != "":
                                if "/" in artist_names:
                                    for artist_name in artist_names.split("/"):
                                        artist, _ = Artist.objects.get_or_create(
                                            name=artist_name
                                        )
                                        artist_list.append(artist)
                                    artist = artist_list[0]
                                else:
                                    artist, _ = Artist.objects.get_or_create(
                                        name=artist_names
                                    )
                                    artist_list.append(artist)
                            else:
                                artist, _ = Artist.objects.get_or_create(name="Unkown")
                                artist_list.append(artist)

                            # Get or create genre
                            genre_list = []
                            for genre in genres:
                                genre, _ = Genre.objects.get_or_create(name=genre)
                                genre_list.append(genre)
                            if len(genre_list) == 0:
                                genre, _ = Genre.objects.get_or_create(name="Unknown")
                                genre_list.append(genre)

                            # Get or create album
                            if not album:
                                album = "Unknown"
                            if isinstance(cover_art, str):
                                cover_art = cover_art.encode("utf-8")
                            album, _ = Album.objects.get_or_create(
                                title=album,
                                artist=artist,
                                defaults={
                                    "cover_art": cover_art,
                                },
                            )
                            # Create track if it doesn't exist

                            track, created = Track.objects.get_or_create(
                                title=title,
                                album=album,
                                defaults={
                                    "file_path": f"{file_path}",
                                    "duration": (
                                        audio.info.length
                                        if hasattr(audio.info, "length")
                                        else None
                                    ),
                                    "is_valid": True,
                                },
                            )
                            if created:
                                for artist in artist_list:
                                    track.artist.add(artist)
                                for genre in genre_list:
                                    track.genre.add(genre)
                                new_tracks += 1
                                track.save()
                            scanned_files += 1
                            yield f"data: Processed File {root}{os.sep}{file}. Files Scanned {scanned_files}\n"

                        except Exception as e:
                            ic(e)
                            messages.warning(
                                request, f"Error processing {file}: {str(e)}"
                            )
                            return redirect("index")

            yield f"data: Finished scanning. Total files scanned {scanned_files}. New Tracks are {new_tracks} \n\n"

        return StreamingHttpResponse(
            processor_generator(directory_path), content_type="text/event-stream"
        )


class PlayTrackView(View):
    def get(self, request, track_id, *args, **kwargs):
        track = get_object_or_404(Track, id=track_id)

        # Check if file exists
        if not track.check_file_exists():
            return JsonResponse({"error": "File not found"}, status=404)

        try:
            # Convert the file path to a Path object for better handling
            file_path = Path(track.file_path)

            # Verify the file exists
            if not file_path.exists():
                return JsonResponse({"error": "File not found"}, status=404)

            # Get the MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = "audio/mpeg"  # Default to audio/mpeg for MP3 files

            # Open and stream the file
            response = FileResponse(
                open(file_path, "rb"), content_type=mime_type, as_attachment=False
            )

            # Set headers for proper streaming
            response["Accept-Ranges"] = "bytes"
            response["Content-Length"] = file_path.stat().st_size
            response["Cache-Control"] = "no-cache"

            # Set the Content-Disposition header with proper encoding
            filename = file_path.name
            encoded_filename = quote(filename)
            response["Content-Disposition"] = f'inline; filename="{encoded_filename}"'
            ic(
                response["Accept-Ranges"],
                response["Content-Length"],
                response["Cache-Control"],
                response["Content-Disposition"],
            )
            return response

        except Exception as e:
            ic(e)
            return JsonResponse({"error": str(e)}, status=500)


class UpdateTrackView(View):
    def post(self, request, track_id, *args, **kwargs) -> JsonResponse:
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
    def get(self, request, track_id, *args, **kwargs) -> JsonResponse:
        track = get_object_or_404(Track, id=track_id)

        # Check if file exists
        if not track.check_file_exists():
            return JsonResponse({"error": "File not found"}, status=404)

        try:
            # Get audio metadata using mutagen
            audio = MutagenFile(track.file_path)

            # Calculate duration in a readable format
            duration = None
            if hasattr(audio.info, "length"):
                duration = time.strftime("%M:%S", time.gmtime(audio.info.length))

            # Get bitrate if available
            bitrate = None
            if hasattr(audio.info, "bitrate"):
                bitrate = f"{audio.info.bitrate // 1000}kbps"

            return JsonResponse(
                {
                    "id": track.id,
                    "title": track.title,
                    "artist": ", ".join(artist.name for artist in track.artist.all()),
                    "album": track.album.title,
                    "cover_art": base64.b64encode(track.album.cover_art).decode(
                        "utf-8"
                    ),
                    "genre": ", ".join(genre.name for genre in track.genre.all()),
                    "duration": duration,
                    "bitrate": bitrate,
                    "track_number": track.track_number,
                    "file_format": track.get_file_extension().lstrip(".").upper(),
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class RemoveTrackView(View):
    def post(self, request, track_id, *args, **kwargs) -> JsonResponse:
        track = get_object_or_404(Track, id=track_id)
        track.delete()
        return JsonResponse({"status": "success"})
