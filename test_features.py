from spotify_client import get_spotify_client, search_song

# Step 1: create Spotify client
sp = get_spotify_client()

# Step 2: search for a known song
tracks = search_song("Blinding Lights", limit=1)

# Step 3: make sure we found something
if not tracks:
    print("No tracks found.")
    raise SystemExit

# Step 4: get the top result's track ID
track = tracks[0]
track_id = track["id"]

print("Testing track:")
print("Name:", track["name"])
print("Artist:", track["artist"])
print("Track ID:", track_id)
print()

# Step 5: try to request audio features
try:
    features = sp.audio_features([track_id])

    print("Raw audio_features response:")
    print(features)
    print()

    if not features or features[0] is None:
        print("Audio features request succeeded, but no feature data was returned.")
    else:
        f = features[0]
        print("Energy:", f.get("energy"))
        print("Tempo:", f.get("tempo"))
        print("Valence:", f.get("valence"))
        print("Danceability:", f.get("danceability"))
        print("Loudness:", f.get("loudness"))

except Exception as e:
    print("Audio features request failed.")
    print("Error type:", type(e).__name__)
    print("Error:", e)