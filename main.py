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

failed = []
succeeded = []

if not config.get("thread_count"):
    max_threads = 10
else:
    max_threads = int(config["thread_count"]) if str(config["thread_count"]).isdigit() and config[
        "thread_count"] > 0 else 10

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


def download_song(song_name, song_url, lyrics_provider, output_format):
    term_command = subprocess.run(["spotdl", song_url,
                                   "--lyrics-provider", lyrics_provider,
                                   "--output-format", output_format],
                                  stdout=subprocess.DEVNULL, stderr=error_log)
    success = True
    if term_command.returncode == 0:
        print(f"Downloaded: {song_name} with URL: {song_url}")
    else:
        print(f"Failed to download: {song_name} with URL: {song_url}")
        success = False
        error_log.write("\n")
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


def download_trackingfile(file_path):
    term_command = subprocess.run(["spotdl", file_path, ], stdout=subprocess.DEVNULL, stderr=error_log)
    if not term_command.returncode == 0:
        print(f"Failed to finish download: {file_path}")
    else:
        print(f"Finished downloading: {file_path}")


for track in tracks_details:
    threads_to_run.append(
        threading.Thread(target=download_song,
                         args=(track["song_name"], track["song_url"], lyrics_provider, output_format)))

split_threads = misc.chunks(threads_to_run, max_threads)

for thread_chunk in split_threads:
    for thread in thread_chunk:
        thread.start()
    for thread in thread_chunk:
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
    thread.join()

print(f"\nDone! Task completed in {misc.get_time_str(start_time)}")
print(f"Downloaded files are in the `{download_folder}` folder")
print(f"Succeeded: {len(succeeded)}")
print(f"Failed: {len(failed)}")

os.chdir("..")  # change back to root directory
misc.change_title("All done, have a nice day!")
error_log.close()
