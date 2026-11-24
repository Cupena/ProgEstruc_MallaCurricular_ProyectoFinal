# Estructuras dinámicas de Ruta Académica

## Condiciones del proyecto

- **Sin clases definidas por el proyecto:** todo el Python se organiza mediante funciones, listas y diccionarios.
- **Sin dependencias externas** para ejecutar `servidor.py` (solo biblioteca estándar de Python).
- **Go Live** sirve `index.html` y `static/`; Python ofrece la API en `127.0.0.1:5000`.

## Estructura 1: grafo dirigido con listas de adyacencia

Módulo: `grafo_requisitos.py`.

- **Vértice:** materia identificada por `key`.
- **Arista A → B:** A es prerrequisito de B.
- **Representación:** diccionario `adyacencia` con listas que crecen dinámicamente, diccionario inverso `requisitos` y catálogo `materias`.
- Funciones: `crear_grafo`, `agregar_materia`, `agregar_requisito`, `requisitos_pendientes`, `materias_disponibles`, `dependientes_directas`, `ruta_requisitos`.
- **Uso real:** `academico.evaluar` construye el grafo para clasificar materias como aprobadas, disponibles o bloqueadas.

## Estructura 2: cola dinámica enlazada (FIFO)

Módulo: `cola_enlazada.py`.

- **Nodo:** diccionario con las claves `valor` y `siguiente`.
- **Cola:** diccionario con `primero`, `ultimo` y `longitud`.
- **Memoria dinámica:** cada `encolar` crea un nodo, `desencolar` lo retira.
- Funciones: `crear_cola`, `encolar`, `desencolar`, `esta_vacia`, `longitud`, `recorrido_bfs`, `ordenar_disponibles`.
- **Uso real:** `academico.evaluar` procesa las recomendaciones académicas mediante esta cola. El recorrido BFS del grafo también usa la cola para explorar materias dependientes por niveles.

## API opcional para demostrar las estructuras

`POST http://127.0.0.1:5000/api/grafo`

Ejemplo JSON:

```json
{
  "careers": [{"courses": [
    {"key": "MAT1", "name": "Matemática I", "prereqs": []},
    {"key": "MAT2", "name": "Matemática II", "prereqs": ["MAT1"]},
    {"key": "MAT3", "name": "Matemática III", "prereqs": ["MAT2"]}
  ]}],
  "career": 0,
  "key": "MAT1"
}
```

La respuesta devuelve los vértices, adyacencias, requisitos, la cadena de requisitos y los dependientes recorridos mediante BFS.

## Ejecución en Mac

Desde la carpeta del proyecto:

```bash
python3 servidor.py
```

Después abre `index.html` con la extensión **Go Live** de VS Code. No se necesita `pip install`.

> Nota: estas modificaciones incorporan las dos estructuras al backend; no representan una solución al problema visual de la pantalla de carga, que quedó fuera del alcance de este cambio.
