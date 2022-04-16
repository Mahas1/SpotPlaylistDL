# SpotPlaylistDL

A small project I made to make my life a bit easier.

## Things to note

- You'll need Python 3.8 or higher to use this software.
- You'll also need ffmpeg and spotdl installed.
  - Install spotdl with `python3 -m pip install spotdl`
  - Install ffmpeg from [this link](https://ffmpeg.org/download.html)
- You'll need to make an application in the [Spotify Developer Portal](https://developer.spotify.com/dashboard/login).
- Copy the client ID and client secret, and paste them into the `config.json`.

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

## Optional features

- You can change the download directory by editing the `config.json` file's `download_folder` field.

```json
{
  "download_folder": "./downloads"
}
```
- You can change the amount of threads used with the `thread_count` field in the `config.json` file.
```json
{
  "thread_count": 10
}
```

- You can change the output format to any of mp3/m4a/flac/opus/ogg/wav by editing the `output_format` field in the `config.json` file.
  - If a valid format is not specified, m4a will be used.
```json
{
  "output_format": "mp3"
}
```

- You can change the lyrics provider by editing the `lyrics_provider` field in the `config.json` file.
  - If no provider is specified, it is automatically set to Genius. 
```json
{
  "lyrics_provider": "genius"
}
```