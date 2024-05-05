# Add Songs to YouTube Music Playlist

This Python script reads song IDs from a CSV file, fetches song details from YouTube Music using the `ytmusicapi` library, and adds these songs to a playlist on YouTube Music.

## Requirements

- Python 3
- `ytmusicapi` library
- `pandas` library
- `tkinter` library

## Usage

1. Run the script using Python:

    ```bash
    python add_songs_to_ytmusic_playlist.py
    ```

2. When prompted, select a CSV file that contains song IDs.

3. Input the name of the column in the CSV file that contains the song IDs.

4. Authenticate with the YouTube Music API when prompted.

5. Choose whether to add songs to an existing playlist (input 'y') or create a new playlist (input 'n').

6. If you chose to create a new playlist, input the name of the new playlist.

7. If you chose to add songs to an existing playlist, select the playlist from the list.

The script will then fetch the song details for each song ID in the CSV file and add the songs to the specified playlist.

## Note

This script is intended to be run as a standalone file and not imported as a module.