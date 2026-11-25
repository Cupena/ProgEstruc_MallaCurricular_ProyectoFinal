"""API para Go Live con biblioteca estándar. CERO clases propias, CERO pip."""
import json
import sqlite3
from pathlib import Path
from threading import Lock
from wsgiref.simple_server import make_server
from academico import evaluar, alternar_cursada
from validaciones import diagnosticar_estado
from faq import listar_preguntas, buscar_preguntas, responder_faq, responder_lote
from grafo_requisitos import crear_grafo, ruta_requisitos
from cola_enlazada import recorrido_bfs

BASE = Path(__file__).resolve().parent
DATABASE = BASE / 'ruta_academica.sqlite3'
LOCK = Lock()
MAX_BYTES = 18 * 1024 * 1024
ALLOWED_ORIGINS = {'http://127.0.0.1:5500', 'http://localhost:5500',
                   'http://127.0.0.1:5501', 'http://localhost:5501',
                   'http://127.0.0.1:5000', 'http://localhost:5000'}


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute('CREATE TABLE IF NOT EXISTS application_state '
                   '(id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)')


def save_state(state):
    with LOCK, sqlite3.connect(DATABASE) as db:
        db.execute('INSERT INTO application_state (id,payload) VALUES (1,?) '
                   'ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',
                   (json.dumps(state, ensure_ascii=False),))


def load_state():
    with sqlite3.connect(DATABASE) as db:
        row = db.execute('SELECT payload FROM application_state WHERE id=1').fetchone()
    return json.loads(row[0]) if row else None


def responder(start_response, status, payload, origin=None):
    contenido = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    headers = [('Content-Type', 'application/json; charset=utf-8'),
               ('Content-Length', str(len(contenido)))]
    if origin in ALLOWED_ORIGINS:
        headers += [('Access-Control-Allow-Origin', origin), ('Vary', 'Origin'),
                    ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type')]
    start_response(status, headers)
    return [contenido]


def aplicacion(environ, start_response):
    ruta = environ.get('PATH_INFO', '')
    metodo = environ.get('REQUEST_METHOD', 'GET')
    origin = environ.get('HTTP_ORIGIN')
    if metodo == 'OPTIONS':
        return responder(start_response, '200 OK', {}, origin)
    if metodo == 'GET' and ruta == '/api/diagnostico':
        return responder(
            start_response, '200 OK',
            diagnosticar_estado(load_state() or {}), origin
        )
    if metodo == 'GET' and ruta == '/api/faq':
        return responder(start_response, '200 OK',
                         {'preguntas': listar_preguntas()}, origin)
    if metodo == 'GET':
        if ruta == '/api/salud':
            return responder(start_response, '200 OK', {'ok': True, 'servidor': 'Python sin dependencias',
                                                       'estructuras': ['grafo dirigido', 'cola enlazada FIFO']}, origin)
        if ruta == '/api/estado':
            return responder(start_response, '200 OK', {'state': load_state()}, origin)
        return responder(start_response, '404 Not Found', {'error': 'Ruta no encontrada'}, origin)
    if metodo != 'POST' or ruta not in ('/api/sincronizar', '/api/evaluar', '/api/alternar-materia', '/api/grafo', '/api/faq'):
        return responder(start_response, '404 Not Found', {'error': 'Ruta no encontrada'}, origin)
    try:
        size = int(environ.get('CONTENT_LENGTH') or '0')
        if not 0 < size <= MAX_BYTES:
            return responder(start_response, '413 Content Too Large', {'error': 'Tamaño inválido'}, origin)
        data = json.loads(environ['wsgi.input'].read(size))
        if not isinstance(data, dict):
            raise ValueError('Se requiere un objeto JSON')
        if ruta == '/api/faq':
            state = data.get('state')
            ci = int(data.get('career', 0))

            if state is None:
                state = load_state() or {}

            if not isinstance(state, dict):
                raise ValueError('Estado academico invalido')

            if 'buscar' in data:
                result = {'preguntas': buscar_preguntas(data['buscar'])}
            elif 'preguntas' in data:
                result = {'respuestas': responder_lote(
                    state, ci, data['preguntas']
                )}
            else:
                result = responder_faq(
                    state, ci,
                    data.get('pregunta'),
                    data.get('materia')
                )
        elif ruta == '/api/alternar-materia':
            state = data.get('state')
            key = data.get('key')
            ci = int(data.get('career', 0))
            if not isinstance(state, dict) or not isinstance(key, str) or ci not in (0, 1):
                raise ValueError('Estado, materia o carrera inválidos')
            updated = alternar_cursada(state, key, ci, data.get('value'))
            save_state(updated)
            result = {'state': updated, 'evaluation': evaluar(updated)}
        elif ruta == '/api/grafo':
            state = data.get('state') or data
            ci = int(data.get('career', 0))
            if ci not in (0, 1):
                raise ValueError('Carrera inválida')
            careers = state.get('careers') or []
            courses = (careers[ci] or {}).get('courses') or [] if ci < len(careers) else []
            grafo = crear_grafo(courses)
            key = str(data.get('key') or '')
            result = {'vertices': list(grafo['materias']), 'adyacencia': grafo['adyacencia'],
                      'requisitos': grafo['requisitos']}
            if key:
                result['cadena_requisitos'] = ruta_requisitos(grafo, key)
                result['dependientes_bfs'] = recorrido_bfs(grafo, key)
        else:
            result = evaluar(data)
            if ruta == '/api/sincronizar':
                save_state(data)
        return responder(start_response, '200 OK', result, origin)
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return responder(start_response, '400 Bad Request', {'error': str(exc)}, origin)


def iniciar():
    init_db()
    with make_server('127.0.0.1', 5000, aplicacion) as server:
        print('Servidor Python listo: http://127.0.0.1:5000/api/salud', flush=True)
        print('Abre index.html con Go Live (puerto 5500).', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Servidor detenido.')


if __name__ == '__main__':
    iniciar()
