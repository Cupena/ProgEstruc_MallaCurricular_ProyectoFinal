# Ruta Académica — Go Live + Python sin clases

## Iniciar

1. En VS Code abre la carpeta `Ruta_Academica_Python`.
2. Terminal: `python3 servidor.py`.
3. Abre `index.html` con **Open with Live Server**.

No necesitas `pip install` para el servidor con Go Live.

## Módulos

- `index.html`, `static/js/`, `static/css/`: interfaz visual.
- `academico.py`: reglas, equivalencias, notas, estados y recomendaciones.
- `grafo_requisitos.py`: **grafo dirigido dinámico** con listas de adyacencia.
- `cola_enlazada.py`: **cola dinámica enlazada** y BFS.
- `servidor.py`: API HTTP estándar sin clases propias.
- `ESTRUCTURAS_DINAMICAS.md`: explicación académica de las dos estructuras.

Los scripts de interfaz todavía contienen lógica de UI en JavaScript. El trabajo actual agrega las dos estructuras dinámicas al backend Python sin reescribir toda la aplicación.
