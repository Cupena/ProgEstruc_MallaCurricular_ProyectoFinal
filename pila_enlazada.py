
"""Pila dinamica enlazada LIFO mediante diccionarios.
Sin clases propias ni dependencias externas.
"""


def crear_pila():
    return {'cima': None, 'longitud': 0}


def apilar(pila, valor):
    nodo = {
        'valor': valor,
        'siguiente': pila['cima']
    }

    pila['cima'] = nodo
    pila['longitud'] += 1

    return pila


def desapilar(pila):
    if esta_vacia(pila):
        raise IndexError('La pila esta vacia')

    nodo = pila['cima']
    pila['cima'] = nodo['siguiente']
    pila['longitud'] -= 1

    return nodo['valor']


def cima(pila):
    if esta_vacia(pila):
        raise IndexError('La pila esta vacia')

    return pila['cima']['valor']


def esta_vacia(pila):
    return pila['cima'] is None


def longitud(pila):
    return pila['longitud']


def obtener_elementos(pila):
    elementos = []
    actual = pila['cima']

    while actual is not None:
        elementos.append(actual['valor'])
        actual = actual['siguiente']

    return elementos


def vaciar_pila(pila):
    pila['cima'] = None
    pila['longitud'] = 0

    return pila
