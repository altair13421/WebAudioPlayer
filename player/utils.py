# views.py
import random
from django.db.models.manager import BaseManager
from .models import Artist, Playlist, Track, Genre, Album
import os
from icecream import ic
from pathlib import Path
from django.db.models import F
from mutagen import File as MutagenFile
from cutlet import Cutlet

katsu = Cutlet()


def build_tree(tracks: BaseManager["Track"]) -> list[dict]:
    """
    Takes a list of Track objects and returns a hierarchical folder structure.
    Omits the first two parts of the path (e.g., '/home/') and builds the tree from there.
    """
    tree = []
    path_parts_dict = {}

    for track in tracks:
        # Split the path into parts
        path_parts = track.file_path.split("/")

        # Omit the first two parts (e.g., '/' and 'home')
        relevant_path = path_parts[2:]
        path_for_checking = "/".join(path_parts[:2])

        # Build the full path string for display
        display_path = "/".join(relevant_path)

        # Current level in the tree
        current_level = path_parts_dict

        # Iterate through each part of the path
        for part in relevant_path:
            if part not in current_level:
                # Create a new node
                current_level[part] = {
                    "name": part,
                    "children": {},
                    "is_folder": os.path.isdir(
                        os.path.join(
                            *path_for_checking,
                            *path_parts[: path_parts.index(part) + 1],
                        )
                    ),
                }
            # Move to the next level
            current_level = current_level[part]["children"]

    # Convert the dictionary to a list of nodes for the template
    return [
        {"name": key, "children": value["children"], "is_folder": True}
        for key, value in path_parts_dict.items()
    ]


def build_node(node, level=0):
    """
    Recursively builds the tree structure for the template.
    """
    return {
        "name": node["name"],
        "children": [
            build_node(child, level + 1) for child in node["children"].values()
        ],
        "level": level,
        "is_folder": node.get("is_folder", False),
    }

    # tree_dict = build_tree(self.get_queryset())
    # for node in tree_dict:
    #     context["tree"].append(build_node(node))


def generate_playlist(count: int = 40) -> list[Track]:
    """
    Generates a playlist of random tracks.
    :param count: Number of tracks to include in the playlist
    :return: List of Track objects
    """
    all_tracks = Track.objects.all().exclude(title__icontains="instrumental")
    all_tracks_list = list(all_tracks)
    random.shuffle(all_tracks_list)
    random_playlist = all_tracks_list[:count]

    return Playlist.create_playlist(random_playlist)


def generate_top_played(count: int = 40) -> list[Track]:
    """
    Generates a list of the most played tracks.
    :param count: Number of tracks to include
    :return: List of Track objects
    """
    all_tracks = Track.objects.all().exclude(title__icontains="instrumental")
    all_tracks_list = list(all_tracks[:1000])
    random.shuffle(all_tracks_list)
    actual_play_count = all_tracks.filter(times_played__gt=0).order_by("-times_played")[
        :count
    ]
    artist_list, genre_list = [], []
    if actual_play_count.count() > 0:
        # Get the first track's artist and genre
        for track in actual_play_count:
            for artist in track.artist.all():
                if artist.name not in artist_list:
                    artist_list.append(artist.name)
            for genre in track.genre.all():
                if genre.name not in genre_list:
                    genre_list.append(genre.name)
    if len(artist_list) < 5 or len(genre_list) < 5:
        # If not enough artists or genres, shuffle the tracks and get more
        for track in all_tracks_list[:count]:
            for artist in track.artist.all():
                if artist.name not in artist_list:
                    artist_list.append(artist.name)
            for genre.name in track.genre.all():
                if genre not in genre_list:
                    genre_list.append(genre.name)

    playlist = []

    artist_tracks = list(all_tracks.filter(artist__name__in=artist_list))
    genre_tracks = list(all_tracks.filter(genre__name__in=genre_list))
    if artist_tracks:
        random.shuffle(artist_tracks)
        artist_tracks = artist_tracks[:3]
    if genre_tracks:
        random.shuffle(genre_tracks)
        genre_tracks = genre_tracks[: count * (2 / 3)]
    all_lists = []
    for track in artist_tracks:
        if not track in all_lists:
            all_lists.append(track)
    for track in genre_tracks:
        if not track in all_lists:
            all_lists.append(track)
    random.shuffle(all_lists)
    playlist.extend(all_lists[:count])
    all_tracks = all_tracks.exclude(id__in=[track.id for track in playlist])
    # Add random tracks to fill the playlist
    while len(playlist) < count:
        random_track = random.choice(all_tracks)
        if random_track not in playlist:
            playlist.append(random_track)

    playlist = playlist[:count]

    print(count)
    play = Playlist.create_playlist(playlist)
    return play


def generate_curated(count: int = 40) -> list[Track]:
    """
    Generates a list of the most rated tracks.
    :param count: Number of tracks to include
    :return: List of Track objects
    """
    most_listened = (
        Track.objects.all()
        .exclude(title__icontains="instrumental")
        .order_by("-times_played")[:count]
    )


def top_artist_mix(count: 40):
    """
    Generates a playlist with the top artists.
    :param count: Number of tracks to include
    :return: List of Track objects
    """
    top_tracks = (
        Track.objects.order_by("-times_played")
        .exclude(title__icontains="instrumental")
    )
    top_tracks = random.sample(list(top_tracks), count)
    artists = Artist.objects.filter(tracks__in=top_tracks).distinct()
    playlist = []
    for artist in artists:
        artist_tracks = artist.tracks.all()[:count]
        playlist.extend(artist_tracks)
    if len(playlist) < count:
        all_tracks = Track.objects.all().exclude(
            id__in=[track.id for track in playlist]
        )
        all_tracks = all_tracks.exclude(title__icontains="instrumental")
        all_tracks = list(all_tracks)
        random.shuffle(all_tracks)
        while len(playlist) < count:
            random_track = random.choice(all_tracks)
            if random_track not in playlist:
                playlist.append(random_track)
    random_tracks = random.sample(playlist, count)
    return Playlist.create_playlist(random_tracks)


def generate_playlist_from_artist(artist: Artist, count: int = 40) -> list[Track]:
    """
    Generates a playlist from a specific artist.
    :param artist: Artist object
    :param count: Number of tracks to include
    :return: List of Track objects
    """
    artist_tracks: Track = artist.tracks.all()
    genre_artists = (
        Artist.objects.filter(
            tracks__genre__in=artist_tracks.values_list("genre", flat=True)
        )
        .distinct()
        .exclude(id=artist.id)
    )
    # raise Exception("Not implemented yet")
    # print(count)
    if artist_tracks.count() < count:
        # print("this true?")
        count = artist_tracks.count()
    random_tracks = random.sample(list(artist_tracks), int(count * 2 / 3))
    while len(random_tracks) < count:
        # Add tracks from similar artists
        similar_artist_tracks = random.sample(
            list(genre_artists.values_list("tracks__id", flat=True)),
            count - len(random_tracks),
        )
        similar_artist_tracks = Track.objects.filter(
            id__in=similar_artist_tracks
        ).exclude(id__in=[track.id for track in random_tracks])
        random_tracks.extend(similar_artist_tracks)
    random_tracks = random.sample(random_tracks, count)
    # print(len(random_tracks), count)
    # raise Exception("Not implemented yet")
    return Playlist.create_playlist(random_tracks, artist_mix=artist.name)


def generate_playlist_from_genre(genre: str, count: int = 40) -> list[Track]:
    """
    Generates a playlist from a specific genre.
    :param genre: Genre string
    :param count: Number of tracks to include
    :return: List of Track objects
    """
    genre_tracks = Track.objects.filter(genre__name=genre)
    if genre_tracks.count() < count:
        count = genre_tracks.count()
    random_tracks = random.sample(list(genre_tracks), count)
    return Playlist.create_playlist(random_tracks)


import os


def process_directory(directory_path):
    """
    Processes a directory path to extract the base directory and subdirectories.
    :param directory_path: Full directory path
    :return: Tuple of (base directory, subdirectories)
    """
    audio_extensions = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}
    scanned_files = 0
    new_tracks = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            if Path(file).suffix.lower() in audio_extensions:
                file_path = os.path.join(root, file)
                try:
                    audio_file = MutagenFile(file_path)
                    if audio_file is None:
                        print("Invalid audio file:", file_path)
                        yield f"Invalid audio file: {file_path}"
                        continue
                    if Track.objects.filter(file_path=file_path).exists():
                        print("Track already exists:", file_path)
                        yield f"Track already exists: {file_path}"
                        continue
                    created, track = process_file(file_path)
                    if created:
                        new_tracks += 1
                        print(
                            "New track added:",
                            track.title,
                            "by",
                            ", ".join(artist.name for artist in track.artist.all()),
                        )
                        yield f"New track added: {track.title} by {', '.join(artist.name for artist in track.artist.all())}"
                    else:
                        yield f"Track already exists: {track.title} by {', '.join(artist.name for artist in track.artist.all())}"
                except Exception as e:
                    yield f"Error processing file {file_path}: {e}"
                    continue
                scanned_files += 1
    yield f"Scanned {scanned_files} files, found {new_tracks} new tracks."


def process_file(file_path):
    """
    Processes a file path to extract the directory and file name.
    :param file_path: Full file path
    :return: Tuple of (directory, file name)
    """
    audio = MutagenFile(file_path)

    title_mtg = audio.get("TIT2", "")
    title = title_mtg.text[0] if title_mtg != "" else ""
    artist_name_mtg = audio.get("TPE1", "")
    artist_names = artist_name_mtg.text[0] if artist_name_mtg != "" else ""
    orig_artist_mtg = audio.get("TPE2", "")
    orig_artist_name = orig_artist_mtg.text[0] if orig_artist_mtg != "" else ""
    album_title_mtg = audio.get("TALB", "")
    album = album_title_mtg.text[0] if album_title_mtg != "" else ""
    genres_mtg = audio.get("TCON", "")
    genres = genres_mtg.text[0].split() if genres_mtg != "" else ""
    cover_art_mtg = audio.get("APIC:Cover", "")
    cover_art = cover_art_mtg.data if cover_art_mtg != "" else ""
    date_mtg = audio.get("TDRC", "")
    release_date = date_mtg.text[0] if date_mtg != "" else "0000-00-00"

    # Get or create artist
    artist_list = []
    if artist_names != "":
        if "/" in artist_names:
            for artist_name in artist_names.split("/"):
                artist, _ = Artist.objects.get_or_create(
                    name=artist_name,
                    romaji_name=get_romaji(artist_name),
                )
                artist_list.append(artist)
            artist = artist_list[0]
        else:
            artist, _ = Artist.objects.get_or_create(
                name=artist_names,
                romaji_name=get_romaji(artist_names),
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

    # Artist in defaults, because it is making multiple albums.
    album, _ = Album.objects.get_or_create(
        title=album,
        romaji_title=get_romaji(album),
        defaults={
            "cover_art": cover_art,
            "artist": artist,
        },
    )
    # Create track if it doesn't exist

    track, created = Track.objects.get_or_create(
        title=title,
        romaji_title=get_romaji(title),
        album=album,
        defaults={
            "file_path": f"{file_path}",
            "duration": (audio.info.length if hasattr(audio.info, "length") else None),
            "is_valid": True,
        },
    )
    if created:
        for artist in artist_list:
            track.artist.add(artist)
        for genre in genre_list:
            track.genre.add(genre)
        track.save()
    return created, track


def set_existing_track_romajis():
    for track in Track.objects.all():
        if not track.romaji_title:
            track.romaji_title = get_romaji(track.title)
            print("setting romaji for track:", track.title, "|", track.romaji_title)
            track.save()
    for artist in Artist.objects.all():
        if not artist.romaji_name:
            artist.romaji_name = get_romaji(artist.name)
            print("setting romaji for artist:", artist.name, "|", artist.romaji_name)
            artist.save()
    for album in Album.objects.all():
        if not album.romaji_title:
            album.romaji_title = get_romaji(album.title)
            print("setting romaji for album:", album.title, "|", album.romaji_title)
            album.save()


def get_romaji(title: str) -> str:
    """
    Returns the romaji version of the title using Cutlet.
    :param title: Title string
    :return: Romaji string
    """
    if not title:
        return ""
    title_rom = katsu.romaji(title)
    if "?" not in title_rom:
        # that means it is a valid romaji
        return title_rom
    # Try Again With Korean, But I have no idea how to do that
    # Return the original title if romaji conversion fails
    return title
