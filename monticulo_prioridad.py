"""Monticulo maximo dinamico para prioridades academicas.
Implementacion sin clases ni dependencias externas.
"""

from grafo_requisitos import impacto_academico


def crear_monticulo():
    return []


def intercambiar(monticulo, i, j):
    monticulo[i], monticulo[j] = monticulo[j], monticulo[i]


def subir(monticulo, indice):
    while indice > 0:
        padre = (indice - 1) // 2

        if monticulo[padre]['prioridad'] >= monticulo[indice]['prioridad']:
            break

        intercambiar(monticulo, padre, indice)
        indice = padre


def bajar(monticulo, indice):
    total = len(monticulo)

    while True:
        mayor = indice
        izquierdo = 2 * indice + 1
        derecho = 2 * indice + 2

        if izquierdo < total:
            if monticulo[izquierdo]['prioridad'] > monticulo[mayor]['prioridad']:
                mayor = izquierdo

        if derecho < total:
            if monticulo[derecho]['prioridad'] > monticulo[mayor]['prioridad']:
                mayor = derecho

        if mayor == indice:
            break

        intercambiar(monticulo, indice, mayor)
        indice = mayor


def insertar(monticulo, valor, prioridad):
    monticulo.append({
        'valor': valor,
        'prioridad': prioridad
    })

    subir(monticulo, len(monticulo) - 1)
    return monticulo


def extraer_maximo(monticulo):
    if not monticulo:
        raise IndexError('El monticulo esta vacio')

    maximo = monticulo[0]
    ultimo = monticulo.pop()

    if monticulo:
        monticulo[0] = ultimo
        bajar(monticulo, 0)

    return maximo


def consultar_maximo(monticulo):
    if not monticulo:
        raise IndexError('El monticulo esta vacio')

    return monticulo[0]


def esta_vacio(monticulo):
    return len(monticulo) == 0


def longitud(monticulo):
    return len(monticulo)


def validar_monticulo(monticulo):
    for indice in range(1, len(monticulo)):
        padre = (indice - 1) // 2

        if monticulo[indice]['prioridad'] > monticulo[padre]['prioridad']:
            return False

    return True


def priorizar_materias(grafo, disponibles):
    monticulo = crear_monticulo()
    resultado = []

    for orden, materia in enumerate(disponibles):
        impacto = impacto_academico(grafo, materia)

        insertar(
            monticulo,
            materia,
            (impacto['total'], -orden)
        )

    while not esta_vacio(monticulo):
        elemento = extraer_maximo(monticulo)
        resultado.append(elemento['valor'])

    return resultado
