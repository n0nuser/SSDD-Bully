import sys
import json
import logging
import threading
from flask import Flask
from aux_functions import generate_node_id, read_config

logger = logging.getLogger(__name__)
api = Flask(__name__)

###############################################################################
# CLASE PROCESO
###############################################################################
class Proceso:
    def __init__(
        self,
        id: int,
        eleccion={"acuerdo": 0, "eleccion_activa": 1, "eleccion_pasiva": 0},
        coordinador: int = None,
        gestor: bool = False,
        estado: bool = True,
    ):
        self.id = id
        self.eleccion = eleccion
        self.coordinador = coordinador
        self.gestor = gestor
        self.estado = estado


###############################################################################


def proceso_run(id):
    # Este hace las peticiones a los demás procesos continuamente
    print("")


def main():
    FICHERO = "config.json"
    global proceso, idsDireccion
    # Puede dar problema al ser variables globales
    # por el hecho de que los demás hilos accedan
    # a la variable global de otro proceso

    try:
        host = sys.argv[1]
        port = sys.argv[2]
        id = sys.argv[3]
    except IndexError:
        host = "127.0.0.1"
        port = 8080
        id = generate_node_id()
    print(f"HOST: {host}\nPORT: {port}\nID: {id}")

    data = read_config(FICHERO)
    direcciones = data["ip_addresses"]
    idsDireccion = {}  # {id: direccion} -> {150: "192.168.1.15"}

    proceso = Proceso(id)

    proceso_run = threading.Thread(target=proceso_run, args=(id)).start()

    try:
        # Este recibe las peticiones de los demás procesos
        api.run(host=host, port=port)
    except:
        logging.critical("Error al iniciar el servidor.", exc_info=True)

    proceso_run.join()


###############################################################################
# ENDPOINTS
###############################################################################
@api.route("/api/ok?id=<int:id>")
def ok(id: int):
    print("")


@api.route("/api/eleccion?id=<int:id>")
def eleccion(id: int):
    print("")


@api.route("/api/coordinador?id=<int:id>")
def coordinador(id: int):
    print("")


@api.route("/api/arrancar?id=<int:id>")
def arrancar(id: int):
    print("")


@api.route("/api/parar?id=<int:id>")
def parar(id: int):
    print("")


@api.route("/api/computar?id=<int:id>")
def computar(id: int):
    print("")


###############################################################################

if __name__ == "__main__":
    main()
