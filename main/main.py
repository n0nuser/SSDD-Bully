import time
import logging
from flask import Flask
from .models import Proceso
from aux_functions import generate_node_id

numProcesos = 4
HOST = "127.0.0.1"
PORT = 8080
FICHERO = "resultados.log"

misProcesos = {}
idsDireccion = {}  # {id: direccion} -> {150: "192.168.1.15"}
flagComputar = False
buzonComputar = False
buzonResponder = False

tiempoIni = 0
tiempoFin = 0
atletas = {}
pistoletazo = Shot()
finCarrera = Shot()
variables = Variables()

logger = logging.getLogger(__name__)
servicio = Flask(__name__)


# @servicio.route("/reinicio")
# def reinicio():
#     global tiempoIni
#     global atletas
#     variables.reiniciar()
#     tiempoIni = 0
#     atletas = {}
#     return "Variables reiniciadas."


# @servicio.route("/preparado")
# def preparado():
#     numPreparados = variables.actualizar("preparados")
#     if numPreparados < numProcesos:
#         pistoletazo.wait()
#     else:
#         pistoletazo.notify()
#     return "Preparado..."


# @servicio.route("/listo")
# def listo():
#     global tiempoIni
#     numListos = variables.actualizar("listos")
#     if numListos < numProcesos:
#         pistoletazo.wait()
#     else:
#         pistoletazo.notify()
#         tiempoIni = time.time()
#     return "Listo..."


# @servicio.route("/llegada/<int:dorsal>")
# def llegada(dorsal: int):
#     atletas[dorsal] = time.time() - tiempoIni
#     numFinalizados = variables.actualizar("finalizados")
#     return str(str(atletas[dorsal]) + " segundos")


# @servicio.route("/resultados")
# def resultados():
#     message = ""
#     for key, value in atletas.items():
#         message = (
#             str(message) + "Atleta " + str(key) + ": " + str(value) + " segundos.\n"
#         )
#     return message


@servicio.route("/servicio/ok?id=<int:id>")
def ok(id: int):
    print("")


@servicio.route("/servicio/eleccion?id=<int:id>")
def eleccion(id: int):
    print("")


@servicio.route("/servicio/coordinador?id=<int:id>")
def coordinador(id: int):
    print("")


@servicio.route("/servicio/arrancar?id=<int:id>")
def arrancar(id: int):
    print("")


@servicio.route("/servicio/parar?id=<int:id>")
def parar(id: int):
    print("")


@servicio.route("/servicio/computar?id=<int:id>")
def computar(id: int):
    global flagComputar
    flagComputar = True
    while not buzonResponder:
        pass
    if buzonComputar:
        buzonComputar = False
        buzonResponder = False
        return 200
    else:
        buzonComputar = False
        buzonResponder = False
        return 400


def start():
    global misProcesos
    for i in range(numProcesos):
        id = generate_node_id()
        proceso = Proceso(id)
        misProcesos[id] = proceso
        proceso.start()
    servicio.run(host=HOST, port=PORT)
