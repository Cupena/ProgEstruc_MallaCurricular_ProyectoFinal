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

## Estructuras adicionales

### Pila dinamica enlazada (LIFO)

Modulo: pila_enlazada.py.

- Nodos enlazados mediante diccionarios.
- Insercion y extraccion en la cima.
- Operaciones principales O(1).
- Recorrido completo O(n).
- Aplicacion: procesamiento inverso de consultas FAQ.

### Ampliacion del grafo dirigido

Modulo: grafo_requisitos.py.

- Deteccion de ciclos mediante DFS.
- Analisis de dependencias transitivas.
- Calculo del impacto academico.
- Validacion de requisitos inexistentes.
- Ordenamiento topologico mediante cola FIFO.
- Recorridos del grafo: O(V + E).

### Monticulo maximo

Modulo: monticulo_prioridad.py.

- Representacion mediante una lista dinamica.
- Insercion O(log n) amortizada.
- Extraccion maxima O(log n).
- Consulta maxima O(1).
- Priorizacion basada en dependencias academicas.
- El calculo de impacto requiere recorrer el grafo.

### FAQ academico

Modulo: faq.py.

- Catalogo de preguntas frecuentes.
- Busqueda normalizada.
- Respuestas generadas con datos academicos.
- Integracion de pila, grafo, cola y monticulo.

API:

- GET /api/faq
- POST /api/faq

### Validaciones y diagnostico

Modulo: validaciones.py.

- Validacion de notas entre 0 y 100.
- Validacion de creditos y semestres.
- Deteccion de materias duplicadas.
- Revision de prerrequisitos.
- Diagnostico del estado academico.

API:

- GET /api/diagnostico

El diagnostico es de consulta y no modifica la base de datos.

### Pruebas automatizadas

Ejecutar desde la carpeta principal:

    py -B -m tests.test_estructuras

Las pruebas utilizan datos ficticios y no modifican la base
de datos ni los registros academicos del estudiante.

No se requieren dependencias externas.
