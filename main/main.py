import time
import logging
from flask import Flask
from .models import Shot, Variables

numAtletas = 4
HOST = "127.0.0.1"
PORT = 8080
FICHERO = "resultados.log"

tiempoIni = 0
tiempoFin = 0
atletas = {}
pistoletazo = Shot()
finCarrera = Shot()
variables = Variables()

logger = logging.getLogger(__name__)
api = Flask(__name__)


@api.route("/reinicio")
def reinicio():
    global tiempoIni
    global atletas
    variables.reiniciar()
    tiempoIni = 0
    atletas = {}
    return "Variables reiniciadas."


@api.route("/preparado")
def preparado():
    numPreparados = variables.actualizar("preparados")
    if numPreparados < numAtletas:
        pistoletazo.wait()
    else:
        pistoletazo.notify()
    return "Preparado..."


@api.route("/listo")
def listo():
    global tiempoIni
    numListos = variables.actualizar("listos")
    if numListos < numAtletas:
        pistoletazo.wait()
    else:
        pistoletazo.notify()
        tiempoIni = time.time()
    return "Listo..."


@api.route("/llegada/<int:dorsal>")
def llegada(dorsal: int):
    atletas[dorsal] = time.time() - tiempoIni
    numFinalizados = variables.actualizar("finalizados")
    return str(str(atletas[dorsal]) + " segundos")


@api.route("/resultados")
def resultados():
    message = ""
    for key, value in atletas.items():
        message = str(message) + "Atleta " + str(key) + ": " + str(value) + " segundos.\n"
    return message


def start():
    api.run(host=HOST, port=PORT)
