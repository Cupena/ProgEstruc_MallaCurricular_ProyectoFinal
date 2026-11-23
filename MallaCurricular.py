#Creacion de repo

"""Ruta Académica: adaptación de consola en Python básico.
Coloca planes_ruta_academica.json en la misma carpeta que este archivo.
"""
import json
import os

CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_PLANES = os.path.join(CARPETA, 'planes_ruta_academica.json')
ARCHIVO_DATOS = os.path.join(CARPETA, 'mis_datos_academicos.json')


def leer_json(ruta, predeterminado):
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except (FileNotFoundError, ValueError):
        return predeterminado


def guardar():
    with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    print('Datos guardados.')