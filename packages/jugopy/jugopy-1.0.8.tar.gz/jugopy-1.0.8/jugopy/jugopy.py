import os
import re
import json
import http.cookies
import random
import string
import urllib.parse
import pymysql
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from wsgiref.simple_server import make_server
from typing import Dict, Any, Optional, Callable, List, Tuple, Union


BASE_DIR = Path.cwd()
PUBLIC_DIR = BASE_DIR / "public"
HTML_DIR = PUBLIC_DIR / "html"

MIME_TYPES = {
    'css': 'text/css',
    'js': 'application/javascript',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'ico': 'image/x-icon',
    'svg': 'image/svg+xml',
    'webp': 'image/webp',
    'woff': 'font/woff',
    'woff2': 'font/woff2',
    'ttf': 'font/ttf',
}

DIRECTORIES = {
    'css': PUBLIC_DIR / 'css',
    'js': PUBLIC_DIR / 'js',
    'png': PUBLIC_DIR / 'images',
    'jpg': PUBLIC_DIR / 'images',
    'jpeg': PUBLIC_DIR / 'images',
    'gif': PUBLIC_DIR / 'images',
    'ico': PUBLIC_DIR / 'images',
    'svg': PUBLIC_DIR / 'images',
    'webp': PUBLIC_DIR / 'images',
    'woff': PUBLIC_DIR / 'fonts',
    'woff2': PUBLIC_DIR / 'fonts',
    'ttf': PUBLIC_DIR / 'fonts',
}

ERROR_PAGE = HTML_DIR / 'error.html'
SESSION_FILE = BASE_DIR / 'sessions.json'

TEMPLATE_ENV = Environment(loader=FileSystemLoader(str(HTML_DIR)))

ROUTES = {}
STATIC_CACHE = {}
MIDDLEWARES = []


class JugoColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    LEVEL_COLORS = {
        'INFO': BLUE,
        'SUCCESS': GREEN,
        'WARNING': WARNING,
        'ERROR': FAIL,
        'HEADER': HEADER
    }


def jugoPrint(message: str, level: str = "INFO") -> None:
    color = JugoColors.LEVEL_COLORS.get(level, JugoColors.ENDC)
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {level}: {message}{JugoColors.ENDC}")


def loadConfig():
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    return {
        'db': [
            os.getenv('DB_HOST', 'localhost'),
            os.getenv('DB_USER', 'root'),
            os.getenv('DB_PASS', ''),
            os.getenv('DB_NAME', 'app_db')
        ],
        'secret': os.getenv('APP_SECRET', 'change-me-in-production'),
        'debug': os.getenv('DEBUG', 'False').lower() == 'true'
    }


def jugoServeError(status: str, content: str, startResponse, showDetails: bool = True) -> list[bytes]:
    startResponse(status, [('Content-Type', 'text/html')])
    config = loadConfig()
    
    if not showDetails and not config['debug']:
        content = "Erreur interne, veuillez contacter l'administrateur"
    
    try:
        with open(ERROR_PAGE, 'rb') as f:
            html = f.read()
        html = html.replace(b'{{ error }}', str(content).encode('utf-8'))
        return [html]
    except Exception:
        return [f"<h1>{status}</h1><p>{content}</p>".encode('utf-8')]


def jugoRoute(path: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        ROUTES[path] = func
        return func
    return decorator


def jugoMiddleware(func):
    MIDDLEWARES.append(func)
    return func


@jugoMiddleware
def logMiddleware(environ):
    jugoPrint(f"📨 {environ['REQUEST_METHOD']} {environ['PATH_INFO']}")


def _isStaticFile(path: str) -> bool:
    filename = path.split('/')[-1]
    return '.' in filename and filename not in ['', '.', '..']


def _getStaticFilePath(filePath: str) -> Optional[Path]:
    filename = filePath.split('/')[-1]
    ext = Path(filename).suffix.lstrip('.')
    
    if not ext or ext not in DIRECTORIES or ext not in MIME_TYPES:
        return None
    
    folder = DIRECTORIES[ext]
    return folder / filename


def _serveStaticFile(filePath: str, startResponse) -> Optional[list[bytes]]:
    if filePath in STATIC_CACHE:
        ext = Path(filePath).suffix.lstrip('.')
        mimeType = MIME_TYPES.get(ext, 'application/octet-stream')
        startResponse('200 OK', [('Content-Type', mimeType)])
        return [STATIC_CACHE[filePath]]
    
    fullPath = _getStaticFilePath(filePath)
    if not fullPath or not fullPath.exists():
        return None
    
    try:
        with open(fullPath, 'rb') as f:
            content = f.read()
        
        if len(content) < 1024 * 1024:
            STATIC_CACHE[filePath] = content
        
        ext = Path(filePath).suffix.lstrip('.')
        mimeType = MIME_TYPES.get(ext, 'application/octet-stream')
        startResponse('200 OK', [('Content-Type', mimeType)])
        return [content]
    except Exception as e:
        jugoPrint(f"Erreur lecture fichier statique {filePath}: {e}", "ERROR")
        return None


def jugoDispatch(environ, startResponse) -> list[bytes]:
    path = environ.get('PATH_INFO', '/')
    
    for middleware in MIDDLEWARES:
        middleware(environ)
    
    if _isStaticFile(path):
        result = _serveStaticFile(path, startResponse)
        if result:
            return result
        return jugoServeError('404 Not Found', f"Fichier {path} introuvable", startResponse, showDetails=True)
    
    handler = ROUTES.get(path)
    if handler:
        try:
            return handler(environ, startResponse)
        except Exception as e:
            config = loadConfig()
            errorMsg = str(e)
            jugoPrint(f"Erreur 500: {errorMsg}", "ERROR")
            
            if config['debug']:
                return jugoServeError('500 Internal Server Error', errorMsg, startResponse, showDetails=True)
            else:
                return jugoServeError('500 Internal Server Error', errorMsg, startResponse, showDetails=False)
    
    return jugoServeError('404 Not Found', f"Route {path} introuvable", startResponse, showDetails=True)


def jugoRender(templateName: str, context: Optional[Dict[str, Any]] = None, startResponse = None) -> list[bytes]:
    context = context or {}
    try:
        template = TEMPLATE_ENV.get_template(templateName)
        html = template.render(**context)
        startResponse('200 OK', [('Content-Type', 'text/html')])
        return [html.encode('utf-8')]
    except Exception as e:
        config = loadConfig()
        errorMsg = f"Erreur rendu: {e}"
        jugoPrint(errorMsg, "ERROR")
        
        if config['debug']:
            return jugoServeError('500 Internal Server Error', errorMsg, startResponse, showDetails=True)
        else:
            return jugoServeError('500 Internal Server Error', errorMsg, startResponse, showDetails=False)


def jugoParsePost(environ) -> Dict[str, Any]:
    contentType = environ.get("CONTENT_TYPE", "").lower()
    contentLength = int(environ.get("CONTENT_LENGTH", 0))
    
    if contentLength == 0:
        return {}
    
    body = environ["wsgi.input"].read(contentLength)

    if contentType.startswith("application/x-www-form-urlencoded"):
        data = urllib.parse.parse_qs(body.decode("utf-8"))
        return {k: v[0] for k, v in data.items()}

    elif contentType.startswith("multipart/form-data"):
        boundary = contentType.split("boundary=")[-1].strip()
        if not boundary:
            return {}
        data = {}
        parts = body.split(f"--{boundary}".encode())
        for part in parts:
            if b"Content-Disposition" in part:
                try:
                    header, content = part.split(b"\r\n\r\n", 1)
                    content = content.strip(b"\r\n--")
                    nameMatch = re.search(rb'name="([^"]+)"', header)
                    if nameMatch:
                        name = nameMatch.group(1).decode("utf-8")
                        data[name] = content.decode("utf-8", errors="ignore")
                except Exception:
                    continue
        return data

    return {}


def jugoSetCookie(environ, name: str, content: Any) -> None:
    cookies = http.cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
    val = json.dumps(content) if isinstance(content, (dict, list)) else str(content)
    cookies[name] = val
    environ['HTTP_COOKIE'] = '; '.join(f"{k}={v.value}" for k, v in cookies.items())


def jugoGetCookie(environ, name: str) -> Any:
    cookies = http.cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
    if name in cookies:
        val = cookies[name].value
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return val
    return None


def jugoGetSession(sessionId: str) -> Dict[str, Any]:
    if not SESSION_FILE.exists():
        return {}
    try:
        with open(SESSION_FILE, 'r') as f:
            sessions = json.load(f)
        
        sessionData = sessions.get(sessionId, {})
        if sessionData.get('expires', 0) < datetime.now().timestamp():
            return {}
        
        return sessionData.get('data', {})
    except Exception:
        return {}


def jugoSaveSession(sessionId: str, data: Dict[str, Any], expireHours: int = 24) -> None:
    sessions = {}
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, 'r') as f:
                sessions = json.load(f)
        except Exception:
            pass
    
    sessions[sessionId] = {
        'data': data,
        'expires': datetime.now().timestamp() + (expireHours * 3600)
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(sessions, f)


def connDb(config: list) -> pymysql.connections.Connection:
    try:
        conn = pymysql.connect(
            host=config[0],
            user=config[1],
            password=config[2],
            database=config[3]
        )
        jugoPrint(f"✅ Connexion DB réussie: {config[3]}", "SUCCESS")
        return conn
    except Exception as e:
        jugoPrint(f"❌ Erreur connexion DB: {e}", "ERROR")
        raise


def runSql(sql: str, params: tuple = None, conn = None) -> Union[List[Dict], int, None]:
    if conn is None:
        config = loadConfig()
        try:
            conn = connDb(config['db'])
        except Exception as e:
            jugoPrint(f"Erreur connexion DB dans runSql: {e}", "ERROR")
            return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            
            if sql.strip().upper().startswith(('SELECT', 'SHOW', 'DESC')):
                result = cursor.fetchall()
                columns = [col[0] for col in cursor.description] if cursor.description else []
                return [dict(zip(columns, row)) for row in result]
            else:
                conn.commit()
                return cursor.rowcount
                
    except Exception as e:
        jugoPrint(f"Erreur SQL: {e}", "ERROR")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def jugoCrypt(data: Any) -> str:
    data = str(data)
    seed = sum((ord(c) + i * 7) * (i + 2) for i, c in enumerate(data))
    random.seed(seed)
    return ''.join(random.sample(string.ascii_letters + string.digits + "@*-+_!?&$#%^", 10))


def jugoCsrfToken() -> str:
    return jugoCrypt(str(random.random()))


def jugoValidateCsrf(environ, tokenName='csrf_token'):
    formData = jugoParsePost(environ)
    sessionId = jugoGetCookie(environ, 'session_id')
    session = jugoGetSession(sessionId) if sessionId else {}
    return formData.get(tokenName) == session.get('csrf_token')


def jugoValidEmail(email: str) -> bool:
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email) is not None


def jugoSlugify(text: str) -> str:
    text = re.sub(r'[^a-zA-Z0-9-]+', '-', text.lower())
    return text.strip('-')


def jugoRedirect(location: str, startResponse, extraHeaders: Optional[list] = None) -> list[bytes]:
    headers = [("Location", location)]
    if extraHeaders:
        headers.extend(extraHeaders)
    startResponse('302 Found', headers)
    return [b'']


def jugoCors(headers=None):
    corsHeaders = [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ]
    if headers:
        corsHeaders.extend(headers)
    return corsHeaders


def jugoRun(app, host: str = '127.0.0.1', port: int = 8080) -> None:
    jugoPrint(f"🚀 Jugopy lancé sur http://{host}:{port}", "SUCCESS")
    with make_server(host, port, app) as server:
        server.serve_forever()


def jugoCreateApp(appName: str, inRoot: bool = False) -> None:
    baseDir = Path.cwd() if inRoot else Path.cwd() / appName

    if baseDir.exists() and not inRoot:
        print(f"❌ Le dossier '{appName}' existe déjà.")
        return

    structure = [
        baseDir / "public" / "html",
        baseDir / "public" / "css",
        baseDir / "public" / "js",
        baseDir / "public" / "images",
        baseDir / "public" / "fonts",
        baseDir / "core",
    ]

    for path in structure:
        path.mkdir(parents=True, exist_ok=True)

    indexHtml = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <h1>Bienvenue sur {{ title }}</h1>
    <p>Votre app Jugopy fonctionne parfaitement 🎉</p>
    <img src="/images/logo.png" alt="Logo" width="100">
</body>
</html>"""

    errorHtml = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Erreur</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <h1>{{ status }}</h1>
    <p>{{ error }}</p>
</body>
</html>"""

    notFoundHtml = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Page non trouvée</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <h1>Page non trouvée 😕</h1>
    <p>La page <strong>{{ path }}</strong> n'existe pas.</p>
</body>
</html>"""

    envExample = """DB_HOST=localhost
DB_USER=root
DB_PASS=
DB_NAME=myapp_db
APP_SECRET=change-me-in-production
DEBUG=True"""

    appPy = f"""from jugopy import *

config = loadConfig()

@jugoRoute('/')
def index(environ, startResponse):
    users = runSql('SELECT * FROM users WHERE id = %s', (1,))
    return jugoRender('index.html', {{'title': '{appName.capitalize()}', 'users': users}}, startResponse)

if __name__ == "__main__":
    jugoRun(jugoDispatch)
"""

    cssFile = """body {
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    color: #222;
    text-align: center;
    margin-top: 5em;
    line-height: 1.6;
}

h1 {
    color: #2c3e50;
    margin-bottom: 1em;
}"""

    (baseDir / "public" / "html" / "index.html").write_text(indexHtml, encoding='utf-8')
    (baseDir / "public" / "html" / "error.html").write_text(errorHtml, encoding='utf-8')
    (baseDir / "public" / "html" / "404.html").write_text(notFoundHtml, encoding='utf-8')
    (baseDir / "public" / "css" / "style.css").write_text(cssFile, encoding='utf-8')
    (baseDir / ".env.example").write_text(envExample, encoding='utf-8')
    (baseDir / "app.py").write_text(appPy, encoding='utf-8')

    print(f"✅ Projet '{appName}' créé avec succès dans : {baseDir}")
    print("👉 Pour démarrer :")
    print(f"   cd {appName}" if not inRoot else "   (déjà dans le dossier)")
    print("   cp .env.example .env")
    print("   python app.py")