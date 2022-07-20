import json

import spotdl.providers.lyrics
from spotdl.providers.lyrics import base as lyrics_base, musixmatch, genius
from spotdl.providers.audio import ytmusic, base as audio_base


class Parser:

    def __init__(self, spotipy_instance):
        self.spotipy = spotipy_instance
        self.base_lyrics = lyrics_base.LyricsProvider()
        self.base_audio = audio_base.AudioProvider()
        self.audio_provider = ytmusic.YouTubeMusic(self.base_audio)
        with open("track_data/custom_tracks_simple.json") as f:
            self.custom_tracks = json.load(f)

    def spotdl_dict(self, spotipy_track: dict, get_lyrics: bool = True):
        raw_album_meta = self.spotipy.album(spotipy_track["album"]["id"])
        raw_artist_meta = self.spotipy.artist(spotipy_track["artists"][0]["id"])

        result = {
            "name": spotipy_track["name"],
            "artists": [artist["name"] for artist in spotipy_track["artists"]],
            "artist": spotipy_track["artists"][0]["name"],
            "album_name": spotipy_track["album"]["name"],
            "album_artist": spotipy_track["album"]["artists"][0]["name"],
            "copyright_text": raw_album_meta["copyrights"][0]["text"] if raw_album_meta["copyrights"] else None,
            "genres": raw_album_meta["genres"] + raw_artist_meta["genres"],
            "disc_number": spotipy_track["disc_number"],
            "disc_count": int(raw_album_meta["tracks"]["items"][-1]["disc_number"]),
            "duration": spotipy_track["duration_ms"] / 1000,
            "year": spotipy_track["album"]["release_date"][:4],
            "date": spotipy_track["album"]["release_date"],
            "track_number": spotipy_track["track_number"],
            "tracks_count": spotipy_track["album"]["total_tracks"],
            "isrc": spotipy_track.get("external_ids", {}).get("isrc"),
            "song_id": spotipy_track["id"],
            "explicit": spotipy_track["explicit"],
            "publisher": raw_album_meta["label"],
            "url": spotipy_track["external_urls"]["spotify"],
            "cover_url": raw_album_meta["images"][0]["url"] if raw_album_meta["images"] else None,
            "download_url": None,  # populated later
            "song_list": None,
            # "song_list": Album.from_url(spotipy_track["album"]["external_urls"]["spotify"]),
            "lyrics": None  # populated later
        }
        if get_lyrics:
            result["lyrics"] = self.get_lyrics(
                name=result["name"],
                artists=result["artists"]
            )
        if result["song_id"] in self.custom_tracks:
            result["download_url"] = self.custom_tracks[result["song_id"]]
        return result

    def get_lyrics(self, name: str, artists: list):
        lyrics = musixmatch.MusixMatch.get_lyrics(self=self.base_lyrics,
                                                  name=name,
                                                  artists=artists)
        if not lyrics:
            lyrics = genius.Genius.get_lyrics(self=self.base_lyrics,
                                              name=name,
                                              artists=artists)
        if not lyrics and len(artists) > 1:
            lyrics = self.get_lyrics(name=name, artists=artists[0])
        return lyrics

    def get_download_url(self, song_object: spotdl.types.Song):
        return self.audio_provider.search(song=song_object)
