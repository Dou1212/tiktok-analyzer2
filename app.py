from flask import Flask, render_template, request
import json
from scripts.read_tiktok import analizar_tiktok

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and file.filename.endswith('.json'):
        try:
            # ✅ Leemos el JSON directamente del archivo subido
            data = json.load(file)
            result = analizar_tiktok(data)
            return render_template('index.html', result=result)
        except Exception as e:
            return f"Error al procesar el archivo: {e}", 400
    else:
        return "Archivo inválido. Sube un JSON válido.", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
