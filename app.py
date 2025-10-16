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
        return True
    except Exception as e:
        print(f"Error al subir a GCS: {e}")
        return False

def safe_get(obj, keys):
    """Navega por claves anidadas de forma segura"""
    for k in keys:
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj

def extract_field(item, candidates):
    """Extrae el primer campo válido de una lista de candidatos"""
    if not isinstance(item, dict):
        return None
    for c in candidates:
        if c in item and item[c]:
            return item[c]
    return None

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
                # Guardar temporalmente
                tmp_folder = "/tmp"
                filename = f"{uuid.uuid4()}.json"
                file_path = os.path.join(tmp_folder, filename)
                file.save(file_path)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Subir a Google Cloud Storage
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    gcs_filename = f"uploads/{timestamp}_{filename}"
                    upload_to_gcs(file_path, gcs_filename)

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

                    results = {}
                    link_fields = ["Link", "link", "url", "URL"]
                    username_fields = ["UserName", "username", "user_name"]

                    # Primera canción
                    if options['first_song']:
                        sounds = safe_get(data, ["Your Activity", "Favorite Sounds", "FavoriteSoundList"])
                        if sounds and len(sounds) > 0:
                            results['primera_song'] = extract_field(sounds[-1], link_fields)

                    # Última canción
                    if options['last_song']:
                        sounds = safe_get(data, ["Your Activity", "Favorite Sounds", "FavoriteSoundList"])
                        if sounds and len(sounds) > 0:
                            results['ultima_song'] = extract_field(sounds[0], link_fields)

                    # Primer seguidor
                    if options['first_follower']:
                        fans = safe_get(data, ["Your Activity", "Follower", "FansList"])
                        if fans and len(fans) > 0:
                            results['primer_seguidor'] = extract_field(fans[-1], username_fields)

                    # Último seguidor
                    if options['last_follower']:
                        fans = safe_get(data, ["Your Activity", "Follower", "FansList"])
                        if fans and len(fans) > 0:
                            results['ultimo_seguidor'] = extract_field(fans[0], username_fields)

                    # Primer like
                    if options['first_like']:
                        likes = safe_get(data, ["Your Activity", "Like List", "ItemFavoriteList"])
                        if likes and len(likes) > 0:
                            results['primer_like'] = extract_field(likes[-1], link_fields)

                    # Último like
                    if options['last_like']:
                        likes = safe_get(data, ["Your Activity", "Like List", "ItemFavoriteList"])
                        if likes and len(likes) > 0:
                            results['ultimo_like'] = extract_field(likes[0], link_fields)

                    # Primer favorito
                    if options['first_fav']:
                        favs = safe_get(data, ["Your Activity", "Favorite Videos", "FavoriteVideoList"])
                        if favs and len(favs) > 0:
                            results['primer_favvideo'] = extract_field(favs[-1], link_fields)

                    # Último favorito
                    if options['last_fav']:
                        favs = safe_get(data, ["Your Activity", "Favorite Videos", "FavoriteVideoList"])
                        if favs and len(favs) > 0:
                            results['ultimo_favvideo'] = extract_field(favs[0], link_fields)

                    # Video aleatorio de likes
                    if options['random_like']:
                        likes = safe_get(data, ["Your Activity", "Like List", "ItemFavoriteList"])
                        if likes and len(likes) > 0:
                            results['random_like'] = extract_field(random.choice(likes), link_fields)

                    # Canción aleatoria
                    if options['random_song']:
                        sounds = safe_get(data, ["Your Activity", "Favorite Sounds", "FavoriteSoundList"])
                        if sounds and len(sounds) > 0:
                            results['random_song'] = extract_field(random.choice(sounds), link_fields)

                    if not results:
                        error = "❌ No se pudo leer el archivo. La estructura del JSON no es compatible. Asegúrate de descargar tus datos de TikTok en formato JSON."
                    
                    # Limpiar archivo temporal
                    os.remove(file_path)
                    
                except json.JSONDecodeError:
                    error = "❌ Error: El archivo no es un JSON válido"
                except Exception as e:
                    error = f"❌ Error al procesar el archivo: {str(e)}"

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)