# Ruta Académica — Go Live corregido

## Uso en VS Code en macOS

1. Extrae este ZIP completo (no abras el HTML desde el ZIP).
2. En VS Code, **Archivo > Abrir carpeta...**, elige `Ruta_Academica_GoLive_CORREGIDA`.
3. Abre una terminal EN ESA CARPETA, escribe `python3 servidor.py` y mantenla abierta.
4. Pulsa **Go Live** abajo a la derecha. Entra a `http://127.0.0.1:5500/index.html`.
5. Si Safari conserva la versión anterior: Safari > Ajustes > Privacidad > Gestionar datos de sitios web, busca `localhost` / `127.0.0.1` y elimina esos datos; o usa una ventana privada.

NO se requiere instalar requirements. La interfaz usa `assets/estilos.css` y `assets/app.js` (rutas relativas); los originales separados se mantienen en `static/js` y `static/css`. Si modificas esos archivos, vuelve a combinar los archivos para reflejar cambios en `assets`.

La lógica académica se encuentra en `academico.py`, `grafo_requisitos.py`, `cola_enlazada.py`. No se definen clases propias. El navegador se comunica con el backend en el puerto 5000.

Si sale una ventana de diagnóstico con archivo no encontrado, comprueba que abriste la carpeta completa en VS Code y que Live Server muestra el puerto 5500.
