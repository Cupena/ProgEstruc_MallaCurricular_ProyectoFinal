"""Servidor Flask de Ruta Académica. Ejecutar: python app.py"""
import json
import sqlite3
from pathlib import Path
from threading import Lock
from flask import Flask, jsonify, render_template, request
from academico import evaluar, alternar_cursada

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder='static', template_folder='templates')
app.json.ensure_ascii = False
DB = ROOT / 'ruta_academica.sqlite3'
lock = Lock()
MAX_PAYLOAD = 18 * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = MAX_PAYLOAD


def database():
    with sqlite3.connect(DB) as con:
        con.execute('CREATE TABLE IF NOT EXISTS application_state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)')


def persist(state):
    with lock, sqlite3.connect(DB) as con:
        con.execute('INSERT INTO application_state (id,payload) VALUES (1,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',
                    (json.dumps(state, ensure_ascii=False),))


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/api/estado')
def load_state():
    database()
    with sqlite3.connect(DB) as con:
        record = con.execute('SELECT payload FROM application_state WHERE id=1').fetchone()
    return jsonify({'state': json.loads(record[0]) if record else None})


@app.post('/api/sincronizar')
def sync():
    state = request.get_json(silent=True)
    if not isinstance(state, dict):
        return jsonify({'error': 'Se requiere un objeto JSON de estado'}), 400
    try:
        result = evaluar(state)
    except (ValueError, TypeError, KeyError) as exc:
        return jsonify({'error': f'Estado académico inválido: {exc}'}), 400
    persist(state)
    return jsonify(result)


@app.post('/api/alternar-materia')
def toggle():
    payload = request.get_json(silent=True) or {}
    state = payload.get('state')
    if not isinstance(state, dict) or not isinstance(payload.get('key'), str):
        return jsonify({'error': 'Estado y código de materia requeridos'}), 400
    ci = int(payload.get('career', 0))
    if ci not in (0, 1):
        return jsonify({'error': 'Índice de carrera inválido'}), 400
    state = alternar_cursada(state, payload['key'], ci, payload.get('value'))
    persist(state)
    return jsonify({'state': state, 'evaluation': evaluar(state)})


@app.post('/api/evaluar')
def evaluate_only():
    state = request.get_json(silent=True)
    if not isinstance(state, dict):
        return jsonify({'error': 'Estado JSON requerido'}), 400
    try:
        return jsonify(evaluar(state))
    except (ValueError, TypeError, KeyError) as exc:
        return jsonify({'error': str(exc)}), 400


if __name__ == '__main__':
    database()
    app.run(host='127.0.0.1', port=5000, debug=True)
