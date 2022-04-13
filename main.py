import json
import os
import shutil
import subprocess
import threading

import re

import spotify
import misc
tracks_details = []

playlist_verifier_regex = r"^https:\/\/open\.spotify\.com\/playlist\/(.)+?(\?si=)+?"
playlist_id_regex = r"(?<=\/playlist\/)(.*?)(?=\?|$)"
playlist_url = input("Enter playlist url: ")
if not re.match(playlist_verifier_regex, playlist_url):
    print("Invalid playlist url")
    playlist_id = ""
    exit()
else:
    playlist_id = re.search(playlist_id_regex, playlist_url).group(0)

playlist_tracks = spotify.playlist_track_details(playlist_id)
for i in playlist_tracks:
    tracks_details.append(spotify.get_track_metadata(i))

to_download = {track["song_name"]: track["song_url"] for track in tracks_details}
failed = []
succeeded = []

max_threads = 10
lock = threading.Lock()
threads_to_run = []

shutil.rmtree("spotdl-dls", ignore_errors=True)

try:
    os.mkdir("spotdl-dls")
except FileExistsError:
    pass

os.chdir("spotdl-dls")  # change directory to spotdl-dls to download the files over there


def download_song(song_name, song_url):
    term_command = subprocess.run(["spotdl", song_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
print("Done!")
print(f"Succeeded: {len(succeeded)}")
print(f"Failed: {len(failed)}")
