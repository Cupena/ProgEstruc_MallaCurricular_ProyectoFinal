from flask import Flask, render_template, jsonify, request
from informe_pdf import informe_bp
from flask_cors import CORS
import MallaCurricular as m

# Importamos las funciones necesarias para trrabajar con el grafo de materias y sus relaciones de prerrequisitos.
from grafoMaterias import (
    crear_grafo,
    exportar_grafo,
    dependientes_bfs,
    cadena_requisitos_dfs
)


# CONFIGURACIÓN INICIAL DEL FLASK
# Se crea la aplicación Flask. __name__ permite que Flask identifique la ubicación del proyecto.
app = Flask(__name__)

'''
    Se habilita CORS para permitir que el frontend pueda comunicarse con el backend aunque se encuentren en diferentes puertos. 
En este caso, únicamente permitimos solicitudes desde:
    - http://127.0.0.1:5500
    - http://localhost:5500
    Las turas autorizadas son las que comienzan con /api/.

'''
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://127.0.0.1:5500",
            "http://localhost:5500"
        ]
    }
})

# Registramos el Blueprint encargado de generar los informes PDF. Esto permite incorporar sus rutas a la aplicación principal.
app.register_blueprint(informe_bp)

# FUNCIONES AUXILIARES
def current():
    # Verificamos si existen planes de estudio cargados. Si no hay ninguno, devolvemos None.
    if not m.planes:
        return None

    # Obtenemos y devolvemos la carrera seleccionada actualmente.
    return m.carrera_actual()


def serialize(materia):
    # Convertimos la información de una materia en un diccionario que posteriormente podrá enviarse al frontend como JSON.
    return {
        # Copiamos todas las propiedades originales de la materia.
        **materia,

        # Agregamos el estado académico de la materia: Aprobada, Pendiente, Bloqueada, etc.
        'estado': m.estado(materia),

        # Obtenemos los prerrequisitos que todavía no se han aprobado.
        'pendientes': m.pendientes(materia),

        # Creamos una lista con información de cada prerrequisito.
        'requisitos_lista': [
            {
                # Código identificador del prerrequisito.
                'codigo': c,

                # Buscamos el nombre de la materia. Si no se encuentra, utilizamos su código.
                'nombre': (m.buscar(c) or {}).get('nombre', c),
                
                # Indicamos si el prerrequisitos ya fue aprobado.
                'aprobada': m.aprobada(c)
            }

            # Recorremos todos los prerrequisitos de la materia.
            for c in m.requisitos(materia)
        ]
    }


# PÁGINA PRINCIPAL

# GET: Se utiliza para solicitar información al servidor.
@app.get('/')
def index():
    # Renderizamos y mostramos el archivo index.html que se encuentra dentro de la carpeta templates.
    return render_template('index.html')


# OBTENER TODAS LAS CARRERAS

@app.get('/api/planes')
def obtener_planes():
    # Recorremos todos los planes de estudio disponibles. Construimos una lista de diccionarios con su información.
    return jsonify([
        {
            # Identificador único de la carrera.
            'id': plan['_id'],

            # Nombre de la carrera.
            'nombre': plan['nombre'],

            #  Cantidad y organización de sus semestres.
            'semestres': plan['semestres']
        }
        # Recorremos cada plan almacecnado en m.planes.
        for plan in m.planes
    ])


# ESTADO ACADEMICO

@app.get('/api/estado')
def estado():
    # Obtenemos la carrera seleccionada actualmente.
    plan = current()

    # Si no existe una carrera seleccionada o no hay planes, devolvemos un mensaje de error con código HTTP 404.
    if not plan:
        return jsonify(
            error='No hay planes JSON válidos en planes_estudio'
        ), 404

    # Obtenemos todas las materias de la carrera. serialize() agrega información sobre su estado, sus prerrequisitos y las materias pendientes.
    lista = [serialize(x) for x in m.materias(plan)]

    # Calculamos la cantidad total de materias.
    total = len(lista)

    # Inicializamos una lista donde organizaremos las materias según el semestre al que pertenecen.
    semestres = []

    # Recorremos todos los semestres de la carrera.
    for i in range(len(plan['semestres'])):
        # Filtramos las materias para obtener únicamente las que pertenecen al semestre actual.
        materias_semestre = [
            x for x in lista
            if x['semestre'] == i + 1
        ]

        # Agregamos el semestre y sus materias a la lista.
        semestres.append({
            'numero': i + 1,
            'materias': materias_semestre
        })


    # CÁLCULO DEL PROGRESO ACADÉMICO   

    progreso = {
        # Cantidad total de materias del plan de estudio.
        'total': total,

        # sum() cuenta cuántas materias tienen estado Aprobada.
        'aprobadas': sum(
            x['estado'] == 'APROBADA'
            for x in lista
        ),

        # Sumamos los créditos de todas las materias.
        'creditos_total': sum(
            int(x.get('creditos', 0))
            for x in lista
        ),

        # Sumamos únicamente los créditos de las materias aprobadas.
        'creditos_aprobados': sum(
            int(x.get('creditos', 0))
            for x in lista
            if x['estado'] == 'APROBADA'
        ),

        # Contamos cuántas materias están bloqueadas. Una materia bloqueada no puede cursarse porque todavía no se han aprobado sus prerrequisitos.
        'bloqueadas': sum(
            x['estado'] == 'BLOQUEADA'
            for x in lista
        )
    }


    # Enviamos toda la información al frontend en formado JSON.
    return jsonify(
        # Información de la carrera seleccionada.
        carrera={
            'id': plan['_id'],
            'nombre': plan['nombre']
        },

        # Lista de todas las carreras disponibles.
        carreras=[
            {
                'id': p['_id'],
                'nombre': p['nombre']
            }
            for p in m.planes
        ],

        # Materias organizadas por semestre.
        semestres=semestres,

        # Estadísticas del progreso académico.
        progreso=progreso,

        # Notas registradas por el usuario.
        notas=m.datos['notas'],

        # Horario académico registrado.
        horario=m.datos['horario'],

        # Nota mónima necesaria para aprobar.
        minima=m.datos['minima']
    )


# CAMBIAR CARRERA

# POST: Se utiliza para enviar información al servidor y realizar una modificación.
@app.post('/api/carrera')
def carrera():
    # Obtenemos los datos JSON enviados por el frontend. Si no se recibe información válida, utilizamos un diccionario vacío.
    payload = request.get_json(silent=True) or {}

    # Extraemos el identificador de la carrera.
    id_ = str(payload.get('id', ''))

    # Comprobamos que el identificador recibido pertenezca a alguna de las carreras disponibles.
    if id_ not in [p['_id'] for p in m.planes]:
        return jsonify(
            error='Carrera desconocida'
        ), 400

    # Actualziamos el identificador de la carrera seleccionada.
    m.datos['carrera_id'] = id_

    # Guardamos los cambios en el archivo de datos.
    m.guardar()

    # Informamos que la operación se realizó correctamente.
    return jsonify(ok=True)


# MARCAR MATERIA APROBADA

@app.post('/api/aprobada')
def aprobada():
    # Recibimos los datos enviados desde el frontend.
    payload = request.get_json(silent=True) or {}

    # Obtenemos el código de la materia.
    codigo = str(
        payload.get('codigo', '')
    ).strip().upper()

    # Buscamos la materia en los planes de estudio.
    materia = m.buscar(codigo)

    if not materia:
        return jsonify(
            error='Materia desconocida'
        ), 404

    valor = payload.get('aprobada')

    # Obtenemos el valor que indica si la materia debe marcarse como aprobada o no.
    if not isinstance(valor, bool):
        return jsonify(
            error='El estado debe ser verdadero o falso'
        ), 400

    # Si queremos aprobar la materia, verificamos que todos sus prerrequisitos estén aprobados.
    if valor and m.pendientes(materia):
        return jsonify(
            error='Faltan requisitos: ' +
            ', '.join(m.pendientes(materia))
        ), 400

    # Si queremos quitar el estado de aprobada, comprobamos que no exista una nota aprobatoria registrada.
    if not valor:
        if codigo in m.datos['notas']:
            # Recuperamos el promedio de la materia. Si no existe utilizamos 0.
            promedio = m.datos['notas'][codigo].get(
                'promedio', 0
            )

            # Si el promedio alcanza la nota mínima, no permitimos quitar su aprobación manualmente.
            if promedio >= m.datos['minima']:
                return jsonify(
                    error='La materia tiene una nota aprobatoria registrada'
                ), 400

    # Si queremos aprobar la materia y todavía no aparece en la lista de aprobadas, la agregamos.
    if valor and codigo not in m.datos['aprobadas']:
        m.datos['aprobadas'].append(codigo)

    # Si queremos quitar su aprobación y aparece en la lista, eliminamos su código.
    if not valor and codigo in m.datos['aprobadas']:
        m.datos['aprobadas'].remove(codigo)

    # Guardamos los cambios realizados.
    m.guardar()

    return jsonify(ok=True)


# REGISTRAR NOTAS

@app.post('/api/notas')
def notas():
    # Recibimos las notas enviadas desde el frontend.
    payload = request.get_json(silent=True) or {}

    # Obtenemos y normalizamos el código de la materia.
    codigo = str(
        payload.get('codigo', '')
    ).strip().upper()

    # Comprobamos que la materia exista.
    if not m.buscar(codigo):
        return jsonify(
            error='Materia desconocida'
        ), 404

    # Obtenemos la lista de las tres notas parciales.
    parciales = payload.get('parciales')

    '''
    Validamos que:
        1. El dato recibido sea una lista.
        2. Contenga exactamente tres notas.
        3. Cada nota sea un entero o decimal.
        4. Cada nota esté entre 0 y 100.
    '''
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

    # Calculamos el promedio de las tres notas.
    promedio = round(
        sum(parciales) / 3, 2
    )

    # Guardamos las notas parciales y el promedio utilizando el código de la materia como identificador.
    m.datos['notas'][codigo] = {
        'parciales': parciales,
        'promedio': promedio
    }

    # Comprobamos si el promedio alcanza la nota mínima.
    if promedio >= m.datos['minima']:
        # Si aprobó y todavía no aparece en la lista, agregamos automáticamente la materia como aprobada.
        if codigo not in m.datos['aprobadas']:
            m.datos['aprobadas'].append(codigo)

    # Si no alcanza la nota mínima, quitamos su aprobación si anteriormente estbaa registrada.
    elif codigo in m.datos['aprobadas']:
        m.datos['aprobadas'].remove(codigo)

    # Guardamos las notas y el estado actualizado.
    m.guardar()

    # Devolvemos el resultado y el promedio calculado.
    return jsonify(
        ok=True,
        promedio=promedio
    )


# AGREGAR HORARIO

@app.post('/api/horario')
def agregar_horario():
    # Recibimos la información del horario.
    p = request.get_json(silent=True) or {}

    # Obtenemos el código de la materia.
    codigo = str(
        p.get('materia', '')
    ).strip().upper()

    # Verificamos que la materia exista.
    if not m.buscar(codigo):
        return jsonify(
            error='Materia desconocida'
        ), 404

    # Creamos un diccionario con los datos del horario.
    registro = {
        'materia': codigo,
        'dia': str(p.get('dia', '')).strip(),
        'hora': str(p.get('hora', '')).strip(),
        'aula': str(p.get('aula', '')).strip()
    }

    # Comprobamos que el día y la hora no estén vacíos. Ambos son campos obligatorios.
    if not registro['dia'] or not registro['hora']:
        return jsonify(
            error='Día y hora son obligatorios'
        ), 400

    # Agregamos el nuevo registro a la lista de horarios.
    m.datos['horario'].append(registro)

    # Guardamos los cambios.
    m.guardar()

    return jsonify(ok=True)


# ELIMINAR HORARIO
# DELETE: Se utiliza para eliminar información.
# <int:indice> recibe un número entero directamente desde la URL.
@app.delete('/api/horario/<int:indice>')
def eliminar_horario(indice):
    # Verificamos que el índice recibido corresponda a una posición existente dentro de la lista de horarios.
    if not 0 <= indice < len(m.datos['horario']):
        return jsonify(
            error='Horario inexistente'
        ), 404

    m.datos['horario'].pop(indice)

    # Guardamos la lista de horarios actualizada.
    m.guardar()

    return jsonify(ok=True)


# CAMBIAR NOTA MINIMA

@app.post('/api/minima')
def minima():
    # Recibimos la nueva nota mínima desde el frontend.
    p = request.get_json(silent=True) or {}

    valor = p.get('minima')

    '''
     Validamos que:
        1. Sea un número entero o decimal.
        2. No sea un booleano.
        3. Esté dentro del rango de 0 a 100.
    '''
    if (
        type(valor) not in (int, float)
        or not 0 <= valor <= 100
    ):
        return jsonify(
            error='Nota mínima inválida'
        ), 400

    # Actualizamos la nota mínima en los datos del sistema.
    m.datos['minima'] = valor

    # Guardamos la nueva configuración.
    m.guardar()

    return jsonify(ok=True)


# OBTENER GRAFO DE MATERIAS

@app.get('/api/grafo')
def grafo():
    # Obtenemos la carrera seleccionada.
    plan = current()

    # Verificamos que exista un plan de estudio.
    if not plan:
        return jsonify(
            error='No hay planes cargados'
        ), 404

    #Construimos el grafo utilizando las materias de la carrera seleccionada. Cada materia representa un nodo y las relacciones de prerrequisitos representan las conexiones.
    g = crear_grafo(m.materias(plan))

    # Exportamos el grafo a un formato que pueda utilizar el frontend para representar visualmente las materias. También enviamos la lista de materias aprobadas para identificar cuáles ya fueron completadas.
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
    # Obtenemos la carrera seleccionada.
    plan = current()

    if not plan:
        return jsonify(
            error='No hay planes cargados'
        ), 404

    # Construimos el grafo con las materias de la carrera.
    g = crear_grafo(m.materias(plan))

    # Verificamos que el código recibido exista como nodo.
    if codigo.upper() not in g['nodos']:
        return jsonify(
            error='Materia no encontrada'
        ), 404

    '''
    Ejecutamos el recorrido BFS (Breadth-First Search).
        BFS recorre el grafo por niveles, comenzando desde la materia indicada y buscando las materias que dependen directa o indirectamente de ella.
    '''
    return jsonify(
        materias=dependientes_bfs(g, codigo)
    )


# RECORRIDO DFS
# CADENA DE PRERREQUISITOS

@app.get('/api/grafo/requisitos/<codigo>')
def cadena_requisitos(codigo):
    # Obtenemos la carrera seleccionada.
    plan = current()

    if not plan:
        return jsonify(
            error='No hay planes cargados'
        ), 404

    # Creamos el grado de materias y prerrequisitos.
    g = crear_grafo(m.materias(plan))

    # Comprobamos que el código exista en el grafo.
    if codigo.upper() not in g['nodos']:
        return jsonify(
            error='Materia no encontrada'
        ), 404

    try:
        '''
        Ejecutamos DFS (Depth-First Search).
            DFS explora una rama del grafo hasta llegar al final antes de regresar y explorar otra.
            En este caso permite obtener la cadena de prerrequisitos necesarios para cursar la materia.
        '''
        resultado = cadena_requisitos_dfs(
            g, codigo
        )

        # Devolvemos la cadena de materias encontrada.
        return jsonify(
            materias=resultado
        )

    # Capturamos errores de tipo VaueError que puedan producirse durante el recorrido del grafo.
    except ValueError as error:
        return jsonify(
            error=str(error)
        ), 422


# EJECUTAR SERVIDOR

# __name__ == "__main__" comprueba que este archivo se esté ejecutando directamente y no desde otro módulo.
if __name__ == '__main__':
    # Iniciamos el servidor Flask.
    app.run(
        debug=True,
        port=5000
    )