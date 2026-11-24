from flask import Flask, render_template, jsonify, request
from informe_pdf import informe_bp
from flask_cors import CORS
import MallaCurricular as m
from grafoMaterias import (
    crear_grafo,
    exportar_grafo,
    dependientes_bfs,
    cadena_requisitos_dfs
)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://127.0.0.1:5500",
            "http://localhost:5500"
        ]
    }
})
app.register_blueprint(informe_bp)


def current():
    if not m.planes:
        return None
    return m.carrera_actual()


def serialize(materia):
    return {
        **materia,
        'estado': m.estado(materia),
        'pendientes': m.pendientes(materia),
        'requisitos_lista': [
            {
                'codigo': c,
                'nombre': (m.buscar(c) or {}).get('nombre', c),
                'aprobada': m.aprobada(c)
            }
            for c in m.requisitos(materia)
        ]
    }


# PAGINA PRINCIPAL

@app.get('/')
def index():
    return render_template('index.html')


# OBTENER TODAS LAS CARRERAS

@app.get('/api/planes')
def obtener_planes():
    return jsonify([
        {
            'id': plan['_id'],
            'nombre': plan['nombre'],
            'semestres': plan['semestres']
        }
        for plan in m.planes
    ])


# ESTADO ACADEMICO

@app.get('/api/estado')
def estado():
    plan = current()

    if not plan:
        return jsonify(
            error='No hay planes JSON válidos en planes_estudio'
        ), 404

    lista = [serialize(x) for x in m.materias(plan)]
    total = len(lista)

    semestres = []

    for i in range(len(plan['semestres'])):
        materias_semestre = [
            x for x in lista
            if x['semestre'] == i + 1
        ]

        semestres.append({
            'numero': i + 1,
            'materias': materias_semestre
        })

    progreso = {
        'total': total,
        'aprobadas': sum(
            x['estado'] == 'APROBADA'
            for x in lista
        ),
        'creditos_total': sum(
            int(x.get('creditos', 0))
            for x in lista
        ),
        'creditos_aprobados': sum(
            int(x.get('creditos', 0))
            for x in lista
            if x['estado'] == 'APROBADA'
        ),
        'bloqueadas': sum(
            x['estado'] == 'BLOQUEADA'
            for x in lista
        )
    }

    return jsonify(
        carrera={
            'id': plan['_id'],
            'nombre': plan['nombre']
        },
        carreras=[
            {
                'id': p['_id'],
                'nombre': p['nombre']
            }
            for p in m.planes
        ],
        semestres=semestres,
        progreso=progreso,
        notas=m.datos['notas'],
        horario=m.datos['horario'],
        minima=m.datos['minima']
    )


# CAMBIAR CARRERA

@app.post('/api/carrera')
def carrera():
    payload = request.get_json(silent=True) or {}
    id_ = str(payload.get('id', ''))

    if id_ not in [p['_id'] for p in m.planes]:
        return jsonify(
            error='Carrera desconocida'
        ), 400

    m.datos['carrera_id'] = id_
    m.guardar()

    return jsonify(ok=True)


# MARCAR MATERIA APROBADA

@app.post('/api/aprobada')
def aprobada():
    payload = request.get_json(silent=True) or {}

    codigo = str(
        payload.get('codigo', '')
    ).strip().upper()

    materia = m.buscar(codigo)

    if not materia:
        return jsonify(
            error='Materia desconocida'
        ), 404

    valor = payload.get('aprobada')

    if not isinstance(valor, bool):
        return jsonify(
            error='El estado debe ser verdadero o falso'
        ), 400

    if valor and m.pendientes(materia):
        return jsonify(
            error='Faltan requisitos: ' +
            ', '.join(m.pendientes(materia))
        ), 400

    if not valor:
        if codigo in m.datos['notas']:
            promedio = m.datos['notas'][codigo].get(
                'promedio', 0
            )

            if promedio >= m.datos['minima']:
                return jsonify(
                    error='La materia tiene una nota aprobatoria registrada'
                ), 400

    if valor and codigo not in m.datos['aprobadas']:
        m.datos['aprobadas'].append(codigo)

    if not valor and codigo in m.datos['aprobadas']:
        m.datos['aprobadas'].remove(codigo)

    m.guardar()

    return jsonify(ok=True)


# REGISTRAR NOTAS

@app.post('/api/notas')
def notas():
    payload = request.get_json(silent=True) or {}

    codigo = str(
        payload.get('codigo', '')
    ).strip().upper()

    if not m.buscar(codigo):
        return jsonify(
            error='Materia desconocida'
        ), 404

    parciales = payload.get('parciales')

    if (
        not isinstance(parciales, list)
        or len(parciales) != 3
        or any(
            type(x) not in (int, float)
            or not 0 <= x <= 100
            for x in parciales
        )
    ):
        return jsonify(
            error='Introduce exactamente 3 notas entre 0 y 100'
        ), 400

    promedio = round(
        sum(parciales) / 3, 2
    )

    m.datos['notas'][codigo] = {
        'parciales': parciales,
        'promedio': promedio
    }

    if promedio >= m.datos['minima']:
        if codigo not in m.datos['aprobadas']:
            m.datos['aprobadas'].append(codigo)

    elif codigo in m.datos['aprobadas']:
        m.datos['aprobadas'].remove(codigo)

    m.guardar()

    return jsonify(
        ok=True,
        promedio=promedio
    )


# AGREGAR HORARIO

@app.post('/api/horario')
def agregar_horario():
    p = request.get_json(silent=True) or {}

    codigo = str(
        p.get('materia', '')
    ).strip().upper()

    if not m.buscar(codigo):
        return jsonify(
            error='Materia desconocida'
        ), 404

    registro = {
        'materia': codigo,
        'dia': str(p.get('dia', '')).strip(),
        'hora': str(p.get('hora', '')).strip(),
        'aula': str(p.get('aula', '')).strip()
    }

    if not registro['dia'] or not registro['hora']:
        return jsonify(
            error='Día y hora son obligatorios'
        ), 400

    m.datos['horario'].append(registro)
    m.guardar()

    return jsonify(ok=True)


# ELIMINAR HORARIO

@app.delete('/api/horario/<int:indice>')
def eliminar_horario(indice):

    if not 0 <= indice < len(m.datos['horario']):
        return jsonify(
            error='Horario inexistente'
        ), 404

    m.datos['horario'].pop(indice)
    m.guardar()

    return jsonify(ok=True)


# CAMBIAR NOTA MINIMA

@app.post('/api/minima')
def minima():
    p = request.get_json(silent=True) or {}

    valor = p.get('minima')

    if (
        type(valor) not in (int, float)
        or not 0 <= valor <= 100
    ):
        return jsonify(
            error='Nota mínima inválida'
        ), 400

    m.datos['minima'] = valor
    m.guardar()

    return jsonify(ok=True)


# OBTENER GRAFO DE MATERIAS

@app.get('/api/grafo')
def grafo():
    plan = current()

    if not plan:
        return jsonify(
            error='No hay planes cargados'
        ), 404

    g = crear_grafo(m.materias(plan))

    return jsonify(
        exportar_grafo(
            g,
            m.datos['aprobadas']
        )
    )


# RECORRIDO BFS
# MATERIAS DEPENDIENTES

@app.get('/api/grafo/dependientes/<codigo>')
def dependientes(codigo):
    plan = current()

    if not plan:
        return jsonify(
            error='No hay planes cargados'
        ), 404

    g = crear_grafo(m.materias(plan))

    if codigo.upper() not in g['nodos']:
        return jsonify(
            error='Materia no encontrada'
        ), 404

    return jsonify(
        materias=dependientes_bfs(g, codigo)
    )


# RECORRIDO DFS
# CADENA DE PRERREQUISITOS

@app.get('/api/grafo/requisitos/<codigo>')
def cadena_requisitos(codigo):
    plan = current()

    if not plan:
        return jsonify(
            error='No hay planes cargados'
        ), 404

    g = crear_grafo(m.materias(plan))

    if codigo.upper() not in g['nodos']:
        return jsonify(
            error='Materia no encontrada'
        ), 404

    try:
        resultado = cadena_requisitos_dfs(
            g, codigo
        )

        return jsonify(
            materias=resultado
        )

    except ValueError as error:
        return jsonify(
            error=str(error)
        ), 422


# EJECUTAR SERVIDOR

if __name__ == '__main__':
    app.run(
        debug=True,
        port=5000
    )
