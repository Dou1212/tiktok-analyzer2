from flask import Flask, request, render_template
import json
import uuid
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None

    if request.method == "POST":
        if "file" not in request.files:
            error = "❌ No se subió ningún archivo"
        else:
            file = request.files["file"]
            if file.filename == "" or not file.filename.endswith(".json"):
                error = "❌ Archivo inválido"
            else:
                # Guardar temporalmente
                tmp_folder = "/tmp"
                filename = f"{uuid.uuid4()}.json"
                file_path = os.path.join(tmp_folder, filename)
                file.save(file_path)

                # Leer JSON
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Analizar datos
                results = {
                    "primera_song": data['Activity']['Favorite Sounds']['FavoriteSoundList'][-1]['Link'],
                    "ultima_song": data['Activity']['Favorite Sounds']['FavoriteSoundList'][0]['Link'],
                    "primer_seguidor": data["Activity"]["Follower List"]["FansList"][-1]["UserName"],
                    "ultimo_seguidor": data["Activity"]["Follower List"]["FansList"][0]["UserName"],
                    "primer_like": data["Activity"]["Like List"]["ItemFavoriteList"][-1]["Link"],
                    "ultimo_like": data["Activity"]["Like List"]["ItemFavoriteList"][0]["Link"],
                    "primer_favvideo": data["Activity"]["Favorite Videos"]["FavoriteVideoList"][-1]["Link"],
                    "ultimo_favvideo": data["Activity"]["Favorite Videos"]["FavoriteVideoList"][0]["Link"]
                }

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
