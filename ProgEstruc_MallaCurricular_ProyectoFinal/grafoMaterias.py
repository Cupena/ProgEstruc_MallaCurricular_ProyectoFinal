"""Grafo dirigido con diccionarios y funciones; sin clases."""
from collections import deque


def crear_grafo(materias):
    nodos = {}
    for materia in materias:
        codigo = str(materia['codigo']).strip().upper()
        if codigo in nodos:
            raise ValueError('Código duplicado: ' + codigo)
        nodos[codigo] = {
            'codigo': codigo, 'nombre': materia.get('nombre', codigo),
            'semestre': materia.get('semestre', 0),
            'creditos': materia.get('creditos', 0),
            'requisitos': [], 'siguientes': []
        }
    externos = {}
    for materia in materias:
        codigo = str(materia['codigo']).strip().upper()
        texto = str(materia.get('requisitos') or '')
        requisitos = [x.strip().upper() for x in texto.split(',') if x.strip()]
        nodos[codigo]['requisitos'] = requisitos
        for req in requisitos:
            if req in nodos:
                nodos[req]['siguientes'].append(codigo)
            else:
                externos.setdefault(codigo, []).append(req)
    return {'nodos': nodos, 'requisitos_externos': externos}


def pendientes_grafo(grafo, codigo, aprobadas):
    codigo = codigo.strip().upper()
    aprobadas = {str(c).upper() for c in aprobadas}
    return [r for r in grafo['nodos'][codigo]['requisitos'] if r not in aprobadas]


def disponibles_grafo(grafo, aprobadas):
    aprobadas = {str(c).upper() for c in aprobadas}
    return [n for codigo, n in grafo['nodos'].items()
            if codigo not in aprobadas and not pendientes_grafo(grafo, codigo, aprobadas)]


def dependientes_bfs(grafo, codigo):
    codigo = codigo.strip().upper()
    if codigo not in grafo['nodos']:
        return []
    cola = deque(grafo['nodos'][codigo]['siguientes'])
    visitados = {codigo}
    resultado = []
    while cola:
        actual = cola.popleft()
        if actual in visitados:
            continue
        visitados.add(actual)
        resultado.append(actual)
        cola.extend(grafo['nodos'][actual]['siguientes'])
    return resultado


def cadena_requisitos_dfs(grafo, codigo):
    codigo = codigo.strip().upper()
    if codigo not in grafo['nodos']:
        return []
    visitados, activos, resultado = set(), set(), []

    def visitar(actual):
        if actual in activos:
            raise ValueError('Ciclo de prerrequisitos detectado en ' + actual)
        if actual in visitados or actual not in grafo['nodos']:
            return
        activos.add(actual)
        for requisito in grafo['nodos'][actual]['requisitos']:
            visitar(requisito)
        activos.remove(actual)
        visitados.add(actual)
        resultado.append(actual)

    visitar(codigo)
    return resultado


def exportar_grafo(grafo, aprobadas):
    aprobadas = {str(c).upper() for c in aprobadas}
    nodos = grafo['nodos']
    return {
        'nodos': [
            {'codigo': n['codigo'], 'nombre': n['nombre'],
             'semestre': n['semestre'],
             'estado': 'APROBADA' if n['codigo'] in aprobadas else
             ('BLOQUEADA' if pendientes_grafo(grafo, n['codigo'], aprobadas) else 'DISPONIBLE')}
            for n in nodos.values()
        ],
        'aristas': [{'origen': r, 'destino': n['codigo']}
                    for n in nodos.values() for r in n['requisitos'] if r in nodos],
        'requisitos_externos': grafo['requisitos_externos']
    }
