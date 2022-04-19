import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import misc
import spotify

start_time = time.time()

# change directory to project root before doing anything else
os.chdir(Path(__file__).parent.absolute())

with open("config.json") as f:
    config = json.load(f)

download_folder = config.get("download_folder", "downloads")
output_format = config.get("output_format", "m4a")
lyrics_provider = config.get("lyrics_provider", "genius")

playlist_verifier_regex = r"^https:\/\/open\.spotify\.com\/playlist\/(.)+?(\?si=)+?"
playlist_id_regex = r"(?<=\/playlist\/)(.*?)(?=\?|$)"
playlist_url = input("Enter playlist url: ")

if not re.match(playlist_verifier_regex, playlist_url):
    print("Invalid playlist url")
    playlist_id = ""
    exit()
else:
    playlist_id = re.search(playlist_id_regex, playlist_url).group(0)

print(f"Playlist ID: {playlist_id}")
try:
    playlist_tracks = spotify.playlist_track_details(playlist_id)
except Exception as e:
    print("An error occurred!")
    print(type(e).__name__, "-", e)
    sys.exit()

tracks_details = []
for i in playlist_tracks:
    if not i:
        continue
    tracks_details.append(spotify.get_track_metadata(i))

to_download = {track["song_name"]: track["song_url"] for track in tracks_details}
misc.change_title("Preparing...")

if not output_format.lower() in ["mp3", "m4a", "flac", "opus", "ogg", "wav"]:
    print("Invalid output format! Defaulting to m4a...")
    output_format = "m4a"
else:
    print(f"Output format: {output_format}")
print(f"Lyrics Provider: {lyrics_provider}")
print(f"Preparing to download {len(tracks_details)} tracks to the `{download_folder}` folder")

if not config.get("thread_count"):
    max_threads = os.cpu_count()
else:
    max_threads = int(config["thread_count"]) if str(config["thread_count"]).isdigit() and config[
        "thread_count"] > 0 else 10

print(f"Threads: {max_threads}")
lock = threading.Lock()
threads_to_run = []
thread_limiter = threading.BoundedSemaphore(max_threads)

# remove spotdl downloads folder if it exists
if config.get("clear_dl_folder", True):
    print(f"Clearing out folder: {download_folder}")
    shutil.rmtree(download_folder, ignore_errors=True)

try:
    os.mkdir(download_folder)
except FileExistsError:
    pass

os.chdir(download_folder)  # change directory to downloads to download the files over there

error_log = open("error_log.txt", "a")

downloaded_songs = 0


def download_song(song_name, song_url, lyrics_provider, output_format):
    global downloaded_songs
    thread_limiter.acquire()
    term_command = subprocess.run(["spotdl", song_url,
                                   "--lyrics-provider", lyrics_provider,
                                   "--output-format", output_format],
                                  stdout=subprocess.DEVNULL, stderr=error_log)
    lock.acquire()
    print(f"Downloaded: {song_name} | Return code: {term_command.returncode}\nTrack URL: {song_url}")
    downloaded_songs += 1
    misc.change_title(f"Downloaded {downloaded_songs} of {len(to_download)}")
    lock.release()
    thread_limiter.release()


def download_trackingfile(file_path):
    term_command = subprocess.run(["spotdl", file_path, ], stdout=subprocess.DEVNULL, stderr=error_log)

    print(f"Finished download: {file_path} | Return code: {term_command.returncode}")


for track in tracks_details:
    threads_to_run.append(
        threading.Thread(target=download_song,
                         args=(track["song_name"], track["song_url"], lyrics_provider, output_format)))

for thread in threads_to_run:
    thread.start()

for thread in threads_to_run:
    thread.join()

incomplete_threads = []
incomplete_downloads = [x for x in os.listdir(".") if x.lower().endswith(".spotdltrackingfile")]
if any(incomplete_downloads):
    print(f"\n{len(incomplete_downloads)} incomplete downloads found! Attempting to finish the download now...")
    misc.change_title("Finishing incomplete downloads...")
for file in os.listdir("."):
    if file.lower().endswith(".spotdltrackingfile"):
        incomplete_threads.append(
            threading.Thread(target=download_trackingfile, args=(file,))
        )

for thread in incomplete_threads:
    thread.start()

for thread in incomplete_threads:
    thread.join()

print(f"\nDone! Task completed in {misc.get_time_str(start_time)}")
print(f"Downloaded files are in the `{download_folder}` folder")
print(f"Succeeded: {len([x for x in os.listdir() if x.endswith(output_format)])} of {len(tracks_details)}")

misc.change_title("All done, have a nice day!")
os.chdir("..")  # change back to root directory

input("Press enter to exit...")
error_log.close()
