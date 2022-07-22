import json
from xml.dom.minidom import Attr
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import misc

with open("config.json", "r") as f:
    config = json.load(f)
    client_id = config["client_id"]
    client_secret = config["client_secret"]
    redirect_uri = config["redirect_uri"]

scope = "user-library-read,user-library-modify,playlist-modify-private," \
        "playlist-read-private,playlist-modify-public,playlist-read-collaborative"

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope,
                                                    redirect_uri=redirect_uri, cache_path=".cache"))



def get_playlist_track_uris(playlist_id):
    uri_list = []
    results = spotify.playlist_items(playlist_id, limit=100)
    tracks = results["items"]
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results["items"])
    for track in tracks:
        uri_list.append(track["track"]["uri"])
    return uri_list


def get_track_uri(track):
    return track["track"]["uri"]


def divide_chunks(list, n):
    for i in range(0, len(list), n):
        yield list[i:i + n]


playlist_url = input("Enter the Playlist URL to add to: ")
try:
    new_playlist_id = misc.get_playlist_id(playlist_url)
except AttributeError:
    print("Invalid playlist URL, aborting...")
    new_playlist_id = ""
    exit()

print("Playlist ID: " + new_playlist_id)

print("Fetching existing track data for playlist")
existing_tracks = get_playlist_track_uris(playlist_id=new_playlist_id)
chunked_existing_tracks = list(divide_chunks(existing_tracks, 100))

# remove all tracks from playlist
print(f"Removing {len(existing_tracks)} tracks from playlist")
for i in range(len(chunked_existing_tracks)):
    print(f"\rPart {i + 1} of {len(chunked_existing_tracks)}", end="")
    spotify.playlist_remove_all_occurrences_of_items(playlist_id=new_playlist_id, items=chunked_existing_tracks[i])
print("\n")

# fetch favourite tracks
print("Getting tracks from custom tracks...")
with open("track_data/custom_tracks_simple.json", "r") as f:
    track_uris = json.load(f)
tracks_to_add = list(divide_chunks([uri for uri, _ in track_uris.items()], 100))

# add tracks to playlist
print("Adding tracks to playlist...")
for i in range(len(tracks_to_add)):
    print(f"\rPart {i + 1} of {len(tracks_to_add)}", end="")
    playlist_to_add = spotify.playlist_add_items(new_playlist_id, tracks_to_add[i])
print("\n")

print("Done!")