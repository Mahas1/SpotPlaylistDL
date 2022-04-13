import json
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import re

import spotify
import misc
tracks_details = []

with open("config.json") as f:
    config = json.load(f)

download_folder = config.get("download_folder") if config.get("download_folder") else "downloads"

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

for i in playlist_tracks:
    tracks_details.append(spotify.get_track_metadata(i))

to_download = {track["song_name"]: track["song_url"] for track in tracks_details}
misc.change_title("Preparing...")
print(f"Preparing to download {len(tracks_details)} tracks to the `{download_folder}` folder")
failed = []
succeeded = []

max_threads = 10
lock = threading.Lock()
threads_to_run = []

# change directory to project root before doing anything else
os.chdir(Path(__file__).parent.absolute())

# remove spotdl downloads folder if it exists
shutil.rmtree(download_folder, ignore_errors=True)

try:
    os.mkdir(download_folder)
except FileExistsError:
    pass

os.chdir(download_folder)  # change directory to downloads to download the files over there

error_log = open("error_log.txt", "a")


def download_song(song_name, song_url):
    term_command = subprocess.run(["spotdl", song_url,
                                   "--lyrics-provider", "genius",
                                   "--output-format", "m4a"],
                                  stdout=subprocess.DEVNULL, stderr=error_log)
    success = True
    if term_command.returncode == 0:
        print(f"Downloaded: {song_name} with URL: {song_url}")
    else:
        print(f"Failed to download: {song_name} with URL: {song_url}")
        success = False
    lock.acquire()
    if success:
        succeeded.append(song_url)
    else:
        failed.append(song_url)
    with open("../succeeded.json", "w") as f:
        json.dump(succeeded, f, indent=4)
    with open("../failed.json", "w") as f:
        json.dump(failed, f, indent=4)
    misc.change_title(f"Downloaded {len(succeeded)} of {len(to_download)} - {len(failed)} failed")
    lock.release()


for track in tracks_details:
    threads_to_run.append(
        threading.Thread(target=download_song, args=(track["song_name"], track["song_url"])))

split_threads = misc.chunks(threads_to_run, max_threads)

for thread_chunk in split_threads:
    for thread in thread_chunk:
        thread.start()
    for thread in thread_chunk:
        thread.join()

os.chdir("..")  # change back to root directory
print(f"Done! Downloaded files are in the `{download_folder}` folder")
print(f"Succeeded: {len(succeeded)}")
print(f"Failed: {len(failed)}")
misc.change_title("All done, have a nice day!")
