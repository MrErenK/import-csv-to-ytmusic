import pandas as pd
import tkinter as tk
from tkinter import filedialog
from ytmusicapi import YTMusic as ytm
import ytmusicapi as ytmapi
import os
import argparse

def get_file_path(args):
    if args.csv:
        return args.csv
    else:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        return file_path

def validate_file_path(file_path):
    if not file_path:
        print("No file selected. Exiting...")
        exit()
    if not file_path.lower().endswith('.csv'):
        print("Error: The selected file is not a CSV file.")
        exit()

def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("Error: The selected file does not exist.")
        exit()
    except pd.errors.EmptyDataError:
        print("Error: The selected file is empty.")
        exit()
    except pd.errors.ParserError:
        print("Error: The selected file could not be parsed as a CSV file.")
        exit()
    return df

def get_id_column(df):
    print("Columns in the CSV file:")
    for i, column in enumerate(df.columns, start=1):
        print(f"{i}. {column}")
    while True:
        column_number = input("Enter the number of the column that contains song IDs: ")
        if column_number.isdigit() and 1 <= int(column_number) <= len(df.columns):
            return df.columns[int(column_number) - 1]
        else:
            print("Invalid input. Please enter a valid number.")

def authenticate_ytmusic():
    if not os.path.isfile("headers_auth.json"):
        print("Please login to your YouTube Music account.")
        input("Press Enter to continue...")
        ytmapi.setup_oauth(filepath="headers_auth.json", open_browser=True)
    try:
        ytmusic = ytm("headers_auth.json")
    except Exception as e:
        print(f"Error initializing YTMusic API: {e}")
        exit()
    return ytmusic

def get_playlist_name():
    getPlayListName = ''
    while getPlayListName.lower() not in ['y', 'n']:
        getPlayListName = input("Do you want to add the songs to an existing playlist one or create a new one? (y/n): ")
    return getPlayListName

def create_playlist(ytmusic):
    playListName = input("Enter the playlist name to create: ")
    try:
        ytmusic.create_playlist(playListName, description="Playlist created using ytmusicapi.")
    except Exception as e:
        print(f"Error creating playlist: {e}")
        exit()
    print(f"New playlist '{playListName}' created.")
    return playListName

def get_existing_playlist(ytmusic):
    try:
        playlists = [playlist for playlist in ytmusic.get_library_playlists() if playlist['playlistId'] != 'SE']
    except Exception as e:
        print(f"Error getting library playlists: {e}")
        exit()
    if not playlists:
        print("No existing playlists found.")
        return create_playlist(ytmusic)
    print("Existing playlists:")
    for i, playlist in enumerate(playlists, start=1):
        if playlist['playlistId'] != 'SE':
            print(f"{i}. Name: {playlist['title']}, ID: {playlist['playlistId']}")
            print("")
    while True:
        playlist_number = input("Enter the number of the playlist to add the songs to: ")
        if playlist_number.isdigit() and 1 <= int(playlist_number) <= len(playlists):
            return playlists[int(playlist_number) - 1]['title']
        else:
            print("Invalid input. Please enter a valid number.")

def get_playlist_id(ytmusic, playListName):
    try:
        new_playlists = ytmusic.get_library_playlists()
    except Exception as e:
        print(f"Error getting library playlists: {e}")
        exit()
    playListID = None
    for playlist in new_playlists:
        if playlist['title'] == playListName or playlist['playlistId'] == playListName:
            playListID = playlist['playlistId']
            break
    if playListID is None:
        print("Error: The specified playlist name or ID does not exist.")
        exit()
    return playListID

def process_values(ytmusic, values, playListID, playListName):
    for value in values:
        try:
            video_details = ytmusic.get_song(value)
            if video_details:
                song_title = video_details['videoDetails']['title']
                search_results = ytmusic.search(song_title, filter='songs', limit=1)
                if search_results:
                    song = search_results[0]
                    title = song['title']
                    print(f"Song: {title}, Artist: {song['artists'][0]['name']}")
                    print(f"URL: https://music.youtube.com/watch?v={song['videoId']}")
                    print(f"Adding to playlist {playListName}, {playListID}")
                    ytmusic.add_playlist_items(playListID, [song['videoId']])
                    print("")
                else:
                    print(f"No results found for value: {value}")
                    print("")
            else:
                print(f"No video details found for value: {value}")
                print("")
        except Exception as e:
            print(f"An error occurred while processing the value '{value}': {e}")
            print("")

def main():
    try:
        parser = argparse.ArgumentParser(description='Add songs to YouTube Music playlist from a CSV file.')
        parser.add_argument('--csv', type=str, help='Path to the CSV file.')
        args = parser.parse_args()

        file_path = get_file_path(args)
        validate_file_path(file_path)
        df = read_csv_file(file_path)
        id_column = get_id_column(df)
        values = df[id_column].unique()
        ytmusic = authenticate_ytmusic()
        getPlayListName = get_playlist_name()
        if getPlayListName.lower() == 'n':
            playListName = create_playlist(ytmusic)
        elif getPlayListName.lower() == 'y':
            playListName = get_existing_playlist(ytmusic)
        else:
            print("Invalid input. Exiting...")
            exit()
        playListID = get_playlist_id(ytmusic, playListName)
        process_values(ytmusic, values, playListID, playListName)
    except KeyboardInterrupt:
        print("")
        print("Exiting...")
        exit()

if __name__ == "__main__":
    main()