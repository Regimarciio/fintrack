from flask import Flask, request, jsonify, render_template
import os
from ocr import extrair_texto_arquivo as extract_text
from parser import parse_data
from ai_parser import parse_with_ai
from database import save_to_db

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    text = extract_text(path)

    data = parse_data(text, path)
    ai_data = parse_with_ai(text)

    if ai_data:
        if ai_data.get("valor_total"):
            data["valor_total"] = ai_data["valor_total"]

        if ai_data.get("estabelecimento"):
            data["estabelecimento"] = ai_data["estabelecimento"]

        if ai_data.get("itens"):
            data["itens"] = ai_data["itens"]

    save_to_db(data)

    return jsonify(data)

app.run(host='0.0.0.0', debug=True, port=5010)
