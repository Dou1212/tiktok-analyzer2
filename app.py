from flask import Flask, request, render_template
import json
import uuid
import os
import random
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
                error = "❌ Archivo inválido. Debe ser un archivo JSON"
            else:
                tmp_folder = "/tmp"
                filename = f"{uuid.uuid4()}.json"
                file_path = os.path.join(tmp_folder, filename)
                file.save(file_path)

                # Leer JSON con manejo de errores
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    error = "❌ Error: El archivo no es un JSON válido"
                    return render_template("index.html", error=error)
                except Exception as e:
                    error = f"❌ Error inesperado al leer el JSON: {str(e)}"
                    return render_template("index.html", error=error)

                # Subir a GCS (opcional)
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    gcs_filename = f"uploads/{timestamp}_{filename}"
                    upload_to_gcs(file_path, gcs_filename)
                except Exception as e:
                    print(f"❌ No se pudo subir a GCS: {e}")
                    gcs_filename = None

                # Obtener opciones seleccionadas
                options = {
                    'first_like': request.form.get('first_like') == 'on',
                    'last_like': request.form.get('last_like') == 'on',
                    'first_song': request.form.get('first_song') == 'on',
                    'last_song': request.form.get('last_song') == 'on',
                    'first_follower': request.form.get('first_follower') == 'on',
                    'last_follower': request.form.get('last_follower') == 'on',
                    'first_fav': request.form.get('first_fav') == 'on',
                    'last_fav': request.form.get('last_fav') == 'on',
                    'random_like': request.form.get('random_like') == 'on',
                    'random_song': request.form.get('random_song') == 'on',
                }

                # Analizar datos
                results = {}
                try:
                    if options['first_song']:
                        results['primera_song'] = data['Activity']['Favorite Sounds']['FavoriteSoundList'][-1]['Link']
                    if options['last_song']:
                        results['ultima_song'] = data['Activity']['Favorite Sounds']['FavoriteSoundList'][0]['Link']
                    if options['first_follower']:
                        results['primer_seguidor'] = data["Activity"]["Follower List"]["FansList"][-1]["UserName"]
                    if options['last_follower']:
                        results['ultimo_seguidor'] = data["Activity"]["Follower List"]["FansList"][0]["UserName"]
                    if options['first_like']:
                        results['primer_like'] = data["Activity"]["Like List"]["ItemFavoriteList"][-1]["Link"]
                    if options['last_like']:
                        results['ultimo_like'] = data["Activity"]["Like List"]["ItemFavoriteList"][0]["Link"]
                    if options['first_fav']:
                        results['primer_favvideo'] = data["Activity"]["Favorite Videos"]["FavoriteVideoList"][-1]["Link"]
                    if options['last_fav']:
                        results['ultimo_favvideo'] = data["Activity"]["Favorite Videos"]["FavoriteVideoList"][0]["Link"]
                    if options['random_like']:
                        like_list = data["Activity"]["Like List"]["ItemFavoriteList"]
                        if like_list:
                            results['random_like'] = random.choice(like_list)["Link"]
                    if options['random_song']:
                        song_list = data['Activity']['Favorite Sounds']['FavoriteSoundList']
                        if song_list:
                            results['random_song'] = random.choice(song_list)["Link"]
                    results['gcs_path'] = gcs_filename
                except Exception as e:
                    error = f"❌ Error inesperado al procesar los datos: {str(e)}"

                # Limpiar archivo temporal
                try:
                    os.remove(file_path)
                except:
                    pass

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
