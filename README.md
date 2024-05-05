# Add Songs to YouTube Music Playlist

This Python script reads song IDs from a CSV file, fetches song details from YouTube Music using the `ytmusicapi` library, and adds these songs to a playlist on YouTube Music.

## Requirements

- Python 3
- `ytmusicapi` library
- `pandas` library
- `tkinter` library

## Usage

1. Run the script using Python. You can optionally use the `--csv` flag to specify the path to your CSV file:

    ```bash
    python add_songs_to_ytmusic_playlist.py --csv /path/to/your/file.csv
    ```

    If you don't use the `--csv` flag, you will be prompted to select a CSV file that contains song IDs.

2. Input the number of the column in the CSV file that contains the song IDs.

3. Authenticate with the YouTube Music API when prompted.

4. Choose whether to add songs to an existing playlist (input 'y') or create a new playlist (input 'n').

5. If you chose to create a new playlist, input the name of the new playlist.

6. If you chose to add songs to an existing playlist, select the playlist number from the list.

The script will then fetch the song details for each song ID in the CSV file, check if the song is already in the playlist, and add the songs to the specified playlist if they are not already present.

## Note

This script is intended to be run as a standalone file and not imported as a module.