"""Pruebas automatizadas sin dependencias externas."""

from pila_enlazada import (
    crear_pila, apilar, desapilar,
    cima, esta_vacia, longitud, vaciar_pila
)

from grafo_requisitos import (
    crear_grafo, detectar_ciclos,
    validar_grafo, orden_topologico,
    impacto_academico
)

from monticulo_prioridad import (
    crear_monticulo, insertar, extraer_maximo,
    consultar_maximo, validar_monticulo,
    priorizar_materias
)

from cola_enlazada import (
    crear_cola, encolar, desencolar
)

from academico import evaluar, nota
from faq import responder_faq, buscar_preguntas, responder_lote

from validaciones import (
    validar_nota, validar_creditos,
    validar_semestre, detectar_duplicados,
    diagnosticar_malla, diagnosticar_estado,
    validar_calificaciones
)


def datos_prueba():
    return [
        {
            'key': 'A', 'name': 'Matematica I',
            'credits': 4, 'semester': 1, 'prereqs': []
        },
        {
            'key': 'B', 'name': 'Matematica II',
            'credits': 4, 'semester': 2, 'prereqs': ['A']
        },
        {
            'key': 'C', 'name': 'Matematica III',
            'credits': 4, 'semester': 3, 'prereqs': ['B']
        },
        {
            'key': 'D', 'name': 'Programacion',
            'credits': 3, 'semester': 1, 'prereqs': []
        }
    ]


def estado_prueba():
    return {'careers': [{'courses': datos_prueba()}]}


def test_pila_vacia():
    assert esta_vacia(crear_pila())


def test_pila_lifo():
    pila = crear_pila()
    apilar(pila, 'A')
    apilar(pila, 'B')
    assert desapilar(pila) == 'B'
    assert desapilar(pila) == 'A'


def test_pila_cima():
    pila = crear_pila()
    apilar(pila, 10)
    assert cima(pila) == 10


def test_pila_longitud():
    pila = crear_pila()
    apilar(pila, 10)
    assert longitud(pila) == 1


def test_pila_vaciado():
    pila = crear_pila()
    apilar(pila, 10)
    vaciar_pila(pila)
    assert esta_vacia(pila)
    assert longitud(pila) == 0


def test_pila_error():
    try:
        desapilar(crear_pila())
    except IndexError:
        return
    raise AssertionError('Se esperaba IndexError')


def test_cola_fifo():
    cola = crear_cola()
    encolar(cola, 'A')
    encolar(cola, 'B')
    assert desencolar(cola) == 'A'
    assert desencolar(cola) == 'B'


def test_grafo_valido():
    assert validar_grafo(crear_grafo(datos_prueba()))['valido']


def test_grafo_ciclo():
    grafo = crear_grafo([
        {'key': 'A', 'prereqs': ['B']},
        {'key': 'B', 'prereqs': ['A']}
    ])
    assert detectar_ciclos(grafo)


def test_grafo_requisito_inexistente():
    grafo = crear_grafo([
        {'key': 'A', 'prereqs': ['X']}
    ])
    assert not validar_grafo(grafo)['valido']


def test_grafo_impacto():
    grafo = crear_grafo(datos_prueba())
    assert impacto_academico(grafo, 'A')['total'] == 2


def test_grafo_topologico():
    orden = orden_topologico(crear_grafo(datos_prueba()))
    assert orden.index('A') < orden.index('B') < orden.index('C')


def test_monticulo_maximo():
    monticulo = crear_monticulo()
    insertar(monticulo, 'A', 5)
    insertar(monticulo, 'B', 10)
    assert consultar_maximo(monticulo)['valor'] == 'B'


def test_monticulo_extraccion():
    monticulo = crear_monticulo()

    for valor in [3, 8, 1, 5]:
        insertar(monticulo, valor, valor)

    resultado = [
        extraer_maximo(monticulo)['valor']
        for _ in range(4)
    ]

    assert resultado == [8, 5, 3, 1]


def test_monticulo_validez():
    monticulo = crear_monticulo()

    for valor in [5, 10, 3, 15, 7]:
        insertar(monticulo, valor, valor)
        assert validar_monticulo(monticulo)


def test_prioridades():
    grafo = crear_grafo(datos_prueba())
    assert priorizar_materias(grafo, ['D', 'A']) == ['A', 'D']


def test_faq_avance():
    respuesta = responder_faq(estado_prueba(), 0, 'avance')
    assert respuesta['respuesta']['total'] == 4


def test_faq_creditos():
    respuesta = responder_faq(estado_prueba(), 0, 'creditos')
    assert respuesta['respuesta']['total'] == 15


def test_faq_pendientes():
    respuesta = responder_faq(estado_prueba(), 0, 'pendientes')
    assert respuesta['respuesta']['pendientes'] == 4


def test_faq_prioridad():
    respuesta = responder_faq(estado_prueba(), 0, 'prioridad')
    assert respuesta['respuesta'][0]['materia'] == 'A'


def test_faq_busqueda():
    assert buscar_preguntas('creditos')


def test_faq_lote_lifo():
    resultado = responder_lote(
        estado_prueba(), 0,
        [{'id': 'avance'}, {'id': 'creditos'}]
    )
    assert resultado[0]['id'] == 'creditos'
    assert resultado[1]['id'] == 'avance'


def test_notas_validas():
    assert validar_nota(0)
    assert validar_nota(70)
    assert validar_nota(100)


def test_notas_invalidas():
    assert not validar_nota(-1)
    assert not validar_nota(101)
    assert not validar_nota('texto')
    assert not validar_nota(float('nan'))


def test_creditos():
    assert validar_creditos(4)
    assert not validar_creditos(-3)


def test_semestres():
    assert validar_semestre(1)
    assert not validar_semestre(0)
    assert not validar_semestre(1.5)


def test_materias_duplicadas():
    materias = datos_prueba()
    materias.append(materias[0])
    assert detectar_duplicados(materias) == ['A']


def test_malla_valida():
    assert diagnosticar_malla(datos_prueba())['valido']


def test_malla_vacia():
    assert not diagnosticar_malla([])['valido']


def test_malla_creditos_invalidos():
    materias = datos_prueba()
    materias[0]['credits'] = -5
    assert not diagnosticar_malla(materias)['valido']


def test_calificaciones():
    assert not validar_calificaciones({'A': [70, 80, 90]})
    assert validar_calificaciones({'A': [70, 120, 90]})


def test_estado_valido():
    assert diagnosticar_estado(estado_prueba())['valido']


def test_estado_invalido():
    assert not diagnosticar_estado({})['valido']


def test_evaluacion_original():
    resultado = evaluar(estado_prueba())
    assert resultado['statuses']['0']['A'] == 'available'
    assert resultado['statuses']['0']['B'] == 'blocked'


def test_calculo_notas_original():
    resultado = nota([70, 80, 90])
    assert resultado['avg'] == 80
    assert resultado['status'] == 'passed'


def ejecutar_pruebas():
    pruebas = sorted(
        (nombre, funcion)
        for nombre, funcion in globals().items()
        if nombre.startswith('test_') and callable(funcion)
    )

    aprobadas = 0
    fallidas = 0

    for nombre, funcion in pruebas:
        try:
            funcion()
            aprobadas += 1
            print(f'[OK] {nombre}')

        except Exception as error:
            fallidas += 1
            print(f'[ERROR] {nombre}: {error!r}')

    print('-' * 50)
    print(f'Total: {len(pruebas)}')
    print(f'Aprobadas: {aprobadas}')
    print(f'Fallidas: {fallidas}')

    return fallidas == 0


if __name__ == '__main__':
    raise SystemExit(0 if ejecutar_pruebas() else 1)
