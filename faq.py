"""Sistema dinamico de preguntas frecuentes academicas."""

from academico import evaluar, cursos, registros, normalizar_nombre
from grafo_requisitos import crear_grafo, impacto_academico
from grafo_requisitos import requisitos_pendientes, validar_grafo
from grafo_requisitos import orden_topologico
from monticulo_prioridad import priorizar_materias
from pila_enlazada import crear_pila, apilar, desapilar, esta_vacia


PREGUNTAS = {
    'avance': 'Cual es mi avance academico?',
    'pendientes': 'Cuantas materias me faltan?',
    'creditos': 'Cuantos creditos tengo aprobados?',
    'disponibles': 'Que materias puedo matricular?',
    'bloqueadas': 'Que materias tengo bloqueadas?',
    'requisitos': 'Que requisitos me faltan?',
    'prioridad': 'Que materias deberia priorizar?',
    'impacto': 'Que materias dependen de esta asignatura?',
    'notas': 'Que nota necesito para aprobar?',
    'validacion': 'Mi malla tiene errores?',
    'ruta': 'Cual es el orden de mis materias?'
}


def listar_preguntas():
    return [
        {'id': clave, 'pregunta': pregunta}
        for clave, pregunta in PREGUNTAS.items()
    ]


def buscar_preguntas(consulta):
    palabras = normalizar_nombre(consulta).split()

    return [
        item for item in listar_preguntas()
        if all(
            palabra in normalizar_nombre(
                item['pregunta'] + ' ' + item['id']
            )
            for palabra in palabras
        )
    ]


def crear_contexto(estado, carrera):
    if carrera not in (0, 1):
        raise ValueError('Carrera invalida')

    materias = cursos(estado, carrera)
    evaluacion = evaluar(estado)
    clave = str(carrera)

    return {
        'materias': materias,
        'grafo': crear_grafo(materias),
        'estados': evaluacion['statuses'].get(clave, {}),
        'estadisticas': evaluacion['statistics'].get(clave, {}),
        'notas': evaluacion['grades'].get(clave, {})
    }


def buscar_materia(contexto, clave):
    for materia in contexto['materias']:
        if materia.get('key') == clave:
            return materia

    raise ValueError('Materia no encontrada')


def materias_por_estado(contexto, estado):
    return [
        {
            'key': materia.get('key'),
            'name': materia.get('name', materia.get('key'))
        }
        for materia in contexto['materias']
        if contexto['estados'].get(materia.get('key')) == estado
    ]


def responder_avance(contexto):
    datos = contexto['estadisticas']

    return {
        'porcentaje': round(datos.get('pct', 0) * 100, 2),
        'aprobadas': datos.get('taken', 0),
        'total': datos.get('total', 0)
    }


def responder_pendientes(contexto):
    datos = contexto['estadisticas']

    return {
        'pendientes': datos.get('total', 0) - datos.get('taken', 0),
        'disponibles': datos.get('available', 0),
        'bloqueadas': datos.get('blocked', 0)
    }


def responder_creditos(contexto):
    datos = contexto['estadisticas']
    total = datos.get('credits', 0)
    aprobados = datos.get('creditsTaken', 0)

    return {
        'total': total,
        'aprobados': aprobados,
        'pendientes': total - aprobados
    }


def responder_requisitos(contexto, materia):
    buscar_materia(contexto, materia)

    aprobadas = {
        clave for clave, estado in contexto['estados'].items()
        if estado == 'taken'
    }

    return {
        'materia': materia,
        'pendientes': requisitos_pendientes(
            contexto['grafo'], materia, aprobadas
        )
    }


def responder_prioridad(contexto):
    disponibles = materias_por_estado(contexto, 'available')
    claves = [materia['key'] for materia in disponibles]

    orden = priorizar_materias(contexto['grafo'], claves)

    return [
        {
            'materia': clave,
            'impacto': impacto_academico(
                contexto['grafo'], clave
            )['total']
        }
        for clave in orden
    ]


def responder_notas(contexto, materia):
    buscar_materia(contexto, materia)

    return contexto['notas'].get(materia, {
        'status': 'none',
        'mensaje': 'No hay calificaciones registradas'
    })


def responder_faq(estado, carrera, pregunta, materia=None):
    if pregunta not in PREGUNTAS:
        raise ValueError('Pregunta no reconocida')

    contexto = crear_contexto(estado, carrera)

    respuestas = {
        'avance': lambda: responder_avance(contexto),
        'pendientes': lambda: responder_pendientes(contexto),
        'creditos': lambda: responder_creditos(contexto),
        'disponibles': lambda: materias_por_estado(
            contexto, 'available'
        ),
        'bloqueadas': lambda: materias_por_estado(
            contexto, 'blocked'
        ),
        'requisitos': lambda: responder_requisitos(
            contexto, materia
        ),
        'prioridad': lambda: responder_prioridad(contexto),
        'impacto': lambda: impacto_academico(
            contexto['grafo'],
            buscar_materia(contexto, materia)['key']
        ),
        'notas': lambda: responder_notas(contexto, materia),
        'validacion': lambda: validar_grafo(contexto['grafo']),
        'ruta': lambda: orden_topologico(contexto['grafo'])
    }

    return {
        'id': pregunta,
        'pregunta': PREGUNTAS[pregunta],
        'respuesta': respuestas[pregunta]()
    }


def responder_lote(estado, carrera, preguntas):
    """Procesa consultas mediante una pila LIFO."""
    pila = crear_pila()
    resultados = []

    for pregunta in preguntas:
        apilar(pila, pregunta)

    while not esta_vacia(pila):
        consulta = desapilar(pila)

        resultados.append(
            responder_faq(
                estado,
                carrera,
                consulta['id'],
                consulta.get('materia')
            )
        )

    return resultados
