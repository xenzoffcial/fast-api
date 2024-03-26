import os
try:import Flask
except:os.system("python3 -m pip install flask")
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
import threading
import queue
import logging
import subprocess
import uuid
from PIL import Image
import re

app = Flask(__name__)

my_queue = queue.Queue()
status_err = False
logging.basicConfig(filename='app.log', level=logging.INFO)


def clear_file(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            pass


def keep_file(folder_path):
    _ = []
    for filename in os.listdir(folder_path):
        _.append(os.path.join(folder_path, filename))
    return _


def remove_file(list_filename: list):
    for i in list_filename:
        os.remove(i)


@app.route('/')
def read_root():
    client_host = request.remote_addr
    return jsonify({"client_host": client_host})


# Di Flask, kita akan menerima data JSON secara manual
@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')
    # Sisanya mirip dengan apa yang dilakukan di FastAPI
    if my_queue.qsize() < 1 and prompt:
        # Penerapan BackgroundTasks di Flask memerlukan adaptasi
        # Contoh ini tidak mengimplementasikannya secara langsung
        logging.info(f"{request.remote_addr} ---- {prompt}")
        return jsonify({"message": "Accepted"})
    else:
        return jsonify({"message": "has queue processing"})


@app.route('/image', methods=['GET'])
def list_images():
    # Contoh ini mengasumsikan bahwa output dan thumbnail sudah dihasilkan
    # dan tersimpan dalam direktori yang sesuai.
    if my_queue.qsize() < 1:
        image_files = [f"output/{filename}" for filename in os.listdir("output")]
        image_thumbnail = [f"thumbnail/{filename}" for filename in os.listdir("thumbnail")]
        # Mengembalikan file JSON promp.json
        with open("promp.json", "r") as infile:
            data = json.load(infile)
        return jsonify({
            "status_gen": True,
            "images": image_files,
            "thumbnail": image_thumbnail,
            "prompt_text": data["text"],
            "status_error": status_err
        })
    else:
        return jsonify({"status_gen": False, "images": None, "prompt_text": ""})


@app.route('/image/<filename>', methods=['GET'])
def get_image(filename):
    filepath = f"output/{secure_filename(filename)}"
    return send_file(filepath)


@app.route('/thumbnail/<filename>', methods=['GET'])
def get_thumbnail(filename):
    filepath = f"thumbnail/{secure_filename(filename)}"
    return send_file(filepath)


@app.route('/status-error', methods=['POST'])
def status_error():
    global status_err
    status_err = False
    return "Change status_err to false finish"


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
