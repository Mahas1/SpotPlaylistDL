import json
import os
import pathlib
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from src import misc, track_parser
import spotdl
from spotdl.types.song import Song

from src.downloader import Downloader

from threading import Thread, Lock, Semaphore

config = open("config.json", "r")
config = json.load(config)

scope = "user-library-read," \
        "playlist-read-private," \
        "playlist-read-collaborative"

client_id = config["client_id"]
client_secret = config["client_secret"]
redirect_uri = config["redirect_uri"]

playlist_url = input("Enter the playlist URL: ")
try:
    playlist_id = misc.get_playlist_id(playlist_url)
except AttributeError:
    print("Invalid playlist URL, aborting...")
    playlist_id = ""
    exit()

spotdl_instance = spotdl.Spotdl(client_id=client_id,
                                client_secret=client_secret,
                                overwrite="skip",
                                threads=os.cpu_count() if os.cpu_count() <= 10 else 10,
                                bitrate=config.get("bitrate", "192k"),
                                user_auth=False
                                )
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope,
                                                    redirect_uri=redirect_uri, cache_path=".cache"))

track_downloader = spotdl.download.downloader.Downloader(
    overwrite=config.get("overwrite", "skip"),
    threads=os.cpu_count(),
    bitrate=config.get("bitrate", "192k"),
    output_format="mp3",
    sponsor_block=False,
    output="{album-artist}/{album}/{artists} - {title}.{output-ext}"

)

parser = track_parser.Parser(spotify)
song_downloader = Downloader(downloader=track_downloader)

results = misc.get_playlist_tracks(playlist_id, spotify)
start = time.time()

with open("track_data\\download_links.json", "r") as f:
    download_links = json.load(f)
with open("track_data\\lyrics.json", "r") as f:
    lyrics = json.load(f)

# with open("track_data/song_dicts.json") as f:
#     song_dicts = json.load(f)
#     print(f"Loaded {len(song_dicts)} songs from file")
#     song_count = 0

song_dicts = misc.load_tracks_from_disk()
cache_count = 0
id_track_mapping = misc.id_track_mapping(song_dicts)
to_download_ids = []
lock = Lock()
semaphore = Semaphore(os.cpu_count())


def generate_song_object(track_dict):
    semaphore.acquire()
    global song_dicts, cache_count, id_track_mapping, to_download_ids
    result = dict()
    try:
        result = parser.spotdl_dict(track_dict, get_lyrics=False)
        if result["song_id"] in id_track_mapping:
            to_download_ids.append(result["song_id"])
            print("Present in dict. Moving on...")
            try:
                lock.release()
            except RuntimeError:
                # release unlocked lock
                pass
            raise FileExistsError
        else:
            print(result["name"], "not present in cache.")
            cache_count += 1
        if result["song_id"] in lyrics:
            result["lyrics"] = lyrics[result["song_id"]]
        else:
            result["lyrics"] = parser.get_lyrics(result["name"], result["artists"])
        song_obj = Song.from_dict(result)
        if result["download_url"] is None:
            if result["song_id"] in download_links:
                song_obj.download_url = download_links[result["song_id"]]
            else:
                song_obj.download_url = parser.get_download_url(song_obj)
            result["download_url"] = song_obj.download_url
        if result.get("download_url") and result["song_id"] not in download_links:
            download_links[result["song_id"]] = result["download_url"]
        if result.get("lyrics") and result["song_id"] not in lyrics:
            lyrics[result["song_id"]] = result.get("lyrics")

        print(f"Metadata successfully fetched - {result['name']}")
        to_download_ids.append(result["song_id"])
        lock.acquire()
        song_dicts.append(result)
        to_download_ids.append(result["song_id"])
        try:
            lock.release()
        except RuntimeError:
            pass
        if cache_count != 0:
            lock.acquire()
            print("track unsaved, Saving now...")
            misc.save_tracks_to_file(song_dicts)
            cache_count = 0
            try:
                lock.release()
            except RuntimeError:
                # release unlocked lock
                pass

    except Exception as e:
        if isinstance(e, FileExistsError):
            print(f"Metadata successfully fetched from disk - {result['name']}")
        else:
            print(f"Metadata failed to fetch - {result['name'] if result else 'Track'} - {type(e).__name__}: {e}")
        try:
            lock.release()
        except:
            pass
    semaphore.release()


tracks_count = len(results)
print(f"Found {tracks_count} tracks in playlist")

metadata_generate_start = time.time()
threads = []
for i in range(0, tracks_count):
    track = results[i]["track"]
    thread = Thread(target=generate_song_object, args=(track,))
    threads.append(thread)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

metadata_end_time = time.time()
print("="*20)

print(f"Metadata generated in: {misc.pretty_time(int(metadata_end_time - metadata_generate_start))}")
# track metadata has been acquired
threads = []

to_download_dicts = [id_track_mapping[id] for id in to_download_ids]
song_objects = []
for item in to_download_dicts:
    song_objects.append(Song.from_dict(item))
song_object_generation_finish = time.time()
if cache_count != 0:
    misc.save_tracks_to_file(song_dicts)
    # save any remaining tracks
    cache_count = 0

for song in song_objects:
    threads.append(Thread(target=song_downloader.download, args=(song,)))

root_path = pathlib.Path(__file__).parent.absolute()

if config.get("download_folder"):
    folder = config["download_folder"]
    user_home = os.path.expanduser("~")
    try:
        os.mkdir(folder.replace("~", user_home))
    except FileExistsError:
        pass
    os.chdir(folder.replace("~", user_home))
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
download_end_time = time.time()
os.chdir(root_path)
print("="*20)
print(f"Downloads finished in: {misc.pretty_time(int(download_end_time - song_object_generation_finish))}")
print(f"Total time taken: {misc.pretty_time(int(download_end_time - start))}")
print("="*20)
input("Press any key to continue...")
