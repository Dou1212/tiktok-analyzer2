from flask import Flask, request, jsonify, render_template
import json
import uuid
import os

app = Flask(__name__)

# Ruta principal para mostrar el formulario
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Ruta para subir JSON y analizarlo
@app.route("/upload", methods=["POST"])
def upload_json():
    if "file" not in request.files:
        return "No se subió ningún archivo", 400

    file = request.files["file"]
    if file.filename == "" or not file.filename.endswith(".json"):
        return "Archivo inválido", 400

    # Guardar temporalmente en /tmp
    tmp_folder = "/tmp"
    filename = f"{uuid.uuid4()}.json"
    file_path = os.path.join(tmp_folder, filename)
    file.save(file_path)

    # Leer y analizar el JSON
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ejemplo: obtener primer like
    primer_like = data["Activity"]["Like List"]["ItemFavoriteList"][-1]["Link"]

    return f"Primer Like: {primer_like}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
