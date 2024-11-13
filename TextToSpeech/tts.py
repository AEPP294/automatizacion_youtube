from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import sys
from mutagen.mp3 import MP3
import config
import random

def creat_session():
    # Cargar configuración desde config.toml y crear una sesión de AWS
    my_config = config.load_config()
    session = Session(aws_access_key_id=my_config['AmazonAWSCredential']['aws_access_key_id'],
                      aws_secret_access_key=my_config['AmazonAWSCredential']['aws_secret_access_key'],
                      region_name=my_config['AmazonAWSCredential']['region_name']
                      )
    return session

def create_tts(text, path):
    # Cargar configuración y crear una instancia de servicio de AWS Polly
    my_config = config.load_config()
    session = creat_session()
    polly = session.client("polly")

    try:
        # Seleccionar la voz para la conversión de texto a voz
        voice_id = my_config['TextToSpeechSetup']['voice_id']
        if my_config['TextToSpeechSetup']['multiple_voices']:
            voices = ["Joanna", "Justin", "Kendra", "Matthew"]
            voice_id = random.choice(voices)

        # Generar la síntesis de voz en formato MP3
        response = polly.synthesize_speech(Text=text,
                                           OutputFormat="mp3",
                                           VoiceId=voice_id)
    except (BotoCoreError, ClientError) as error:
        print(error)
        sys.exit(-1)

    # Acceder al flujo de audio desde la respuesta
    if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
               output = path
               try:
                    # Abrir un archivo para escribir el audio como un flujo binario
                    with open(output, "wb") as file:
                       file.write(stream.read())

               except IOError as error:
                  # No se pudo escribir en el archivo, salir de forma controlada
                  print(error)
                  sys.exit(-1)

    else:
        # La respuesta no contenía datos de audio, salir de forma controlada
        print("No se pudo transmitir el audio")
        sys.exit(-1)

def get_length(path):
    # Obtener la duración del archivo de audio
    try:
        audio = MP3(path)
        length = audio.info.length
        return length
    except:
        return None
