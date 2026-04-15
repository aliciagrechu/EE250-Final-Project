from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    song = ""
    artist = ""
    mood = ""
    results = []

    if request.method == "POST":
        song = request.form.get("song", "").strip()
        artist = request.form.get("artist", "").strip()

        # Temporary placeholder mood for frontend testing.
        # Later, your backend/Spotify API will determine this automatically.
        if song or artist:
            mood = "Waiting for Spotify classification"

            # Temporary fake results so the UI has something to display.
            # Later, replace this with real Spotify search results.
            results = [
                {
                    "id": "1",
                    "name": song if song else "Unknown Song",
                    "artist": artist if artist else "Unknown Artist"
                },
                {
                    "id": "2",
                    "name": (song + " Remix") if song else "Sample Remix",
                    "artist": artist if artist else "Unknown Artist"
                }
            ]

    return render_template(
        "index.html",
        song=song,
        artist=artist,
        mood=mood,
        results=results
    )

if __name__ == "__main__":
    app.run(debug=True)