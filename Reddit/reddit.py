# Importar dependencias de Reddit
import praw
from praw.reddit import Reddit
from praw.models import MoreComments
# Gestionar la base de datos
from tinydb import Query

import time
import config
import database

submission = Query()

def login():
    try:
        # Cargar configuración desde config.toml y autenticar en Reddit
        my_config = config.load_config()
        reddit = praw.Reddit(client_id=my_config['RedditCredential']['client_id'],
                             client_secret=my_config['RedditCredential']['client_secret'],
                             user_agent=my_config['RedditCredential']['user_agent'])

        print("¡Inicio de sesión en Reddit exitoso!")
        return reddit
    except Exception as e:
        print(f"Error al iniciar sesión en Reddit: {e}")
        return None

def get_thread(reddit: Reddit, subreddit: str):
    print("Accediendo al subreddit:", subreddit)
    subreddit_ = reddit.subreddit(subreddit)

    # Obtener los hilos más populares de la semana
    threads = subreddit_.top('week')

    # Ordenar los hilos en función del número de votos positivos
    sorted_threads = sorted(threads, key=lambda x: int(x.score), reverse=True)

    chosen_thread = None

    # Obtener el hilo más votado que no esté en la base de datos
    db = database.load_databse()
    for thread in sorted_threads:
        if not db.search(submission.id == str(thread.id)):
            db.insert({'id': thread.id, 'time': time.time()})
            db.close()
            print(f"Hilo elegido: {thread.title} -- Puntuación: {thread.score}")
            chosen_thread = thread
            db.close()
            break
    db.close()
    return chosen_thread

def get_comments(thread):
    # Cargar la configuración para el número máximo de comentarios a extraer
    my_config = config.load_config()
    topn = my_config['Reddit']['topn_comments']
    chosen_comments = None
    comments = []
    for top_level_comment in thread.comments:
        if len(comments) == topn:
            break
        if isinstance(top_level_comment, MoreComments):
            continue
        comments.append(top_level_comment)

    chosen_comments = comments
    print(f"{len(chosen_comments)} comentarios seleccionados")
    return chosen_comments

# Probar las funciones
if __name__ == "__main__":
    reddit_client = login()
    if reddit_client:
        thread = get_thread(reddit_client, "popular")  # Asegúrate de especificar el subreddit adecuado
        if thread:
            comments = get_comments(thread)
            for comment in comments:
                print(comment.body)  # Imprime el cuerpo de cada comentario seleccionado
