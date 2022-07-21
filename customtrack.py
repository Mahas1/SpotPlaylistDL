import json
import os

from pathlib import Path

from src import misc


class CustomTrack:
    def __init__(self) -> None:
        self.root = (Path(__file__).parent.absolute())
        with open(os.path.join(self.root, "track_data", "custom_tracks_human.json")) as f:
            self.custom_tracks = json.load(f)
            self.clear_screen(prompt=False)
        self.print_ui()

    def add_custom_track(self):
        friendly_name = input("Enter Friendly Name: ")
        spotify_url = input("Enter Spotify URL: ")
        youtube_url = input("Enter YouTube URL: ")
        self.custom_tracks.append(
            {"friendly_name": friendly_name, "spotify_url": spotify_url, "youtube_url": youtube_url})
        self.flush_changes()

    def flush_changes(self):
        with open(os.path.join(self.root, "track_data", "custom_tracks_human.json"), "w") as f:
            json.dump(self.custom_tracks, f, indent=4)
        to_dump = {}
        with open(os.path.join(self.root, "track_data", "custom_tracks_human.json"), "r") as f:
            human = json.load(f)
        for entry in human:
            spot_url = entry["spotify_url"]
            track_id = misc.get_track_id(spot_url)
            youtube_url = entry["youtube_url"]
            to_dump[track_id] = youtube_url

        with open(os.path.join(self.root, "track_data", "custom_tracks_simple.json"), "w") as f:
            json.dump(to_dump, f, indent=4)

    def load_changes(self):
        with open(os.path.join(self.root, "track_data", "custom_tracks_human.json")) as f:
            self.custom_tracks = json.load(f)

    def print_tracks(self):
        for i, track in enumerate(self.custom_tracks):
            print(
                f"{i + 1}. {track['friendly_name']}\n\tSpotify: {track['spotify_url']}\n\tYouTube: {track['youtube_url']}")

    def remove_track(self):
        self.print_tracks()
        track_number = int(input("Enter Track Number: "))
        print(f"Removed: {self.custom_tracks.pop(track_number - 1)['friendly_name']}")
        self.flush_changes()

    def clear_screen(self, prompt=True):
        if prompt:
            input("Press any key to continue...")
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def push_to_git(self):
        os.system("git add track_data/custom_tracks_human.json")
        os.system("git add track_data/custom_tracks_simple.json")
        os.system("git commit -m \"Update Custom Tracks\"")
        os.system("git push")

    def pull_from_git(self):
        os.system("git pull")

    def print_ui(self):
        while True:
            print("""
1. Add Custom Track
2. Remove Custom Track
3. Print Custom Tracks
4. Push to Git
5. Pull from Git
6. Exit
            """)
            choice = input("Enter Choice: ")
            if choice == "1":
                self.clear_screen(prompt=False)
                self.add_custom_track()
                self.clear_screen()
            elif choice == "2":
                self.clear_screen(prompt=False)
                self.remove_track()
                self.clear_screen()
            elif choice == "3":
                self.clear_screen(prompt=False)
                self.print_tracks()
                self.clear_screen()
            elif choice == "4":
                self.clear_screen(prompt=False)
                self.push_to_git()
                self.clear_screen()
            elif choice == "5":
                self.clear_screen(prompt=False)
                self.pull_from_git()
                self.clear_screen()
            elif choice == "6":
                exit()
            else:
                print("Invalid Choice")
                self.clear_screen()


custom_track = CustomTrack()
