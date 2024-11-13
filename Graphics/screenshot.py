import json
import re
import config
import time
from pathlib import Path
from typing import Dict, Final

from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright


# from utils.imagenarator import imagemaker

def get_screenshots_of_reddit_posts(reddit_thread, reddit_comments, screenshot_num: int, theme="dark"):

    # Configuración de valores
    W = 1080
    H = 1920

    reddit_id = re.sub(r"[^\w\s-]", "", reddit_thread.id)
    # ! Asegúrate de que la carpeta de capturas de pantalla de Reddit exista
    Path(f"./Assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

    screenshot_num: int
    with sync_playwright() as p:
        print("Iniciando navegador en modo headless...")

        browser = p.chromium.launch(headless=False)  # headless=False para verificar visualmente en el navegador
        context = browser.new_context()
        my_config = config.load_config()
        # El factor de escala del dispositivo (dsf) permite aumentar la resolución de las capturas de pantalla
        # Cuando dsf es 1, el ancho de la captura es de 600 píxeles
        # Por lo tanto, necesitamos un dsf tal que el ancho de la captura sea mayor que la resolución final del video
        dsf = (W // 600) + 1

        context = browser.new_context(
            locale="en-us",
            color_scheme="dark",
            viewport=ViewportSize(width=W, height=H),
            device_scale_factor=dsf,
        )
        # Establece el tema y deshabilita cookies no esenciales
        if theme == "dark":
            cookie_file = open(
                "./Graphics/data/cookie-dark-mode.json", encoding="utf-8"
            )
            bgcolor = (33, 33, 36, 255)
            txtcolor = (240, 240, 240)

        cookies = json.load(cookie_file)
        cookie_file.close()

        context.add_cookies(cookies)  # Cargar cookies de preferencia

        # Obtener la captura de pantalla de la publicación principal
        page = context.new_page()
        # Ir a la página de inicio de sesión de Reddit
        page.goto("https://www.reddit.com/login/?experiment_d2x_2020ify_buttons=enabled&use_accountmanager=true&experiment_d2x_google_sso_gis_parity=enabled&experiment_d2x_onboarding=enabled&experiment_d2x_am_modal_design_update=enabled")
        # Rellenar la información de usuario
        page.locator("id=loginUsername").fill(my_config["RedditCredential"]["username"])
        page.locator("id=loginPassword").fill(my_config["RedditCredential"]["passkey"])
        page.get_by_role("button", name="Log In").click()
        time.sleep(10)
        # Ir a la publicación
        page.goto("https://www.reddit.com" + reddit_thread.permalink, timeout=0)
        time.sleep(10)
        page.keyboard.press("Escape")
        
        page.goto("https://www.reddit.com" + reddit_thread.permalink, timeout=0)
        page.set_viewport_size(ViewportSize(width=W, height=H))

        postcontentpath = f"./Assets/temp/{reddit_id}/png/title.png"
        page.locator(f'[data-test-id="post-rtjson-content"]').screenshot(path=postcontentpath)
        print("Captura de pantalla de la publicación principal completada")

        for idx, comment in enumerate(reddit_comments):

            if page.locator('[data-testid="content-gate"]').is_visible():
                page.locator('[data-testid="content-gate"] button').click()

            page.goto(f'https://reddit.com{comment.permalink}', timeout=0)

            try:
                page.locator(f"#t1_{comment.id}").screenshot(
                    path=f"./Assets/temp/{reddit_id}/png/{idx}.png"
                )
                print(f"Captura de pantalla de {idx + 1} comentario de un total de {len(reddit_comments)}")
            except TimeoutError:
                print("TimeoutError: Omitiendo captura de pantalla...")
                continue

        # Cerrar la instancia del navegador cuando terminamos de usarla
        browser.close()

    print("Capturas de pantalla descargadas exitosamente.")
