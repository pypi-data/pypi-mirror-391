import os
import re
import io
import json
import http.cookies
import random
import string
import pymysql
import urllib.parse
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from wsgiref.simple_server import make_server
import shutil


BASE_DIR = os.getcwd()
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
HTML_DIR = os.path.join(PUBLIC_DIR, "html")

MIME_TYPES = {
    'css': 'text/css',
    'js': 'application/javascript',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'ico': 'image/x-icon',
}

DIRECTORIES = {
    'css': os.path.join(PUBLIC_DIR, 'css'),
    'js': os.path.join(PUBLIC_DIR, 'js'),
    'png': os.path.join(PUBLIC_DIR, 'images'),
    'jpg': os.path.join(PUBLIC_DIR, 'images'),
    'jpeg': os.path.join(PUBLIC_DIR, 'images'),
    'gif': os.path.join(PUBLIC_DIR, 'images'),
    'ico': os.path.join(PUBLIC_DIR, 'images'),
}

ERROR_PAGE = os.path.join(HTML_DIR, 'error.html')
SESSION_FILE = os.path.join(BASE_DIR, 'sessions.json')

TEMPLATE_ENV = Environment(loader=FileSystemLoader(HTML_DIR))


def jugoConsColor():
    return {
        'HEADER': '\033[95m',
        'BLUE': '\033[94m',
        'GREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
    }


def jugoPrint(message, level="INFO"):
    colors = jugoConsColor()
    levelColors = {
        'INFO': colors['BLUE'],
        'SUCCESS': colors['GREEN'],
        'WARNING': colors['WARNING'],
        'ERROR': colors['FAIL'],
        'HEADER': colors['HEADER']
    }
    color = levelColors.get(level, colors['ENDC'])
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {level}: {message}{colors['ENDC']}")


def jugoServeError(status, content, startResponse):
    startResponse(status, [('Content-Type', 'text/html')])
    try:
        with open(ERROR_PAGE, 'rb') as f:
            html = f.read()
        html = html.replace(b'{{error}}', str(content).encode('utf-8'))
        return [html]
    except Exception:
        return [f"<h1>{status}</h1><p>{content}</p>".encode('utf-8')]


ROUTES = {}

def jugoRoute(path):
    def decorator(func):
        ROUTES[path] = func
        return func
    return decorator

def jugoDispatch(environ, startResponse):
    path = environ.get('PATH_INFO', '/')
    handler = ROUTES.get(path)
    if handler:
        return handler(environ, startResponse)
    return jugoServeError('404 Not Found', f"La route {path} est introuvable.", startResponse)


def jugoLoadStatic(fileName, startResponse):
    _, ext = os.path.splitext(fileName)
    ext = ext.lstrip('.')
    mimeType = MIME_TYPES.get(ext)
    folder = DIRECTORIES.get(ext)
    if not mimeType or not folder:
        return jugoServeError('404 Not Found', f"Extension '.{ext}' non supportée.", startResponse)
    path = os.path.join(folder, fileName)
    if not os.path.exists(path):
        return jugoServeError('404 Not Found', f"Le fichier {fileName} est introuvable.", startResponse)
    with open(path, 'rb') as f:
        content = f.read()
    startResponse('200 OK', [('Content-Type', mimeType)])
    return [content]


def jugoRender(templateName, context=None, startResponse=None):
    context = context or {}
    try:
        template = TEMPLATE_ENV.get_template(templateName)
        html = template.render(**context)
        startResponse('200 OK', [('Content-Type', 'text/html')])
        return [html.encode('utf-8')]
    except Exception as e:
        return jugoServeError('500 Internal Server Error', f"Erreur de rendu : {e}", startResponse)


def jugoParsePost(environ):
    content_type = environ.get("CONTENT_TYPE", "").lower()
    content_length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(content_length)

    if content_type.startswith("application/x-www-form-urlencoded"):
        data = urllib.parse.parse_qs(body.decode("utf-8"))
        return {k: v[0] for k, v in data.items()}

    elif content_type.startswith("multipart/form-data"):
        boundary = content_type.split("boundary=")[-1].strip()
        if not boundary:
            return {}
        data = {}
        parts = body.split(f"--{boundary}".encode())
        for part in parts:
            if b"Content-Disposition" in part:
                try:
                    header, content = part.split(b"\r\n\r\n", 1)
                    content = content.strip(b"\r\n--")
                    name_match = re.search(rb'name="([^"]+)"', header)
                    if name_match:
                        name = name_match.group(1).decode("utf-8")
                        data[name] = content.decode("utf-8", errors="ignore")
                except Exception:
                    continue
        return data

    return {}


def jugoSetCookie(environ, name, content):
    cookies = http.cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
    val = json.dumps(content) if isinstance(content, (dict, list)) else str(content)
    cookies[name] = val
    environ['HTTP_COOKIE'] = '; '.join(f"{k}={v.value}" for k, v in cookies.items())
    return environ

def jugoGetCookie(environ, name):
    cookies = http.cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
    if name in cookies:
        val = cookies[name].value
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return val
    return None


def jugoGetSession(sessionId):
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, 'r') as f:
        sessions = json.load(f)
    return sessions.get(sessionId, {})

def jugoSaveSession(sessionId, data):
    sessions = {}
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            sessions = json.load(f)
    sessions[sessionId] = data
    with open(SESSION_FILE, 'w') as f:
        json.dump(sessions, f)


def jugoCrypt(data):
    data = str(data)
    seed = sum((ord(c) + i * 7) * (i + 2) for i, c in enumerate(data))
    random.seed(seed)
    return ''.join(random.sample(string.ascii_letters + string.digits + "@*-+_!?&$#%^", 10))

def jugoValidEmail(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email) is not None

def jugoSlugify(text):
    text = re.sub(r'[^a-zA-Z0-9-]+', '-', text.lower())
    return text.strip('-')


def jugoRun(app, host='127.0.0.1', port=8080):
    jugoPrint(f"🚀 Jugopy lancé sur http://{host}:{port}", "SUCCESS")
    with make_server(host, port, app) as server:
        server.serve_forever()


def jugoCreateApp(app_name: str, in_root: bool = False):
    base_dir = os.getcwd() if in_root else os.path.join(os.getcwd(), app_name)

    if os.path.exists(base_dir) and not in_root:
        print(f"❌ Le dossier '{app_name}' existe déjà.")
        return

    structure = [
        os.path.join(base_dir, "public", "html"),
        os.path.join(base_dir, "public", "css"),
        os.path.join(base_dir, "public", "js"),
        os.path.join(base_dir, "public", "images"),
        os.path.join(base_dir, "core"),
    ]

    for path in structure:
        os.makedirs(path, exist_ok=True)

    index_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <h1>Bienvenue sur {{ title }}</h1>
    <p>Votre app Jugopy fonctionne parfaitement 🎉</p>
</body>
</html>
"""
    error_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Erreur</title>
</head>
<body>
    <h1>Erreur détectée 🚨</h1>
    <p>{{ error }}</p>
</body>
</html>
"""

    app_py = f"""from jugopy import *

@jugoRoute('/')
def index(environ, startResponse):
    return jugoRender('index.html', {{'title': '{app_name.capitalize()}'}}, startResponse)

if __name__ == "__main__":
    jugoRun(jugoDispatch)
"""

    css_file = """body {
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    color: #222;
    text-align: center;
    margin-top: 5em;
}"""

    with open(os.path.join(base_dir, "public", "html", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    with open(os.path.join(base_dir, "public", "html", "error.html"), "w", encoding="utf-8") as f:
        f.write(error_html)
    with open(os.path.join(base_dir, "public", "css", "style.css"), "w", encoding="utf-8") as f:
        f.write(css_file)
    with open(os.path.join(base_dir, "app.py"), "w", encoding="utf-8") as f:
        f.write(app_py)

    print(f"✅ Projet '{app_name}' créé avec succès dans : {base_dir}")
    print("👉 Pour démarrer :")
    print(f"   cd {app_name}" if not in_root else "   (déjà dans le dossier)")
    print("   python app.py")
