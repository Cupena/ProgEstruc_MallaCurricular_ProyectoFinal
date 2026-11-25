"""Validaciones y diagnostico del estado academico."""

import math
from grafo_requisitos import crear_grafo, validar_grafo


def numero_valido(valor, minimo, maximo=None):
    if isinstance(valor, bool):
        return False

    try:
        numero = float(valor)

        if not math.isfinite(numero):
            return False

        if numero < minimo:
            return False

        if maximo is not None and numero > maximo:
            return False

        return True

    except (ValueError, TypeError, OverflowError):
        return False


def validar_nota(nota):
    return numero_valido(nota, 0, 100)


def validar_creditos(creditos):
    return numero_valido(creditos, 0)


def validar_semestre(semestre):
    if not numero_valido(semestre, 1):
        return False

    return float(semestre).is_integer()


def detectar_duplicados(materias):
    encontrados = set()
    duplicados = set()

    for materia in materias:
        if not isinstance(materia, dict):
            continue

        clave = materia.get('key')

        if not isinstance(clave, str) or not clave:
            continue

        if clave in encontrados:
            duplicados.add(clave)

        encontrados.add(clave)

    return sorted(duplicados)


def validar_materia(materia):
    errores = []

    if not isinstance(materia, dict):
        return ['La materia debe ser un diccionario']

    clave = materia.get('key')

    if not isinstance(clave, str) or not clave.strip():
        errores.append('Codigo de materia invalido')

    if not isinstance(materia.get('name'), str):
        errores.append('Nombre de materia invalido')

    if not validar_creditos(materia.get('credits')):
        errores.append('Cantidad de creditos invalida')

    if not validar_semestre(materia.get('semester')):
        errores.append('Semestre invalido')

    requisitos = materia.get('prereqs', [])

    if not isinstance(requisitos, list):
        errores.append('Los requisitos deben ser una lista')
    elif any(not isinstance(r, str) or not r for r in requisitos):
        errores.append('Prerrequisito invalido')
    elif clave in requisitos:
        errores.append('La materia es requisito de si misma')

    return errores


def diagnosticar_malla(materias):
    errores = []

    if not isinstance(materias, list):
        return {
            'valido': False,
            'errores': ['Se requiere una lista de materias'],
            'total': 0
        }

    if not materias:
        errores.append('No hay materias cargadas')

    for indice, materia in enumerate(materias):
        for error in validar_materia(materia):
            errores.append(f'Materia {indice + 1}: {error}')

    for clave in detectar_duplicados(materias):
        errores.append(f'Materia duplicada: {clave}')

    if not errores:
        grafo = crear_grafo(materias)
        errores.extend(validar_grafo(grafo)['errores'])

    return {
        'valido': not errores,
        'errores': errores,
        'total': len(materias)
    }


def validar_calificaciones(calificaciones):
    errores = []

    if not isinstance(calificaciones, dict):
        return ['Registro de calificaciones invalido']

    for materia, parciales in calificaciones.items():
        if not isinstance(parciales, list):
            errores.append(f'{materia}: formato invalido')
            continue

        if len(parciales) > 3:
            errores.append(f'{materia}: exceso de parciales')

        for indice, nota in enumerate(parciales):
            if nota is not None and nota != '':
                if not validar_nota(nota):
                    errores.append(
                        f'{materia}: parcial {indice + 1} invalido'
                    )

    return errores


def diagnosticar_estado(estado):
    if not isinstance(estado, dict):
        return {
            'valido': False,
            'errores': ['Estado academico invalido'],
            'carreras': []
        }

    errores = []
    resultados = []

    carreras = estado.get('careers', [])
    registros = estado.get('careerRecords', [])

    if not isinstance(carreras, list):
        return {
            'valido': False,
            'errores': ['Formato de carreras invalido'],
            'carreras': []
        }

    if not isinstance(registros, list):
        errores.append('Formato de registros invalido')
        registros = []

    if not any(c is not None for c in carreras):
        errores.append('No hay carreras cargadas')

    for indice, carrera in enumerate(carreras):
        if carrera is None:
            continue

        if not isinstance(carrera, dict):
            errores.append(f'Carrera {indice + 1}: formato invalido')
            continue

        resultado = diagnosticar_malla(
            carrera.get('courses', [])
        )

        if indice < len(registros):
            registro = registros[indice]

            if isinstance(registro, dict):
                resultado['errores'].extend(
                    validar_calificaciones(
                        registro.get('grades', {})
                    )
                )

        resultado['valido'] = not resultado['errores']
        resultado['carrera'] = indice

        resultados.append(resultado)

        errores.extend(
            f'Carrera {indice + 1}: {error}'
            for error in resultado['errores']
        )

    return {
        'valido': not errores,
        'errores': errores,
        'carreras': resultados
    }
