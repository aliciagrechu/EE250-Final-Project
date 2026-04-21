<<<<<<< Updated upstream
#spotify_client.py: uses spotify to search for songs because it returns clean data that yt-dlp can use to find right youtube video, also uses playback so song will start playing on Spotify
#used Claude to understand how to use Spotify API and .env file to pass login information, and how to format tracks for yt - dlp 

#credentials for spotify API stored in .env and not hardcoded for security

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Reads SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI from .env so os.getenv() can find them
load_dotenv()

#builds authenticated spotify cleint, SpotifyOAuth handles login on first run, then caches token so subsequent runs don't require login
def get_spotify_client():
    client_id     = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri  = os.getenv("SPOTIPY_REDIRECT_URI")

    #if issue in .env file
    if not client_id or not client_secret or not redirect_uri:
        raise RuntimeError(
            "Missing Spotify credentials in .env — "
            "make sure SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, "
            "and SPOTIPY_REDIRECT_URI are all set."
        )

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            # user-read-playback-state lets us check which device is active;
            # user-modify-playback-state lets us actually start playback
            scope="user-read-playback-state user-modify-playback-state",
            open_browser=True,
            cache_path=".spotify_cache"
        )
    )

#search spotify for tracks matching query, track ID needed to start playback and pass to yt-dlp
def search_song(query, limit=5):
    sp = get_spotify_client()
    results = sp.search(q=query, type="track", limit=limit)


    tracks = []
    for track in results.get("tracks", {}).get("items", []):
        tracks.append({
            "id":          track["id"],
            "name":        track["name"],
            # artists is a list so join into one string
            "artist":      ", ".join(a["name"] for a in track["artists"]),
            "album":       track["album"]["name"],
            "popularity":  track.get("popularity", 0),   # 0–100 score
            "duration_ms": track.get("duration_ms", 0),
        })

    return tracks

#starts playback on user's active spotify device
def play_song(track_id: str):
    sp = get_spotify_client()

    # Check which devices are currently available
    devices = sp.devices().get("devices", [])
    if not devices:
        raise RuntimeError(
            "No active Spotify device found. "
            "Open Spotify on your phone or desktop and try again."
        )

    # Use whichever device is already active, or fall back to the first one
    active = next((d for d in devices if d["is_active"]), devices[0])

    sp.start_playback(
        device_id=active["id"],
        uris=[f"spotify:track:{track_id}"]  # Spotify URI format for a track
    )
    print(f"[spotify] Playing track {track_id} on device: {active['name']}")
=======
import os

from dotenv import load_dotenv  # loads variables from the .env file (client ID and client secret) into Python
import spotipy  # Spotify API wrapper for Python
from spotipy.oauth2 import SpotifyOAuth  # handles Spotify login (OAuth) so user doesn't have to log in more than once 


load_dotenv()  # actually loads the .env file so we can use its values


def get_spotify_client():
    # get credentials from the .env file
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    # if any credential is missing, stop and show an error
    if not client_id or not client_secret or not redirect_uri:
        raise RuntimeError("Missing Spotify environment variables in .env")

    # create and return a Spotify client object
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,          # your app's client ID
            client_secret=client_secret,  # your app's client secret
            redirect_uri=redirect_uri,    # where Spotify sends you after login
            scope="",                     # no special permissions needed for search
            open_browser=True,            # opens browser for login if needed
            cache_path=".spotify_cache"   # saves login token so you don't log in every time
        )
    )


def search_song(query, limit=5):
    # create a Spotify client (logs in if needed)
    sp = get_spotify_client()

    # send a search request to Spotify API
    results = sp.search(q=query, type="track", limit=limit)

    # create an empty list to store simplified track data
    tracks = []

    # loop through each track returned by Spotify
    for track in results.get("tracks", {}).get("items", []):
        # extract only the fields we care about and store them in a dictionary
        tracks.append({
            "id": track["id"],  # unique Spotify track ID
            "name": track["name"],  # song title
            "artist": ", ".join(artist["name"] for artist in track["artists"]),  # combine all artists into one string
            "album": track["album"]["name"],  # album name
            "popularity": track.get("popularity", 0),  # popularity score (0–100)
            "duration_ms": track.get("duration_ms", 0),  # song length in milliseconds
        })

    # return the cleaned list of track dictionaries
    return tracks
>>>>>>> Stashed changes
