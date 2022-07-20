import json
import os
from pathlib import Path

from src import misc

root = (Path(__file__).parent.absolute())

with open(os.path.join(root, "custom_tracks_human.json"), "r") as f:
    human_json = json.load(f)

to_dump = {}

for entry in human_json:
    spot_url = entry["spotify_url"]
    track_id = misc.get_track_id(spot_url)
    youtube_url = entry["youtube_url"]
    to_dump[track_id] = youtube_url

with open(os.path.join(root, "custom_tracks_simple.json"), "w") as f:
    json.dump(to_dump, f, indent=4)
