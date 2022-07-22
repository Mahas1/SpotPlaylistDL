# SpotPlaylistDL
A tool utilizing `spotdl` to download a playlist from Spotify.

> **Warning**
> This script is intended only for my use. If you want to use this, use it at your own risk.
However, bug reports and feature requests are appreciated.

## Usage
- Install dependencies by `pip install -r requirements.txt`
- Fill in the required details in `config.json` **(you need to create the file yourself)**
    ```json
    {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "redirect_uri": "http://localhost:8080 (set this up in the Spotify developer portal)",
        "bitrate": "320k",
        "download_folder": "~/downloads/spotdl downloads",
        "overwrite": "skip"
    }
    ```
- Run `python main.py`

## Adding Custom Tracks
- Access the Custom Track menu by running `python customtrack.py`
- You can add, delete, and view the existing Custom Tracks in the script.

## How It Works
- The script saves the metadata it acquires to `track_data/song_dicts.json` to save API calls on multiple downloads.
- When looking for metadata, it first searches the `song_dicts.json`. 
If metadata is not present, it fetches metadata from the Spotify API and saves it to the file.
- It then downloads each track in the playlist. This process is threaded, and uses as many threads as the number of CPU threads.
<br><br>
- Feel free to make a PR with your additions to the `song_dicts.json`.

# Credits
- [Spotdl](https://github.com/spotDL/spotify-downloader/) for Spotdl and for clarifying any doubts I had about their library.
- [Spotipy](https://github.com/plamere/spotipy) for the Spotify API Wrapper.
- [Joshj23](https://github.com/Joshj23icy) for their extensive help in gathering lyrics 
for hundreds of tracks now present in `song_dicts.json`.
