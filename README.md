# Ruta Académica — Go Live sin dependencias de archivos visuales

1. Descomprime el ZIP y abre la carpeta `Ruta_Academica_GoLive_AUTOCONTENIDA` completa en VS Code.
2. En una terminal ejecuta `python3 servidor.py` (biblioteca estándar, sin pip).
3. Abre `index.html` con la extensión Live Server / Go Live.
4. En el navegador abre la dirección que ofrece Go Live.

**Importante:** `index.html` incluye internamente todo el CSS y JavaScript de la aplicación. El backend Python permanece independiente y debe seguir ejecutándose para sus funciones. La malla mantiene el desplazamiento horizontal por CSS.

Si aparece una versión vieja, usa la recarga sin caché o una ventana privada. El servidor en el puerto 5000 responde a `/api/salud`.
