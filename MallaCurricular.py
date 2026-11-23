
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


def materias(carrera):
    resultado = []
    for numero, semestre in enumerate(planes[carrera]['semestres'], 1):
        for materia in semestre:
            item = materia.copy()
            item['semestre'] = numero
            resultado.append(item)
    return resultado


def buscar(codigo, carrera):
    for materia in materias(carrera):
        if materia['codigo'].upper() == codigo.upper():
            return materia
    return None


def aprobada(codigo):
    return codigo.upper() in datos['aprobadas']


def requisitos(materia):
    texto = materia['requisitos'].strip()
    return [x.strip() for x in texto.split(',') if x.strip()]


def pendientes(materia):
    return [codigo for codigo in requisitos(materia) if not aprobada(codigo)]


def estado(materia):
    if aprobada(materia['codigo']):
        return 'APROBADA'
    if pendientes(materia):
        return 'BLOQUEADA'
    return 'DISPONIBLE'


def elegir_carrera():
    print('\nCARRERAS')
    for i, plan in enumerate(planes, 1):
        print(i, '-', plan['nombre'])
    try:
        numero = int(input('Selecciona una carrera: ')) - 1
        if 0 <= numero < len(planes):
            datos['carrera'] = numero
            guardar()
    except ValueError:
        print('Debes escribir un número.')


def mostrar_malla():
    carrera = datos['carrera']
    for numero, semestre in enumerate(planes[carrera]['semestres'], 1):
        print('\n--- SEMESTRE', numero, '---')
        for m in semestre:
            print(m['codigo'], '-', m['nombre'], '|', estado(m))


def detalle():
    codigo = input('Código de la materia: ').strip().upper()
    m = buscar(codigo, datos['carrera'])
    if not m:
        print('No se encontró esa materia en la carrera seleccionada.')
        return
    print('\nMateria:', m['nombre'])
    print('Código:', m['codigo'])
    print('Semestre:', m['semestre'])
    print('Créditos:', m['creditos'])
    print('Estado:', estado(m))
    if requisitos(m):
        print('Prerrequisitos:')
        for req in requisitos(m):
            original = buscar(req, datos['carrera'])
            nombre = original['nombre'] if original else req
            print(' -', nombre, ':', 'Aprobado' if aprobada(req) else 'Pendiente')
    else:
        print('Sin prerrequisitos.')
    if codigo in datos['notas']:
        print('Notas:', datos['notas'][codigo])


def marcar_aprobada():
    codigo = input('Código de la materia: ').strip().upper()
    m = buscar(codigo, datos['carrera'])
    if not m:
        print('No se encontró esa materia.')
        return
    if aprobada(codigo):
        print('La materia ya está aprobada.')
        return
    if pendientes(m):
        print('No puedes aprobarla todavía. Faltan:', ', '.join(pendientes(m)))
        return
    datos['aprobadas'].append(codigo)
    guardar()


def registrar_notas():
    codigo = input('Código de la materia: ').strip().upper()
    m = buscar(codigo, datos['carrera'])
    if not m:
        print('Materia no encontrada.')
        return
    print('Introduce las tres notas parciales, entre 0 y 100.')
    notas = []
    for numero in range(1, 4):
        while True:
            try:
                valor = float(input('Parcial ' + str(numero) + ': '))
                if 0 <= valor <= 100:
                    notas.append(valor)
                    break
                print('La nota debe estar entre 0 y 100.')
            except ValueError:
                print('Escribe un número válido.')
    promedio = round(sum(notas) / 3, 2)
    datos['notas'][codigo] = {'parciales': notas, 'promedio': promedio}
    print('Promedio:', promedio)
    if promedio >= datos['minima']:
        print('Resultado: APROBADA')
        if codigo not in datos['aprobadas']:
            datos['aprobadas'].append(codigo)
    else:
        print('Resultado: NO APROBADA')
        if codigo in datos['aprobadas']:
            datos['aprobadas'].remove(codigo)
    guardar()


def progreso():
    lista = materias(datos['carrera'])
    total = len(lista)
    terminadas = sum(1 for m in lista if aprobada(m['codigo']))
    creditos = sum(int(m['creditos']) for m in lista)
    completados = sum(int(m['creditos']) for m in lista if aprobada(m['codigo']))
    print('\nCarrera:', planes[datos['carrera']]['nombre'])
    print('Materias aprobadas:', terminadas, 'de', total)
    print('Materias restantes:', total - terminadas)
    print('Progreso:', round(100 * terminadas / total, 1) if total else 0, '%')
    print('Créditos completados:', completados, 'de', creditos)
    print('Materias bloqueadas:', sum(estado(m) == 'BLOQUEADA' for m in lista))


def recomendar():
    print('\nMATERIAS DISPONIBLES PARA CURSAR')
    disponibles = [m for m in materias(datos['carrera']) if estado(m) == 'DISPONIBLE']
    disponibles.sort(key=lambda m: m['semestre'])
    if not disponibles:
        print('No hay materias disponibles.')
    for m in disponibles:
        print(m['codigo'], '-', m['nombre'], '| Semestre', m['semestre'], '|', m['creditos'], 'créditos')
    print('Estas son materias elegibles por prerrequisitos, no una matrícula automática.')


def horario():
    while True:
        print('\nHORARIO: 1. Ver  2. Agregar  3. Eliminar  0. Volver')
        op = input('Opción: ')
        if op == '0':
            break
        if op == '1':
            for i, clase in enumerate(datos['horario'], 1):
                print(i, '-', clase['materia'], clase['dia'], clase['hora'], clase['aula'])
        elif op == '2':
            codigo = input('Código de materia: ').upper().strip()
            if not buscar(codigo, datos['carrera']):
                print('Materia no encontrada.')
                continue
            dia = input('Día: ')
            hora = input('Hora (ejemplo 08:00-10:00): ')
            aula = input('Aula: ')
            datos['horario'].append({'materia': codigo, 'dia': dia, 'hora': hora, 'aula': aula})
            guardar()
        elif op == '3':
            try:
                numero = int(input('Número de entrada a eliminar: ')) - 1
                datos['horario'].pop(numero)
                guardar()
            except (ValueError, IndexError):
                print('Número incorrecto.')


def cambiar_minima():
    try:
        valor = float(input('Nota mínima de aprobación (0 a 100): '))
        if 0 <= valor <= 100:
            datos['minima'] = valor
            guardar()
        else:
            print('Valor fuera de rango.')
    except ValueError:
        print('Número incorrecto.')


planes = leer_json(ARCHIVO_PLANES, [])
datos = leer_json(ARCHIVO_DATOS, {'carrera': 0, 'aprobadas': [], 'notas': {}, 'horario': [], 'minima': 60})
for clave, valor in {'carrera': 0, 'aprobadas': [], 'notas': {}, 'horario': [], 'minima': 60}.items():
    if clave not in datos:
        datos[clave] = valor


def main():
    if not planes:
        print('Falta el archivo planes_ruta_academica.json en la misma carpeta.')
        return
    if not isinstance(datos['carrera'], int) or datos['carrera'] >= len(planes):
        datos['carrera'] = 0
    while True:
        print('\n========== RUTA ACADÉMICA ==========')
        print('Carrera:', planes[datos['carrera']]['nombre'])
        print('1. Cambiar carrera')
        print('2. Ver malla curricular')
        print('3. Consultar materia y requisitos')
        print('4. Marcar materia aprobada')
        print('5. Registrar tres notas parciales')
        print('6. Ver progreso académico')
        print('7. Recomendar materias disponibles')
        print('8. Administrar horario')
        print('9. Cambiar nota mínima')
        print('0. Salir')
        opcion = input('Selecciona una opción: ')
        if opcion == '1': elegir_carrera()
        elif opcion == '2': mostrar_malla()
        elif opcion == '3': detalle()
        elif opcion == '4': marcar_aprobada()
        elif opcion == '5': registrar_notas()
        elif opcion == '6': progreso()
        elif opcion == '7': recomendar()
        elif opcion == '8': horario()
        elif opcion == '9': cambiar_minima()
        elif opcion == '0':
            guardar()
            print('Hasta luego.')
            break
        else:
            print('Opción no válida.')


if __name__ == '__main__':
    main()
