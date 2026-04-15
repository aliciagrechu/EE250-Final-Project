from flask import Flask, render_template, request

app = Flask(__name__)

# Temporary mood/color logic for frontend testing.
# Later, your Spotify backend can replace this with real classification.
def classify_mood(song_name: str):
    name = song_name.lower()

    if "remix" in name or "dance" in name or "party" in name:
        return "Energetic", "#ff4fa3"
    elif "love" in name or "summer" in name or "happy" in name:
        return "Happy", "#f59e0b"
    elif "night" in name or "dark" in name or "blue" in name:
        return "Moody", "#3b82f6"
    else:
        return "Chill", "#8b5cf6"


@app.route("/", methods=["GET", "POST"])
def index():
    search_song = ""
    search_artist = ""

    selected_song = ""
    selected_artist = ""
    mood = ""
    color = "#f59e0b"

    results = []
    selected_id = ""

    if request.method == "POST":
        action = request.form.get("action", "search")

        # Keep the search box values after submit
        search_song = request.form.get("song", "").strip()
        search_artist = request.form.get("artist", "").strip()

        # Temporary fake results for frontend testing
        if search_song or search_artist:
            base_song = search_song if search_song else "Unknown Song"
            base_artist = search_artist if search_artist else "Unknown Artist"

            results = [
                {"id": "1", "name": base_song, "artist": base_artist},
                {"id": "2", "name": f"{base_song} Remix", "artist": base_artist},
                {"id": "3", "name": f"{base_song} Live", "artist": base_artist},
            ]

        if action == "select":
            selected_id = request.form.get("selected_id", "")

            # Recover the selected track info from hidden inputs
            selected_song = request.form.get("selected_song", "").strip()
            selected_artist = request.form.get("selected_artist", "").strip()

            if selected_song:
                mood, color = classify_mood(selected_song)

    return render_template(
        "index.html",
        search_song=search_song,
        search_artist=search_artist,
        selected_song=selected_song,
        selected_artist=selected_artist,
        mood=mood,
        color=color,
        results=results,
        selected_id=selected_id
    )


if __name__ == "__main__":
    app.run(debug=True)