from bs4 import BeautifulSoup
from markdown import markdown
import re

def markdown_to_text(markdown_string):
    """ Convierte una cadena de texto en formato markdown a texto plano """

    # Convertir markdown a HTML y luego a texto, ya que BeautifulSoup puede extraer texto de manera limpia
    html = markdown(markdown_string)

    # Eliminar fragmentos de código
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code>', ' ', html)

    # Extraer texto
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))
    return text
