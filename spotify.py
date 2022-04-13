import json

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

scope = "user-library-read,user-library-modify,playlist-modify-private," \
        "playlist-read-private,playlist-modify-public,playlist-read-collaborative"
with open('config.json') as config_file:
    config = json.load(config_file)
client_id = config.get('client_id')
if not client_id:
    client_id = input("Enter your client id: ")
client_secret = config.get('client_secret')
if not client_secret:
    client_secret = input("Enter your client secret: ")

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


def playlist_track_details(playlist_id):
    results = spotify.playlist_items(playlist_id, limit=100)
    tracks = results["items"]
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results["items"])
    return [x["track"] for x in tracks]


def get_track_metadata(track):
    return {
        "song_name": track["name"],
        "song_album_name": track["album"]["name"],
        "song_artists": [artist["name"] for artist in track["artists"]],
        "song_duration": round(track["duration_ms"] / 1000, ndigits=3),
        "isrc": track.get('external_ids', {}).get('isrc'),
        "song_id": track["id"],
        "song_url": track["external_urls"]["spotify"],
    }


def playlist_tracks(playlist_id):
    tracks = []
    results = spotify.playlist_items(playlist_id, limit=100)
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results["items"])
    return tracks


def get_track_details(track_id):
    track = spotify.track(track_id)
    return track
