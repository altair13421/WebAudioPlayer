# views.py
import random
from django.db.models.manager import BaseManager
from .models import Playlist, Track
import os
from icecream import ic
from django.db.models import F


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
                            *path_parts[: path_parts.index(part) + 1]
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


def generate_playlist(count: int = 20) -> list[Track]:
    """
    Generates a playlist of random tracks.
    :param count: Number of tracks to include in the playlist
    :return: List of Track objects
    """
    all_tracks = Track.objects.all()
    all_tracks_list = list(all_tracks)
    random.shuffle(all_tracks_list)
    random_playlist = all_tracks_list[:count]

    return Playlist.create_playlist(random_playlist)


def generate_top_played(count: int = 20) -> list[Track]:
    """
    Generates a list of the most played tracks.
    :param count: Number of tracks to include
    :return: List of Track objects
    """
    all_tracks = Track.objects.all().prefetch_related("artist", "album", "genre")
    all_tracks_list = list(all_tracks)
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
    ic(artist_list, genre_list)

    # remove Instrumental from the list
    all_tracks = all_tracks.exclude(title__icontains="instrumental")

    artist_tracks = list(all_tracks.filter(artist__name__in=artist_list))
    genre_tracks = list(all_tracks.filter(genre__name__in=genre_list))
    if artist_tracks:
        random.shuffle(artist_tracks)
        if len(artist_tracks) > 3:
            artist_tracks = artist_tracks[:3]
        else:
            artist_tracks = artist_tracks
    if genre_tracks:
        random.shuffle(genre_tracks)
        if len(genre_tracks) > 2:
            genre_tracks = genre_tracks[:12]
        else:
            genre_tracks = genre_tracks
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

    play = Playlist.create_playlist(playlist)
    return play


def generate_curated(count: int = 20) -> list[Track]:
    """
    Generates a list of the most rated tracks.
    :param count: Number of tracks to include
    :return: List of Track objects
    """
    most_listened = Track.objects.all().order_by("-times_played")[:count]
