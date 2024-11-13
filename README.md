# Automatización de YouTube 📺

Con este proyecto, los videos generados a partir de publicaciones populares de Reddit se subirán automáticamente a tu canal de YouTube.

## Video de Ejemplo
[![Video de Ejemplo](video-reddit.mp4)](video-reddit.mp4)

## Construido con
* [![AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)][AWS-url]
* [![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)][Python-url]
* [![Reddit](https://img.shields.io/badge/Reddit-FF4500?style=for-the-badge&logo=reddit&logoColor=white)][Reddit-url]
* [![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)][Youtube-url]
* [![Json](https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white)][Json-url]

[AWS-url]: https://aws.amazon.com/
[Python-url]: https://www.python.org/
[Youtube-url]: https://www.youtube.com/
[Reddit-url]: https://www.reddit.com/
[Json-url]: https://www.json.org/json-en.html

## Instalación 💻

1. Clona este repositorio y crea un entorno virtual.

   ```bash
   git clone https://github.com/davidcanoteayuda/automatizacion_youtube.git

   cd automatizacion_youtube

   python3 -m venv venv

   source venv/bin/activate

2. Instala las dependencias del proyecto:

   ```bash
   pip install -r requirements.txt
   
3. Configura Playwright: (es posible que esto NO sea necesario en tu caso!)

   ```bash
   python -m playwright install
   python -m playwright install-deps

4. Regístrate en AWS Free Tier para obtener credenciales:

   Inicia sesión en AWS y navega a Credenciales de seguridad.
   
   Crea una clave de acceso para el servicio Amazon Polly.
   
   Guarda tu Access Key ID y Secret Access Key. Luego, abre el archivo config.toml en tu proyecto y actualiza los siguientes parámetros:

   ```toml
   [AmazonAWSCredential]
   aws_access_key_id = 'TU_ACCESS_KEY_ID_DE_AWS'
   aws_secret_access_key = 'TU_SECRET_ACCESS_KEY_DE_AWS'

5. Configura una aplicación en Reddit:

   Dirígete a Preferencias de Aplicación en Reddit y crea una nueva aplicación.
   
   Asegúrate de seleccionar el tipo script y guarda los valores de personal use script y secret token.
   
   Actualiza el archivo config.toml con tus credenciales de Reddit:

   ```toml
   [RedditCredential]
   client_id='TU_PERSONAL_USE_SCRIPT'
   client_secret='TU_SECRET_TOKEN'
   user_agent='{Nombre del Proyecto} v1.0 por /u/{Tu Nombre de Usuario en Reddit}'
   username='Tu Nombre de Usuario en Reddit'
   passkey='Tu Contraseña de Reddit'

6. Configura el directorio y el video de fondo en config.toml:

   ```toml
   [Directory]
   path='/ruta/completa/del/proyecto'
   
   [Background]
   path='/ruta/completa/del/video_fondo.mp4'

7. Para subir automáticamente el video generado a YouTube, establece upload_to_youtube = true y configura la frecuencia de subida en segundos (ejemplo: cada 6 horas):

   ```toml
   [App]
   upload_to_youtube=true
   run_every=21600  # 6 horas en segundos

8. Habilita la API de YouTube:

   Sigue este tutorial hasta el minuto 10:58 para habilitar la API de YouTube y obtener un client_id y un client_secret.

   Descarga el archivo client_secrets.json generado y guárdalo en la carpeta principal de este proyecto. Este archivo es necesario para la autenticación en YouTube.

   Además, actualiza el archivo config.toml con las credenciales obtenidas para que el programa pueda acceder a la API de YouTube:

   ```toml
   [YoutubeCredential]
   client_id='TU_CLIENT_ID'
   client_secret='TU_CLIENT_SECRET'

## Ejecución del Programa 🚀

Después de configurar todos los parámetros, ejecuta el siguiente comando para comenzar a generar y subir videos automáticamente:

   ```bash
   python main.py
