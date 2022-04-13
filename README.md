# SpotPlaylistDL

A small project I made to make my life a bit easier.

## Things to note

- You'll need Python 3.8 or higher to use this software.
- You'll need to make an application in the [Spotify Developer Portal](https://developer.spotify.com/dashboard/login).
- Copy the client ID and client secret, and paste them into the `config.json`.

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

## Optional features

- you can change the download directory by editing the `config.json` file's `download_folder` field.

```json
{
  "download_folder": "./downloads"
}
```

