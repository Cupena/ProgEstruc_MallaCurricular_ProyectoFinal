"""Autenticación modular sin clases, solo biblioteca estándar."""
import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from http.cookies import SimpleCookie

SESSION_SECONDS = 7 * 24 * 3600
ITERATIONS = 310_000


def preparar_tablas(db):
    db.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE COLLATE NOCASE,
        sal BLOB NOT NULL,
        clave_hash BLOB NOT NULL,
        creado INTEGER NOT NULL)''')
    db.execute('''CREATE TABLE IF NOT EXISTS sesiones (
        token_hash TEXT PRIMARY KEY,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        vence INTEGER NOT NULL)''')
    db.execute('''CREATE TABLE IF NOT EXISTS estados_usuario (
        usuario_id INTEGER PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
        payload TEXT NOT NULL)''')


def validar_registro(nombre, correo, clave):
    nombre = str(nombre or '').strip()
    correo = str(correo or '').strip().lower()
    if not (2 <= len(nombre) <= 80):
        raise ValueError('El nombre debe tener entre 2 y 80 caracteres.')
    if len(correo) > 254 or not re.fullmatch(r'[^\s@]+@uamv\.edu\.ni', correo):
        raise ValueError('Utilizá un correo institucional @uamv.edu.ni válido.')
    if not isinstance(clave, str) or len(clave) < 10 or len(clave) > 128:
        raise ValueError('La contraseña debe tener entre 10 y 128 caracteres.')
    return nombre, correo


def derivar_clave(clave, sal):
    return hashlib.pbkdf2_hmac('sha256', clave.encode('utf-8'), sal, ITERATIONS)


def registrar(db, nombre, correo, clave):
    nombre, correo = validar_registro(nombre, correo, clave)
    sal = secrets.token_bytes(16)
    try:
        cursor = db.execute('INSERT INTO usuarios (nombre,correo,sal,clave_hash,creado) VALUES (?,?,?,?,?)',
                            (nombre, correo, sal, derivar_clave(clave, sal), int(time.time())))
    except sqlite3.IntegrityError:
        raise ValueError('Ya existe una cuenta con ese correo.') from None
    return {'id': cursor.lastrowid, 'nombre': nombre, 'correo': correo}


def autenticar(db, correo, clave):
    correo = str(correo or '').strip().lower()
    if not re.fullmatch(r'[^\s@]+@uamv\.edu\.ni', correo):
        raise ValueError('Utilizá tu correo institucional @uamv.edu.ni.')
    row = db.execute('SELECT id,nombre,correo,sal,clave_hash FROM usuarios WHERE correo=?', (correo,)).fetchone()
    if not row or not isinstance(clave, str) or not hmac.compare_digest(derivar_clave(clave, row[3]), row[4]):
        raise ValueError('Correo o contraseña incorrectos.')
    return {'id': row[0], 'nombre': row[1], 'correo': row[2]}


def crear_sesion(db, usuario_id):
    token = secrets.token_urlsafe(32)
    db.execute('INSERT INTO sesiones(token_hash,usuario_id,vence) VALUES (?,?,?)',
               (hashlib.sha256(token.encode()).hexdigest(), usuario_id, int(time.time()) + SESSION_SECONDS))
    return token


def leer_cookie(environ):
    cookies = SimpleCookie()
    try:
        cookies.load(environ.get('HTTP_COOKIE', ''))
        return cookies['ra_sesion'].value if 'ra_sesion' in cookies else None
    except Exception:
        return None


def usuario_actual(db, environ):
    token = leer_cookie(environ)
    if not token:
        return None
    row = db.execute('''SELECT u.id,u.nombre,u.correo FROM sesiones s
                        JOIN usuarios u ON u.id=s.usuario_id
                        WHERE s.token_hash=? AND s.vence>?''',
                     (hashlib.sha256(token.encode()).hexdigest(), int(time.time()))).fetchone()
    return {'id': row[0], 'nombre': row[1], 'correo': row[2]} if row else None


def cerrar_sesion(db, environ):
    token = leer_cookie(environ)
    if token:
        db.execute('DELETE FROM sesiones WHERE token_hash=?', (hashlib.sha256(token.encode()).hexdigest(),))


def cookie_sesion(token, environ):
    # HTTP local en 127.0.0.1; Secure se activa al desplegar detrás de HTTPS.
    secure = '; Secure' if environ.get('wsgi.url_scheme') == 'https' else ''
    return f'ra_sesion={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age={SESSION_SECONDS}{secure}'


def cookie_borrada():
    return 'ra_sesion=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0'
