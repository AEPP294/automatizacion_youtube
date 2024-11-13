#!/usr/bin/python

import httplib2
import os
import random
import sys
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import config

my_config = config.load_config()

httplib2.RETRIES = 1

# Número máximo de intentos antes de detener el proceso
MAX_RETRIES = 10

# Siempre reintentar cuando ocurran estas excepciones
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = f"{my_config['Directory']['path']}/client_secrets.json"

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
ADVERTENCIA: Configure OAuth 2.0

Para ejecutar este ejemplo, debe configurar el archivo client_secrets.json
ubicado en:

   %s

con la información de la API Console
https://console.cloud.google.com/

Para más información sobre el formato de client_secrets.json, visite:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,  # Usar la ruta del archivo
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Llamar al método videos.insert de la API para crear y subir el video
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

# Este método implementa una estrategia de retroceso exponencial para reanudar
# una subida fallida
def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Subiendo archivo...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("El video con ID '%s' fue subido exitosamente." % response['id'])
                else:
                    exit("La subida falló con una respuesta inesperada: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "Un error HTTP recuperable %d ocurrió:\n%s" % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "Ocurrió un error recuperable: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No se intentará reintentar nuevamente.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Esperando %f segundos y reintentando..." % sleep_seconds)
            time.sleep(sleep_seconds)

if __name__ == '__main__':
    argparser.add_argument("--file", required=True, help="Archivo de video a subir")
    argparser.add_argument("--title", help="Título del video", default="Título de Prueba")
    argparser.add_argument("--description", help="Descripción del video", default="Descripción de Prueba")
    argparser.add_argument("--category", default="22", help="Categoría numérica del video. "
                                                           "Ver https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Palabras clave del video, separadas por comas", default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
                           default=VALID_PRIVACY_STATUSES[0], help="Estado de privacidad del video.")
    args = argparser.parse_args()

    if not os.path.exists(args.file):
        exit("Por favor, especifique un archivo válido usando el parámetro --file.")

    youtube = get_authenticated_service(args)
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        print("Un error HTTP %d ocurrió:\n%s" % (e.resp.status, e.content))
