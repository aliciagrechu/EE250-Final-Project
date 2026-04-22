#audio_features.py: searches Youtube and downloads audio as mp3 via yt- dlp. It then loads the audio signal and computes signal features using librosa. It will return those features as a dict for tone_classfier.py to use.
#used Claude to understand how to use yt - dlp for as subprocess and how to call librosa to get features


#import necessary libraries
import os
import subprocess
import numpy as np
import librosa


DOWNLOAD_DIR = "downloads" #folder where mp3s are saved
AUDIO_FORMAT = "mp3"

#downloads song and returns local file path
#yt-dlp is command-line tool to download from Youtube, call it as subprocess
def download_song(track_name: str, artist: str) -> str:
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # safe file name so OS doesn't intepret parts of name as a path, each song always maps to the same path
    safe_name = f"{track_name}_{artist}".replace(" ", "_").replace("/", "-")
    expected_file = os.path.join(DOWNLOAD_DIR, f"{safe_name}.{AUDIO_FORMAT}")

    # if we already downloaded this song, skip request
    if os.path.exists(expected_file):
        print(f"[download] Using cached file: {expected_file}")
        return expected_file

    #ytsearch1 tells yt-dlp to search Youtube and take first result
    query = f"ytsearch1:{track_name} {artist} official audio"
    #%(ext)s is a yt-dlp placeholder, fills in actual extension after we check .mp3 path exists
    output_template = os.path.join(DOWNLOAD_DIR, f"{safe_name}.%(ext)s")

    print(f"[download] Searching YouTube for: {track_name} – {artist}")

    cmd = [
        "py", "-m", "yt_dlp",
        "--extract-audio", #strip video stream, keep audio only
        "--audio-format", AUDIO_FORMAT, #convert to mp3 regardless of source format
        "--audio-quality", "0", # 0 is best available quality
        "--output", output_template,
        "--no-playlist", #if returns playlist, take only first item
        "--quiet", #suppress progress bars
        "--js-runtimes", "node", #JS engine used to parse Youtube pages
        query
    ]

    #run yt-dlp as subprocess, capture whatever it wants to print to terminal, stores as a string
    result = subprocess.run(cmd, capture_output=True, text=True)

    #if doesn't return 0, something went wrong 
    if result.returncode != 0:
        raise RuntimeError(
            f"yt-dlp failed for '{track_name}' by '{artist}'.\n"
            f"stderr: {result.stderr.strip()}"
        )

    #make sure file landed where we expected
    if not os.path.exists(expected_file):
        raise RuntimeError(
            f"yt-dlp succeeded but expected file not found: {expected_file}\n"
            f"Check the downloads/ folder to see what was actually saved."
        )

    print(f"[download] Saved to: {expected_file}")
    return expected_file

#loads audio file and extracts features for tone classifer 
def extract_features(filepath: str) -> dict:
    

    print(f"[features] Loading audio: {filepath}")

    #22050 is standard sample rate for audio ML, duration = 60 so we dond't prcoess full clip
    y, sr = librosa.load(filepath, sr=22050, duration=60)
    print(f"[features] Loaded {len(y)/sr:.1f}s of audio at {sr} Hz")

    #tempo: librosa estimates bpm by looking for repeat energy peaks
    # atleast_1d handles both old (scalar) and new (array) librosa return types
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])

    #energy: using RMS to find average loduness of signal 
    energy = float(np.mean(librosa.feature.rms(y=y)))
    
    #spectral centroid: where most of the sound energy lives on frequency axis
    spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    
    #zero crossing rate: how many times per second the waveform changes signs
    zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(y)))


    features = {
        "tempo":              tempo,
        "energy":             energy,
        "spectral_centroid":  spectral_centroid,
        "zero_crossing_rate": zero_crossing_rate
    }

    print("[features] Extracted:")
    for k, v in features.items():
        print(f"           {k:25s} = {v:.4f}")

    return features

#pipeline wrapper: signle call that downloads, extratcs, and returns information, called by app.py
def get_features_for_song(track_name: str, artist: str) -> dict:
    filepath = download_song(track_name, artist)
    return extract_features(filepath)

#test to ensure pipekline works, run with python audio_features.py
if __name__ == "__main__":

    test_songs = [
        ("In My Life",      "The Beatles"),    # expected: warm
        ("Gimme Shelter",   "Rolling Stones"),  # expected: dark
        ("Good Vibrations", "Beach Boys"),      # expected: chill/dance
    ]

    for name, artist in test_songs:
        print(f"\n{'='*55}")
        print(f"Testing: {name} — {artist}")
        print('='*55)
        try:
            feats = get_features_for_song(name, artist)
            print(f"[OK] Feature extraction succeeded for '{name}'")
        except Exception as e:
            print(f"[ERROR] {e}")
