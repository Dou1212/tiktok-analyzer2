from flask import Flask, request, jsonify, render_template
import json
import os
import uuid

app = Flask(__name__)

# Ruta principal (formulario)
@app.route("/")
def index():
    return render_template("index.html")

# Ruta para subir JSON (solo lo guarda temporalmente)
@app.route("/upload", methods=["POST"])
def upload_json():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "" or not file.filename.endswith(".json"):
        return jsonify({"error": "Invalid file type"}), 400

    # Carpeta temporal de Cloud Run
    tmp_folder = "/tmp"
    filename = f"{uuid.uuid4()}.json"
    file_path = os.path.join(tmp_folder, filename)

    # Guarda el JSON temporalmente
    file.save(file_path)

    # Procesar JSON con tus scripts (ejemplo)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    primer_like = data["Activity"]["Like List"]["ItemFavoriteList"][-1]["Link"]

    return jsonify({"primer_like": primer_like, "temp_path": file_path})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
