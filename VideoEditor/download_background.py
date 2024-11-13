# importación de módulos
from pytube import YouTube
import os.path
from os import path

# ruta de guardado
SAVE_PATH = "../Assets/background/"

def background_exists():
    return path.exists(SAVE_PATH + 'Nature.mp4')

def download(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(22)
        print(f"Descargando {yt.title}...")
        stream.download(output_path=SAVE_PATH, filename="Nature.mp4")

    except Exception as e:
        print(e)
        return None
