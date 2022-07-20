import re, os, json

import spotipy

track_id_regex = r"(?<=\/track\/)(.*?)(?=\?|$)"
playlist_id_regex = r"(?<=\/playlist\/)(.*?)(?=\?|$)"


def get_track_id(playlist_url):
    playlist_id = re.search(track_id_regex, playlist_url).group(0)
    return playlist_id


def get_playlist_id(playlist_url):
    playlist_id = re.search(playlist_id_regex, playlist_url).group(0)
    return playlist_id


def get_playlist_tracks(playlist_id, spotipy_instance: spotipy.Spotify):
    results = spotipy_instance.playlist(playlist_id)["tracks"]
    tracks = results["items"]
    while results["next"]:
        results = spotipy_instance.next(results)
        tracks.extend(results["items"])
    return tracks


def pretty_time(input_seconds: int):
    if input_seconds < 0:
        return "0 seconds"
    minutes, seconds = divmod(input_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    final_string_to_join = []
    if weeks > 0:
        final_string_to_join.append(f"{weeks} {'weeks' if weeks != 1 else 'week'}")
    if days > 0:
        final_string_to_join.append(f"{days} {'days' if days != 1 else 'day'}")
    if hours > 0:
        final_string_to_join.append(f"{hours} {'hours' if hours != 1 else 'hour'}")
    if minutes > 0:
        final_string_to_join.append(f"{minutes} {'minutes' if minutes != 1 else 'minute'}")
    if seconds > 0:
        final_string_to_join.append(f"{seconds} {'seconds' if seconds != 1 else 'second'}")

    if len(final_string_to_join) > 1:
        final_string = ", ".join(final_string_to_join[:-1]) + f", and {final_string_to_join[-1]}"
    else:
        final_string = ", ".join(final_string_to_join)
    return final_string


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def load_tracks_from_disk():
    with open("track_data/song_dicts.json") as f:
        song_dicts = json.load(f)
        print(f"Loaded {len(song_dicts)} songs from file")
    return song_dicts


def get_song_ids_from_file(song_dicts: dict = None):
    if not song_dicts:
        with open("track_data/song_dicts.json") as f:
            song_dicts = json.load(f)
    song_ids = [song_dict.get("song_id") for song_dict in song_dicts]
    song_ids = list(set(song_ids))
    return song_ids


def save_tracks_to_file(song_dicts: dict):
    with open("track_data/song_dicts.json", "w") as f:
        json.dump(song_dicts, f, indent=4)
    print(f"Saved {len(song_dicts)} songs to file")


def id_track_mapping(song_dicts: dict):
    return {song_dict.get("song_id"): song_dict for song_dict in song_dicts}
