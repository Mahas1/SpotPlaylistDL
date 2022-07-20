import json
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import misc
import track_parser
import spotdl
from spotdl.types.song import Song

config = open("../config.json", "r")
config = json.load(config)

scope = "user-library-read,user-library-modify,playlist-modify-private," \
        "playlist-read-private,playlist-modify-public,playlist-read-collaborative"

client_id = config["client_id"]
client_secret = config["client_secret"]
redirect_uri = config["redirect_uri"]

spotdl.SpotifyClient.init(client_id=client_id, client_secret=client_secret,
                          user_auth=False)
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope,
                                                    redirect_uri=redirect_uri, cache_path="../.cache"))

parser = track_parser.Parser(spotify)

playlist_url = input("Enter playlist URL: ").strip()
playlist_id = misc.get_playlist_id(playlist_url)

# results = spotify.playlist(playlist_id)
results = misc.get_playlist_tracks(playlist_id, spotify)
start = time.time()

with open("../track_data/download_links.json", "r") as f:
    download_links = json.load(f)
with open("../track_data/lyrics.json", "r") as f:
    lyrics = json.load(f)


def generate_song_object(track_dict):
    start = time.time()
    result = parser.spotdl_dict(track_dict, get_lyrics=False)
    if result["song_id"] in lyrics:
        print("Lyrics present in json. Using that...")
        result["lyrics"] = lyrics[result["song_id"]]
    else:
        result["lyrics"] = parser.get_lyrics(result["name"], result["artists"])
    metadata_time = time.time()
    print("Metadata generated in:", int((metadata_time - start) * 1000), "milliseconds")
    song_obj = Song.from_dict(result)
    if result["song_id"] in download_links:
        print("Download URL present in json. Using that...")
        song_obj.download_url = download_links[result["song_id"]]
    else:
        song_obj.download_url = parser.get_download_url(song_obj)
    result["download_url"] = song_obj.download_url
    print(f"Track: {result['name']}")
    print("ID:", result["song_id"])
    print(f"Lyrics: {'Found' if result.get('lyrics') else 'Not found'}")
    print(f"Download URL: {result.get('download_url')}")
    if result.get("download_url") and result["song_id"] not in download_links:
        "Download URL not present... Adding to download links"
        download_links[result["song_id"]] = result["download_url"]
        with open("../track_data/download_links.json", "w") as f:
            json.dump(download_links, f, indent=4)
    if result.get("lyrics") and result["song_id"] not in lyrics:
        print("Lyrics not present... Adding to lyrics")
        lyrics[result["song_id"]] = result.get("lyrics")
        with open("../track_data/lyrics.json", "w") as f:
            json.dump(lyrics, f, indent=4)


tracks_count = len(results)
print(f"Found {tracks_count} tracks in playlist")
with open("../finished.json") as f:
    finished = json.load(f)
print(f"{finished} tracks already finished")
print(f"Running till track {finished+60}")

for i in range(finished, tracks_count):
    if i >= finished+60:
        break
    track = results[i]["track"]
    print("Generating: {}/{}".format(i + 1, tracks_count))
    try:
        generate_song_object(track)
    except Exception as e:
        print(f"{type(e).__name__} - {e}")
    print()
    with open("../finished.json", "w") as f:
        json.dump(i, f, indent=4)
