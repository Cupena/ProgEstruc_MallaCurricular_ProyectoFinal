"""Grafo dirigido dinámico de prerrequisitos, implementado SIN clases.

Cada materia es un vértice, y una arista A -> B indica que A
es requisito de B. Las listas de adyacencia crecen al añadir materias.
"""


def crear_grafo(cursos):
    grafo = {'adyacencia': {}, 'requisitos': {}, 'materias': {}}
    for materia in cursos:
        clave = str(materia.get('key') or '')
        if clave:
            agregar_materia(grafo, clave, materia)
    for materia in cursos:
        destino = str(materia.get('key') or '')
        if not destino:
            continue
        for requisito in materia.get('prereqs') or []:
            agregar_requisito(grafo, str(requisito), destino)
    return grafo


def agregar_materia(grafo, clave, datos=None):
    if clave not in grafo['adyacencia']:
        grafo['adyacencia'][clave] = []
        grafo['requisitos'][clave] = []
    if datos is not None:
        grafo['materias'][clave] = datos
    return grafo


def agregar_requisito(grafo, requisito, materia):
    if not requisito or not materia:
        return grafo
    agregar_materia(grafo, requisito)
    agregar_materia(grafo, materia)
    if materia not in grafo['adyacencia'][requisito]:
        grafo['adyacencia'][requisito].append(materia)
    if requisito not in grafo['requisitos'][materia]:
        grafo['requisitos'][materia].append(requisito)
    return grafo


def requisitos_pendientes(grafo, materia, aprobadas):
    return [r for r in grafo['requisitos'].get(materia, []) if r not in aprobadas]


def materias_disponibles(grafo, aprobadas):
    return [clave for clave in grafo['materias']
            if clave not in aprobadas and not requisitos_pendientes(grafo, clave, aprobadas)]


def dependientes_directas(grafo, materia):
    return list(grafo['adyacencia'].get(materia, []))


def ruta_requisitos(grafo, materia, visitados=None):
    """Devuelve prerrequisitos transitivos; evita ciclos mediante visitados."""
    if visitados is None:
        visitados = set()
    pendientes = []
    for requisito in grafo['requisitos'].get(materia, []):
        if requisito not in visitados:
            visitados.add(requisito)
            pendientes.append(requisito)
            pendientes.extend(ruta_requisitos(grafo, requisito, visitados))
    return pendientes


def dependientes_indirectas(grafo, materia):
    """Identifica todas las materias dependientes."""
    visitados = {materia}
    pendientes = list(grafo['adyacencia'].get(materia, []))
    resultado = []

    while pendientes:
        actual = pendientes.pop()

        if actual in visitados:
            continue

        visitados.add(actual)
        resultado.append(actual)

        pendientes.extend(
            grafo['adyacencia'].get(actual, [])
        )

    return resultado


def impacto_academico(grafo, materia):
    """Calcula el impacto de una materia sobre el plan."""
    directas = dependientes_directas(grafo, materia)
    dependientes = dependientes_indirectas(grafo, materia)

    return {
        'materia': materia,
        'directas': len(directas),
        'indirectas': len(set(dependientes) - set(directas)),
        'total': len(dependientes),
        'materias_afectadas': dependientes
    }


def detectar_ciclos(grafo):
    """Detecta dependencias circulares mediante DFS."""
    visitados = set()
    activos = set()

    def visitar(materia):
        if materia in activos:
            return True

        if materia in visitados:
            return False

        visitados.add(materia)
        activos.add(materia)

        for siguiente in grafo['adyacencia'].get(materia, []):
            if visitar(siguiente):
                return True

        activos.remove(materia)
        return False

    for materia in grafo['adyacencia']:
        if visitar(materia):
            return True

    return False


def validar_grafo(grafo):
    """Valida ciclos y referencias inexistentes."""
    errores = []

    for materia, requisitos in grafo['requisitos'].items():
        for requisito in requisitos:
            if requisito not in grafo['materias']:
                errores.append(
                    f'Requisito inexistente: {requisito} para {materia}'
                )

    if detectar_ciclos(grafo):
        errores.append('Se detectaron dependencias circulares')

    return {
        'valido': not errores,
        'errores': errores
    }


def orden_topologico(grafo):
    """Ordena las materias respetando sus prerrequisitos."""
    from cola_enlazada import crear_cola, encolar
    from cola_enlazada import desencolar, esta_vacia

    validacion = validar_grafo(grafo)

    if not validacion['valido']:
        raise ValueError('; '.join(validacion['errores']))

    grados = {
        materia: len(requisitos)
        for materia, requisitos in grafo['requisitos'].items()
    }

    cola = crear_cola()
    resultado = []

    for materia, grado in grados.items():
        if grado == 0:
            encolar(cola, materia)

    while not esta_vacia(cola):
        actual = desencolar(cola)
        resultado.append(actual)

        for siguiente in grafo['adyacencia'].get(actual, []):
            grados[siguiente] -= 1

            if grados[siguiente] == 0:
                encolar(cola, siguiente)

    if len(resultado) != len(grados):
        raise ValueError('El grafo contiene ciclos')

    return resultado
