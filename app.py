from flask import Flask, request, render_template
import json
import uuid
import os
import random
from google.cloud import storage
from datetime import datetime
import traceback

app = Flask(__name__)

# Configuración del bucket
BUCKET_NAME = "tiktok_guarda_jsonn"

def upload_to_gcs(file_path, destination_blob_name):
    """Sube un archivo a Google Cloud Storage"""
    try:
        print(f"🔄 Intentando subir archivo a GCS...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        
        blob.upload_from_filename(file_path)
        print(f"✅ Archivo subido exitosamente a gs://{BUCKET_NAME}/{destination_blob_name}")
        return True
    except Exception as e:
        print(f"❌ Error al subir a GCS: {e}")
        print(f"📋 Traceback completo: {traceback.format_exc()}")
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None

    if request.method == "POST":
        print("=" * 50)
        print("📥 Nueva petición POST recibida")
        
        if "file" not in request.files:
            error = "❌ No se subió ningún archivo"
            print(f"⚠️ {error}")
        else:
            file = request.files["file"]
            print(f"📁 Archivo recibido: {file.filename}")
            
            if file.filename == "" or not file.filename.endswith(".json"):
                error = "❌ Archivo inválido. Debe ser un archivo JSON"
                print(f"⚠️ {error}")
            else:
                # Guardar temporalmente
                tmp_folder = "/tmp"
                filename = f"{uuid.uuid4()}.json"
                file_path = os.path.join(tmp_folder, filename)
                print(f"💾 Guardando temporalmente en: {file_path}")
                file.save(file_path)

                # Leer JSON
                try:
                    print(f"📖 Leyendo archivo JSON...")
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    print(f"✅ JSON leído correctamente")
                    print(f"🔑 Claves principales del JSON: {list(data.keys())}")

                    # Verificar estructura
                    if 'Activity' in data:
                        print(f"✅ Clave 'Activity' encontrada")
                        print(f"🔑 Subclaves de Activity: {list(data['Activity'].keys())}")
                    else:
                        print(f"⚠️ ADVERTENCIA: No se encontró la clave 'Activity'")

                    # Subir a Google Cloud Storage
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    gcs_filename = f"uploads/{timestamp}_{filename}"
                    print(f"☁️ Subiendo a GCS como: {gcs_filename}")
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
                    print(f"⚙️ Opciones seleccionadas: {options}")

                    # Analizar datos según opciones
                    results = {}

                    # Primera canción
                    if options['first_song']:
                        try:
                            print(f"🎵 Buscando primera canción...")
                            results['primera_song'] = data['Activity']['Favorite Sounds']['FavoriteSoundList'][-1]['Link']
                            print(f"✅ Primera canción encontrada")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener primera canción: {e}")

                    # Última canción
                    if options['last_song']:
                        try:
                            print(f"🎶 Buscando última canción...")
                            results['ultima_song'] = data['Activity']['Favorite Sounds']['FavoriteSoundList'][0]['Link']
                            print(f"✅ Última canción encontrada")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener última canción: {e}")

                    # Primer seguidor
                    if options['first_follower']:
                        try:
                            print(f"👤 Buscando primer seguidor...")
                            results['primer_seguidor'] = data["Activity"]["Follower List"]["FansList"][-1]["UserName"]
                            print(f"✅ Primer seguidor encontrado")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener primer seguidor: {e}")

                    # Último seguidor
                    if options['last_follower']:
                        try:
                            print(f"👥 Buscando último seguidor...")
                            results['ultimo_seguidor'] = data["Activity"]["Follower List"]["FansList"][0]["UserName"]
                            print(f"✅ Último seguidor encontrado")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener último seguidor: {e}")

                    # Primer like
                    if options['first_like']:
                        try:
                            print(f"❤️ Buscando primer like...")
                            results['primer_like'] = data["Activity"]["Like List"]["ItemFavoriteList"][-1]["Link"]
                            print(f"✅ Primer like encontrado")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener primer like: {e}")

                    # Último like
                    if options['last_like']:
                        try:
                            print(f"💖 Buscando último like...")
                            results['ultimo_like'] = data["Activity"]["Like List"]["ItemFavoriteList"][0]["Link"]
                            print(f"✅ Último like encontrado")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener último like: {e}")

                    # Primer favorito
                    if options['first_fav']:
                        try:
                            print(f"⭐ Buscando primer favorito...")
                            results['primer_favvideo'] = data["Activity"]["Favorite Videos"]["FavoriteVideoList"][-1]["Link"]
                            print(f"✅ Primer favorito encontrado")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener primer favorito: {e}")

                    # Último favorito
                    if options['last_fav']:
                        try:
                            print(f"🌟 Buscando último favorito...")
                            results['ultimo_favvideo'] = data["Activity"]["Favorite Videos"]["FavoriteVideoList"][0]["Link"]
                            print(f"✅ Último favorito encontrado")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener último favorito: {e}")

                    # Video aleatorio de likes
                    if options['random_like']:
                        try:
                            print(f"🎲 Buscando video aleatorio de likes...")
                            like_list = data["Activity"]["Like List"]["ItemFavoriteList"]
                            if like_list:
                                results['random_like'] = random.choice(like_list)["Link"]
                                print(f"✅ Video aleatorio encontrado")
                            else:
                                print(f"⚠️ Lista de likes vacía")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener video aleatorio: {e}")

                    # Canción aleatoria
                    if options['random_song']:
                        try:
                            print(f"🎧 Buscando canción aleatoria...")
                            song_list = data['Activity']['Favorite Sounds']['FavoriteSoundList']
                            if song_list:
                                results['random_song'] = random.choice(song_list)["Link"]
                                print(f"✅ Canción aleatoria encontrada")
                            else:
                                print(f"⚠️ Lista de canciones vacía")
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ No se pudo obtener canción aleatoria: {e}")

                    # Agregar ruta de GCS
                    results['gcs_path'] = gcs_filename
                    
                    print(f"🎉 Análisis completado. Resultados encontrados: {len(results)}")
                    
                    # Limpiar archivo temporal
                    os.remove(file_path)
                    print(f"🗑️ Archivo temporal eliminado")
                    
                except json.JSONDecodeError as e:
                    error = "❌ Error: El archivo no es un JSON válido"
                    print(f"❌ JSONDecodeError: {e}")
                    print(f"📋 Traceback: {traceback.format_exc()}")
                except Exception as e:
                    error = f"❌ Error al procesar el archivo: {str(e)}"
                    print(f"❌ Exception: {e}")
                    print(f"📋 Traceback completo: {traceback.format_exc()}")
        
        print("=" * 50)

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Iniciando servidor en puerto {port}")
    app.run(host="0.0.0.0", port=port)