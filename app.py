from flask import Flask, request, jsonify
from google.cloud import storage
import uuid

app = Flask(__name__)

# Configura tu bucket
BUCKET_NAME = "tiktok-json-storage"  # Cambia por el nombre real de tu bucket
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

@app.route("/upload", methods=["POST"])
def upload_json():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "" or not file.filename.endswith(".json"):
        return jsonify({"error": "Invalid file type"}), 400

    # Nombre único para evitar sobreescrituras
    filename = f"{uuid.uuid4()}.json"

    # Subir a GCS
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type="application/json")

    return jsonify({"message": "JSON uploaded successfully", "gcs_path": f"gs://{BUCKET_NAME}/{filename}"})
