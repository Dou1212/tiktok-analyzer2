from flask import Flask, request, jsonify, render_template
from google.cloud import storage
import uuid

app = Flask(__name__)

# Configura tu bucket de GCS
BUCKET_NAME = "tiktok-json-storage"  # Cambia por el nombre real de tu bucket
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

# Ruta principal para mostrar el formulario
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Ruta para subir JSON
@app.route("/upload", methods=["POST"])
def upload_json():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "" or not file.filename.endswith(".json"):
        return jsonify({"error": "Invalid file type"}), 400

    # Nomb
