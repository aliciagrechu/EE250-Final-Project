print("STARTING APP")
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    mode = "mood"

    if request.method == "POST":
        query = request.form.get("query")
        mode = request.form.get("mode")

    return render_template("index.html", query=query, mode=mode)

if __name__ == "__main__":
    app.run(debug=True)