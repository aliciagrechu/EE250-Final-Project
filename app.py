from flask import Flask, render_template, request
import traceback

from spotify_client import search_song, play_song
from audio_features import get_features_for_song
from tone_classifier import predict_tone, TONE_COLORS
from mqtt_publisher import publish_tone

app = Flask(__name__)

def rgb_to_hex(rgb: tuple) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


@app.route("/", methods=["GET", "POST"])
def index():
    search_song_val = ""
    search_artist = ""

    selected_song = ""
    selected_artist = ""
    mood = ""
    color = "#1DB954"  # default green
    scores = {}

    results = []
    selected_id = ""
    error = ""

    if request.method == "POST":
        action = request.form.get("action", "search")

        search_song_val = request.form.get("song", "").strip()
        search_artist   = request.form.get("artist", "").strip()

        if action == "search":
            # DEBUGGING
            print("SEARCH ACTION HIT")
            print("song:", search_song_val)
            print("artist:", search_artist)

            if search_song_val or search_artist:
                query = f"{search_song_val} {search_artist}".strip()
                try:
                    tracks = search_song(query, limit=5)
                    # Spotify search_song returns id, name, artist, album, popularity, duration_ms
                    # index.html also checks song_result.image — add it (None if not present)
                    results = [
                        {
                            "id":     t["id"],
                            "name":   t["name"],
                            "artist": t["artist"],
                            "album":  t["album"],
                            "image":  t.get("image"),   # album art URL if available
                        }
                        for t in tracks
                    ]
                except Exception as e:
                    error = f"Spotify search failed: {e}"

        elif action == "select":
            selected_id     = request.form.get("selected_id", "")
            selected_song   = request.form.get("selected_song", "").strip()
            selected_artist = request.form.get("selected_artist", "").strip()

            # Restore search results so they stay visible after selection
            # (passed back as hidden fields from the form)
            import json
            raw_results = request.form.get("results_json", "[]")
            try:
                results = json.loads(raw_results)
            except Exception:
                results = []

            if selected_song:
                try:
                    # 1. Download audio from YouTube and extract features
                    features = get_features_for_song(selected_song, selected_artist)

                    # 2. Classify tone
                    tone, scores = predict_tone(features)
                    mood = tone.capitalize()
                    color = rgb_to_hex(TONE_COLORS[tone])

                    # 3. Publish tone to RPi LEDs via MQTT
                    mqtt_ok = publish_tone(tone)
                    if not mqtt_ok:
                        error = "LED update failed: MQTT broker unreachable. Check that the Raspberry Pi is on and mosquitto is running."

                    # 4. Start Spotify playback
                    if selected_id:
                        try:
                            play_song(selected_id)
                        except RuntimeError as e:
                            # Surface playback errors but don't hide the mood result
                            error = (error + " | " if error else "") + f"Spotify playback failed: {e}"

                except Exception as e:
                    error = f"Analysis failed: {e}\n{traceback.format_exc()}"

    return render_template(
        "index.html",
        search_song=search_song_val,
        search_artist=search_artist,
        selected_song=selected_song,
        selected_artist=selected_artist,
        mood=mood,
        color=color,
        scores=scores,
        results=results,
        selected_id=selected_id,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)