import os
import re
import multiprocessing
from os.path import exists
from typing import Tuple, Any, Final

import shutil
from typing import Tuple, Any
from PIL import Image

from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.crop import crop
import random
import time
import config

def prepare_background(reddit_id, length, W, H):
    my_config = config.load_config()

    # Configurar el video de fondo y ajustar su duración y resolución
    video = VideoFileClip(my_config['Background']['path']).without_audio()
    vide_duration = video.duration

    # Seleccionar un inicio aleatorio en el video para el fondo
    random_start = random.randint(0, int(vide_duration))
    vid = video.subclip(random_start, random_start+length)
    video.close()

    # Redimensionar el video y preparar la sección del fondo
    vid_resized = resize(vid, height=H)
    clip = vid_resized

    # Calcular el centro del clip de fondo
    c = clip.w // 2

    # Calcular las coordenadas para el recorte
    half_w = W // 2
    x1 = c - half_w
    x2 = c + half_w

    return crop(clip, x1=x1, y1=0, x2=x2, y2=H)

def make_final_video(
    title_audio_path,
    comments_audio_path,
    title_image_path,
    comments_image_path,
    length: int,
    reddit_id,
):
    # Valores de configuración
    W = 1080
    H = 1920
    opacity = 0.95

    print("Creando el video final 🎥")
    background_clip = prepare_background(reddit_id, length, W, H)

    # Reunir todos los clips de audio
    audio_clips = [
        AudioFileClip(i)
        for i in comments_audio_path
    ]

    # Insertar el audio del título
    audio_clips.insert(0, AudioFileClip(title_audio_path))
    audio_concat = concatenate_audioclips(audio_clips)

    # Crear el audio compuesto
    audio_composite = CompositeAudioClip([audio_concat])

    print(f"El video tendrá una duración de: {length} segundos")

    # Agregar el título al video
    image_clips = []
    # Reunir todas las imágenes

    new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)

    screenshot_width = int((W * 90) // 100)

    title = ImageClip(title_image_path).set_duration(audio_clips[0].duration).set_opacity(new_opacity).set_position("center")
    resized_title = resize(title, width=screenshot_width)
    image_clips.insert(0, resized_title)

    for idx, i in enumerate(comments_image_path):
        comment = ImageClip(i).set_duration(audio_clips[idx + 1].duration).set_opacity(new_opacity).set_position("center")
        resized_comment = resize(comment, width=screenshot_width)
        image_clips.append(resized_comment)

    image_concat = concatenate_videoclips(image_clips)  # kwarg transition para retraso en imgs
    image_concat.audio = audio_composite
    audio_composite.close()
    final = CompositeVideoClip([background_clip, image_concat.set_position("center")])
    image_concat.close()

    subreddit = reddit_id

    # Exportar el video final
    final.write_videofile(
        f"./Results/{subreddit}.mp4",
        fps=int(24),
        audio_codec="aac",
        audio_bitrate="192k",
        threads=multiprocessing.cpu_count(),
        #preset="ultrafast", # para pruebas
    )
    final.close()

    print("El resultado está en la carpeta de resultados.")
