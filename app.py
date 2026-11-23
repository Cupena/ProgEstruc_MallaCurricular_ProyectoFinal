
from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

CARPETA = os.path.dirname(os.path.abspath(__file__))
CARPETA_PLANES = os.path.join(CARPETA, "planes_estudio")


def cargar_planes():
    planes = []

    if not os.path.exists(CARPETA_PLANES):
        print("ERROR: No existe la carpeta planes_estudio")
        return planes

    for archivo in sorted(os.listdir(CARPETA_PLANES)):

        if archivo.endswith(".json"):
            ruta = os.path.join(CARPETA_PLANES, archivo)

            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = json.load(f)

                if isinstance(contenido, list):
                    planes.extend(contenido)

                elif isinstance(contenido, dict):
                    planes.append(contenido)

                print("Archivo cargado:", archivo)

            except (OSError, ValueError) as error:
                print("Error leyendo", archivo, error)

    return planes


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/planes")
def obtener_planes():
    planes = cargar_planes()
    return jsonify(planes)


@app.route("/api/materias/<int:carrera>")
def obtener_materias(carrera):
    planes = cargar_planes()

    if carrera >= len(planes):
        return jsonify({"error": "Carrera no encontrada"}), 404

    materias = []

    for numero, semestre in enumerate(
        planes[carrera]["semestres"], 1
    ):
        for materia in semestre:
            item = materia.copy()
            item["semestre"] = numero
            materias.append(item)

    return jsonify(materias)


if __name__ == "__main__":
    app.run(debug=True)
