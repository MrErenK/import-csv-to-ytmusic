import pandas as pd
import tkinter as tk
from tkinter import filedialog
from ytmusicapi import YTMusic
import ytmusicapi as ytmapi
import os
import argparse
from typing import Generator, Any

# Constants
AUTH_FILE = "headers_auth.json"
PLAYLIST_IDS_TO_NOT_SHOW = ["LM", "SE"]

def get_file_path(args: argparse.Namespace) -> str:
    if args.csv:
        return args.csv
    else:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        return file_path

def validate_file_path(file_path: str) -> None:
    if not file_path:
        raise ValueError("No file selected.")
    if not file_path.lower().endswith('.csv'):
        raise ValueError("The selected file is not a CSV file.")

def read_csv_file(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError("The selected file does not exist.")
    except pd.errors.EmptyDataError:
        raise ValueError("The selected file is empty.")
    except pd.errors.ParserError:
        raise ValueError("The selected file could not be parsed as a CSV file.")
    return df

def get_id_column(df: pd.DataFrame) -> str:
    print("Columns in the CSV file:")
    for i, column in enumerate(df.columns, start=1):
        print(f"{i}. {column}")
    while True:
        column_number = input("Enter the number of the column that contains song IDs: ")
        if column_number.isdigit() and 1 <= int(column_number) <= len(df.columns):
            return df.columns[int(column_number) - 1]
        else:
            print("Invalid input. Please enter a valid number.")

def get_unique_song_ids(df: pd.DataFrame, id_column: str) -> Generator[Any, Any, Any]:
    seen = set()
    for value in df[id_column]:
        if value not in seen:
            seen.add(value)
            yield value

def authenticate_ytmusic() -> YTMusic:
    auth_file = AUTH_FILE
    if not os.path.isfile(auth_file):
        print("Please login to your YouTube Music account.")
        input("Press Enter to continue...")
        ytmapi.setup_oauth(filepath=auth_file, open_browser=True)
    try:
        ytmusic = YTMusic(auth_file)
    except Exception as e:
        print(f"Error initializing YTMusic API: {e}")
        exit()
    return ytmusic

def get_playlist_choice() -> str:
    while True:
        choice = input("Do you want to add the songs to an existing playlist, create a new one, or add to Liked Songs? (existing/e, new/n, liked/l): ")
        if choice.lower() in ['existing', 'e', 'ex', 'exist']:
            return 'existing'
        elif choice.lower() in ['new', 'n', 'ne', 'create']:
            return 'new'
        elif choice.lower() in ['liked', 'l', 'like', 'likes']:
            return 'liked'
        else:
            print("Invalid choice. Please enter 'existing', 'new', or 'liked'.")

def create_or_get_playlist(ytmusic: YTMusic, values) -> str:
    choice = get_playlist_choice()
    if choice == 'liked':
        return get_liked_playlist(ytmusic)
    elif choice == 'existing':
        return get_existing_playlist(ytmusic)
    elif choice == 'new':
        return create_playlist(ytmusic)

def create_playlist(ytmusic: YTMusic) -> str:
    playlist_name = input("Enter the playlist name to create: ")
    playlist_description = input("Enter a description for the playlist: ")
    try:
        playlist_id = ytmusic.create_playlist(playlist_name, description=playlist_description)
    except Exception as e:
        print(f"Error creating playlist: {e}")
        exit()
    print(f"New playlist '{playlist_name}' created.")
    return playlist_id

def get_existing_playlist(ytmusic: YTMusic, prompt: str = "Enter the number of the playlist to add the songs to: ") -> str:
    if not ytmusic:
        print("Error: YTMusic object not found.")
        exit()
    try:
        playlists = [playlist for playlist in ytmusic.get_library_playlists() if playlist['playlistId'] not in PLAYLIST_IDS_TO_NOT_SHOW]
    except Exception as e:
        print(f"Error getting library playlists: {e}")
        exit()
    if not playlists:
        print("No existing playlists found.")
        return create_playlist(ytmusic)
    print("Existing playlists:")
    for i, playlist in enumerate(playlists, start=1):
        print(f"{i}. Name: {playlist['title']}, ID: {playlist['playlistId']}")
    while True:
        playlist_number = input(prompt)
        if playlist_number.isdigit() and 1 <= int(playlist_number) <= len(playlists):
            return playlists[int(playlist_number) - 1]['playlistId']
        else:
            print("Invalid input. Please enter a valid number.")

def get_playlist_id(ytmusic: YTMusic, playlist_name: str) -> str:
    try:
        playlists = ytmusic.get_library_playlists()
    except Exception as e:
        print(f"Error getting library playlists: {e}")
        exit()
    playlist_id = None
    for playlist in playlists:
        if playlist['title'] == playlist_name or playlist['playlistId'] == playlist_name:
            playlist_id = playlist['playlistId']
            break
    if playlist_id is None:
        print("Error: The specified playlist name or ID does not exist.")
        exit()
    return playlist_id

def get_playlist_songs(ytmusic: YTMusic, playlist_id: str) -> list:
    try:
        playlist = ytmusic.get_playlist(playlist_id, limit=None)
        playlist_songs = {song['videoId']: song for song in playlist['tracks']}
        return list(playlist_songs.values())
    except Exception as e:
        print(f"Error getting songs from playlist: {e}")
        exit()

def get_playlist_name(ytmusic: YTMusic, playlist_id: str) -> str:
    try:
        playlists = ytmusic.get_library_playlists()
    except Exception as e:
        print(f"Error getting library playlists: {e}")
        exit()
    playlist_name = None
    for playlist in playlists:
        if playlist['playlistId'] == playlist_id:
            playlist_name = playlist['title']
            break
    if playlist_name is None:
        print("Error: The specified playlist ID does not exist.")
        exit()
    return playlist_name

def get_liked_playlist(ytmusic: YTMusic) -> str:
    try:
        return 'LM'
    except Exception as e:
        print("Error: Liked Songs playlist not found.")
        exit()

def add_to_liked_songs(ytmusic: YTMusic, values: list) -> None:
    try:
        confirmation = input("Are you sure you want to add these songs to Liked Songs? (yes/no): ").strip().lower()
        if confirmation not in ["yes", "y"]:
            print("Operation canceled.")
            return

        liked_songs = ytmusic.get_liked_songs(limit=None)
        liked_song_ids = {song['videoId']: song['title'] for song in liked_songs['tracks']}
        total_liked_songs = len(liked_songs['tracks'])

        print(f"Total number of songs in Liked Songs: {total_liked_songs}")
        print("Adding songs to Liked Songs...")

        added_song_count = 0
        for value in values:
            if value in liked_song_ids:
                print(f"Song: {liked_song_ids[value]} is already in Liked Songs. Skipping...")
                continue
            try:
                song_info = ytmusic.get_song(value)
                if 'videoDetails' not in song_info:
                    print(f"Error: 'videoDetails' not found for song with ID {value}")
                    continue

                song_details = song_info['videoDetails']
                song_title = song_details.get('title', 'Unknown Title')
                song_author = song_details.get('author', 'Unknown Author')
                song_id = song_details.get('videoId', 'Unknown ID')

                print(f"Song: {song_title}, Artist: {song_author}")
                print(f"URL: https://music.youtube.com/watch?v={song_id}")
                print("Adding to Liked Songs...")
                print("")
                ytmusic.rate_song(song_id, 'LIKE')
                added_song_count += 1
            except Exception as e:
                print(f"Error adding song {value} to Liked Songs: {e}")

        print(f"Total number of songs added to Liked Songs: {added_song_count}")
        print(f"Total number of songs in Liked Songs: {total_liked_songs + added_song_count}")
    except Exception as e:
        print(f"Error retrieving liked songs: {e}")
    print("Finished adding songs to Liked Songs.")

def process_song(ytmusic: YTMusic, value: str, playlist_id: str, playlist_name: str) -> int:
    try:
        song_info = ytmusic.get_song(value)
        if 'videoDetails' not in song_info:
            print(f"Error: 'videoDetails' not found for song with ID {value}")
            return 0
        
        song_details = song_info['videoDetails']
        song_title = song_details.get('title', 'Unknown Title')
        song_author = song_details.get('author', 'Unknown Author')
        song_id = song_details.get('videoId', 'Unknown ID')

        playlist_songs = {song['videoId'] for song in get_playlist_songs(ytmusic, playlist_id)}
        if value in playlist_songs:
            print(f"Song: {song_title}, Artist: {song_author} has already been added to the playlist \"{playlist_name}\". Skipping...")
            return 0
        print(f"Song: {song_title}, Artist: {song_author}")
        print(f"URL: https://music.youtube.com/watch?v={song_id}")
        print(f"Adding to playlist: {playlist_name}, {playlist_id}")
        print("")
        try:
            ytmusic.add_playlist_items(playlist_id, [song_id])
        except Exception as e:
            print(f"Error adding song {song_title} to playlist: {e}")
            return 0
        return 1
    except Exception as e:
        print(f"Error processing song with ID {value}: {e}")
        return 0

def process_values(ytmusic: YTMusic, values: list, playlist_id: str, playlist_name: str, delete_duplicates: bool, track_count: int) -> None:
    if delete_duplicates:
        delete_duplicate_song(ytmusic, playlist_id, auto_delete=True)

    print(f"Total number of songs in the playlist: {track_count}")
    print(f"Adding songs to playlist: {playlist_name}...")

    song_count = 0
    for value in values:
        song_count += process_song(ytmusic, value, playlist_id, playlist_name)

    print(f"Total number of songs added: {song_count}")
    print(f"Total number of songs in the playlist: {track_count + song_count}")

    if delete_duplicates:
        delete_duplicate_song(ytmusic, playlist_id, auto_delete=True)

def delete_duplicate_song(ytmusic: YTMusic, playlist_id: str, auto_delete: bool = False) -> None:
    try:
        playlist = ytmusic.get_playlist(playlist_id, limit=None)

        song_counts = {}
        for item in playlist['tracks']:
            if item['videoId'] in song_counts:
                song_counts[item['videoId']] += 1
            else:
                song_counts[item['videoId']] = 1

        print(f"Checking for duplicate songs in playlist: {playlist['title']}...")
        duplicate_songs = {song_id: count for song_id, count in song_counts.items() if count > 1}
        if not duplicate_songs:
            print("No duplicate songs found in the playlist.")
            return
        print("Duplicate songs:")
        for song_id, count in duplicate_songs.items():
            song = next((item for item in playlist['tracks'] if item['videoId'] == song_id), None)
            if song:
                print(f"{song['title']} by {song['artists'][0]['name']} ({count} duplicates)")
        if auto_delete or input("Do you want to remove the duplicate songs? (y/n): ").lower() == 'y':
            print("Deleting duplicate songs...")
            for song_id, count in duplicate_songs.items():
                for _ in range(count - 1):  # We leave one instance of the song, so we remove count - 1 instances
                    song = next((item for item in playlist['tracks'] if item['videoId'] == song_id), None)
                    if song:
                        ytmusic.remove_playlist_items(playlist_id, [{'videoId': song['videoId'], 'setVideoId': song['setVideoId']}])
                        print(f"Duplicate song: {song['title']} by {song['artists'][0]['name']} has been deleted from the playlist.")
        else:
            print("No duplicate songs were removed.")
    except Exception as e:
        print(f"Error deleting duplicate songs from playlist: {e}")

def check_duplicates(ytmusic: YTMusic, delete_duplicates: bool) -> None:
    playlist_name = get_existing_playlist(ytmusic, prompt="Enter the number of the playlist to check the duplicates: ")
    playlist_id = get_playlist_id(ytmusic, playlist_name)
    if delete_duplicates:
        delete_duplicate_song(ytmusic, playlist_id, auto_delete=True)
    else:
        delete_duplicate_song(ytmusic, playlist_id)

def get_playlist_info(ytmusic: YTMusic, values: list, args: argparse.Namespace) -> None:
    if args.add_to_liked:
        add_to_liked_songs(ytmusic, values)
    else:
        choice = get_playlist_choice()
        if choice == 'liked':
            add_to_liked_songs(ytmusic, values)
        elif choice == 'existing':
            playlist_id = get_existing_playlist(ytmusic)
        elif choice == 'new':
            playlist_id = create_playlist(ytmusic)
        else:
            raise ValueError("Invalid playlist choice.")

        playlist_name = get_playlist_name(ytmusic, playlist_id)
        track_count = len(get_playlist_songs(ytmusic, playlist_id))
        process_values(ytmusic, values, playlist_id, playlist_name, args.delete_duplicates, track_count)

def main() -> None:
    try:
        parser = argparse.ArgumentParser(description='Add songs to YouTube Music playlist from a CSV file.')
        parser.add_argument('--csv', type=str, help='Path to the CSV file.')
        parser.add_argument('--delete-duplicates', '-dd', action='store_true', help='Delete duplicate songs from the playlist.')
        parser.add_argument('--check-duplicates', '-cd', action='store_true', help='Check for duplicate songs in a playlist.')
        parser.add_argument('--add-to-liked', '-al', action='store_true', help='Add songs to Liked Songs instead of a playlist.')
        args = parser.parse_args()

        ytmusic = authenticate_ytmusic()

        if args.check_duplicates:
            if args.csv:
                print("Cannot check for duplicates when --csv flag is provided.")
                exit()
            check_duplicates(ytmusic, args.delete_duplicates)
        else:
            file_path = get_file_path(args)
            validate_file_path(file_path)
            df = read_csv_file(file_path)
            id_column = get_id_column(df)
            values = list(get_unique_song_ids(df, id_column))
            print(f"Total number of unique songs found in CSV file: {len(values)}")
            get_playlist_info(ytmusic, values, args)

    except KeyboardInterrupt:
        print("")
        print("Exiting...")
        exit()

if __name__ == "__main__":
    main()