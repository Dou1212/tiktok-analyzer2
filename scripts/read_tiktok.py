def analizar_tiktok(data):
    try:
        # CANCIONES FAVORITAS
        primera_song = data['Activity']['Favorite Sounds']['FavoriteSoundList'][-1]['Link']
        ultima_song = data['Activity']['Favorite Sounds']['FavoriteSoundList'][0]['Link']

        # SEGUIDORES
        primer_seguidor = data["Activity"]["Follower List"]["FansList"][-1]["UserName"]
        ultimo_seguidor = data["Activity"]["Follower List"]["FansList"][0]["UserName"]

        # LIKES
        primer_like = data["Activity"]["Like List"]["ItemFavoriteList"][-1]["Link"]
        ultimo_like = data["Activity"]["Like List"]["ItemFavoriteList"][0]["Link"]

        # VIDEOS FAVORITOS
        primer_favvideo = data["Activity"]["Favorite Videos"]["FavoriteVideoList"][-1]["Link"]
        ultimo_favvideo = data["Activity"]["Favorite Videos"]["FavoriteVideoList"][0]["Link"]

        resultado = (
            f"🎵 Primera y última canción favorita:\n{primera_song} - {ultima_song}\n\n"
            f"👤 Primer y último seguidor:\n{primer_seguidor} - {ultimo_seguidor}\n\n"
            f"❤️ Primer y último like:\n{primer_like} - {ultimo_like}\n\n"
            f"📹 Primer y último video favorito:\n{primer_favvideo} - {ultimo_favvideo}"
        )
        return resultado

    except Exception as e:
        return f"⚠️ Error procesando el archivo: {e}"
