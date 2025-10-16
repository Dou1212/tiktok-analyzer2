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

def get_nested_value(data, *keys):
    """Obtiene un valor anidado del JSON de forma segura"""
    try:
        value = data
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError, IndexError):
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

                    # Detectar estructura del JSON
                    # NUEVA ESTRUCTURA (2024-2025)
                    if 'Ads and data' in data:
                        # Primera canción (Favorite Sounds)
                        if options['first_song']:
                            sounds = get_nested_value(data, 'Activity', 'Favorite Sounds', 'FavoriteSoundList')
                            if sounds and len(sounds) > 0:
                                results['primera_song'] = sounds[-1].get('Link', '')

                        # Última canción
                        if options['last_song']:
                            sounds = get_nested_value(data, 'Activity', 'Favorite Sounds', 'FavoriteSoundList')
                            if sounds and len(sounds) > 0:
                                results['ultima_song'] = sounds[0].get('Link', '')

                        # Primer seguidor
                        if options['first_follower']:
                            fans = get_nested_value(data, 'Activity', 'Follower List', 'FansList')
                            if fans and len(fans) > 0:
                                results['primer_seguidor'] = fans[-1].get('UserName', '')

                        # Último seguidor
                        if options['last_follower']:
                            fans = get_nested_value(data, 'Activity', 'Follower List', 'FansList')
                            if fans and len(fans) > 0:
                                results['ultimo_seguidor'] = fans[0].get('UserName', '')

                        # Primer like
                        if options['first_like']:
                            likes = get_nested_value(data, 'Activity', 'Like List', 'ItemFavoriteList')
                            if likes and len(likes) > 0:
                                results['primer_like'] = likes[-1].get('Link', '')

                        # Último like
                        if options['last_like']:
                            likes = get_nested_value(data, 'Activity', 'Like List', 'ItemFavoriteList')
                            if likes and len(likes) > 0:
                                results['ultimo_like'] = likes[0].get('Link', '')

                        # Primer favorito
                        if options['first_fav']:
                            favs = get_nested_value(data, 'Activity', 'Favorite Videos', 'FavoriteVideoList')
                            if favs and len(favs) > 0:
                                results['primer_favvideo'] = favs[-1].get('Link', '')

                        # Último favorito
                        if options['last_fav']:
                            favs = get_nested_value(data, 'Activity', 'Favorite Videos', 'FavoriteVideoList')
                            if favs and len(favs) > 0:
                                results['ultimo_favvideo'] = favs[0].get('Link', '')

                        # Video aleatorio de likes
                        if options['random_like']:
                            likes = get_nested_value(data, 'Activity', 'Like List', 'ItemFavoriteList')
                            if likes and len(likes) > 0:
                                results['random_like'] = random.choice(likes).get('Link', '')

                        # Canción aleatoria
                        if options['random_song']:
                            sounds = get_nested_value(data, 'Activity', 'Favorite Sounds', 'FavoriteSoundList')
                            if sounds and len(sounds) > 0:
                                results['random_song'] = random.choice(sounds).get('Link', '')

                    # ESTRUCTURA ALTERNATIVA (más reciente según GitHub)
                    elif 'Video' in data or ('Activity' in data and 'Video' in data['Activity']):
                        # Intentar con Activity > Video > Videos > VideoList
                        video_list = get_nested_value(data, 'Activity', 'Video', 'Videos', 'VideoList')
                        if not video_list:
                            video_list = get_nested_value(data, 'Video', 'Videos', 'VideoList')
                        
                        if video_list and len(video_list) > 0:
                            # Primer video
                            if options['first_like']:
                                results['primer_like'] = video_list[-1].get('Link', '')
                            
                            # Último video
                            if options['last_like']:
                                results['ultimo_like'] = video_list[0].get('Link', '')
                            
                            # Video aleatorio
                            if options['random_like']:
                                results['random_like'] = random.choice(video_list).get('Link', '')

                    # Si no se encontró ninguna estructura conocida
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