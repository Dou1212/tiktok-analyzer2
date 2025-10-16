from flask import Flask, request, render_template
import json
import uuid
import os
from google.cloud import storage
from datetime import datetime

app = Flask(__name__)

# Configuración del bucket
BUCKET_NAME = "tiktok_guarda_jsonn"

def upload_to_gcs(file_path, destination_blob_name):
    """Sube un archivo a Google Cloud Storage"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        
        blob.upload_from_filename(file_path)
        print(f"✅ Archivo subido a gs://{BUCKET_NAME}/{destination_blob_name}")
        return True
    except Exception as e:
        print(f"❌ Error al subir a GCS: {e}")
        return False

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
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Subir a Google Cloud Storage
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    gcs_filename = f"uploads/{timestamp}_{filename}"
                    upload_to_gcs(file_path, gcs_filename)

                    # Analizar datos
                    results = {
                        "primera_song": data['Activity']['Favorite Sounds']['FavoriteSoundList'][-1]['Link'],
                        "ultima_song": data['Activity']['Favorite Sounds']['FavoriteSoundList'][0]['Link'],
                        "primer_seguidor": data["Activity"]["Follower List"]["FansList"][-1]["UserName"],
                        "ultimo_seguidor": data["Activity"]["Follower List"]["FansList"][0]["UserName"],
                        "primer_like": data["Activity"]["Like List"]["ItemFavoriteList"][-1]["Link"],
                        "ultimo_like": data["Activity"]["Like List"]["ItemFavoriteList"][0]["Link"],
                        "primer_favvideo": data["Activity"]["Favorite Videos"]["FavoriteVideoList"][-1]["Link"],
                        "ultimo_favvideo": data["Activity"]["Favorite Videos"]["FavoriteVideoList"][0]["Link"],
                        "gcs_path": gcs_filename
                    }
                    
                    # Limpiar archivo temporal
                    os.remove(file_path)
                    
                except Exception as e:
                    error = f"❌ Error al procesar el archivo: {str(e)}"

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)