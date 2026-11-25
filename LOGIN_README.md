# Ruta Académica: inicio de sesión UAM

## Para reemplazar el proyecto

1. Cierra Live Server si está activo.
2. Descomprime este ZIP y abre la carpeta **Ruta_Academica_Login_UAM_Lista** completa en VS Code.
3. Ejecuta `python3 servidor.py` desde esa carpeta. No necesita `pip install`.
4. Abre `login.html` con **Open with Live Server**. Utiliza `http://127.0.0.1:5500/login.html`.
5. Elige **Crear cuenta** para dar de alta un usuario institucional @uamv.edu.ni. Luego podrás ingresar.

El proyecto no crea una cuenta de administrador con una clave conocida. Las contraseñas se almacenan con PBKDF2-HMAC SHA-256 y sal única. Se mantiene el grafo de prerrequisitos y la cola enlazada, sin clases propias.

**Nota:** `¿Olvidaste tu contraseña?` muestra un aviso; no envía correos, ya que este proyecto local no tiene servicio de recuperación configurado.

**Datos:** si estás reemplazando una versión previa y deseas conservar tus cuentas creadas, haz una copia de `ruta_academica.sqlite3` de la versión anterior y colócala en la nueva carpeta con el servidor apagado. La nueva configuración exige el dominio institucional a los usuarios nuevos.


## Corrección Go Live
Los estilos y la ilustración del login están integrados en `login.html` para que se muestre correctamente aunque Live Server no encuentre recursos CSS. `auth/login.js` sigue siendo el módulo JavaScript independiente; `servidor.py` y `autenticacion.py` siguen gestionando la lógica de backend. Abre la carpeta COMPLETA en VS Code antes de usar Live Server.
