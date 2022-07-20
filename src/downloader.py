import threading
import os

import spotdl


class Downloader:
    def __init__(self, downloader: spotdl.download.downloader.Downloader):
        self.downloader = downloader
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(os.cpu_count())

    def download(self, song_object: spotdl.types.Song):
        self.semaphore.acquire()
        try:
            self.downloader.search_and_download(song_object)
            print(f"Download Success: {song_object.name}")
        except Exception as e:
            print(f"Download Failed - {song_object.name} - {type(e).__name__}: {e}")
        self.semaphore.release()
