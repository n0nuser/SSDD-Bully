import sys
import json
import random
import logging
import requests
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


###############################################################################
# MANEJADORA WAIT Y NOTIFY
###############################################################################
class Handler:
    """Clase manejadora de los hilos. Define las funciones para la gestión de la concurrencia y notificación a los demás hilos."""

    def __init__(self):
        """ """
        self._cond = Condition(Lock())
        self._flag = False

    def is_set(self):
        """Devuelve el valor de la flag.
        Returns:
            flag (bool): Condición de espera.
        """
        return self._flag

    def wait(self, timeout=None):
        """Si el flag es falso, espera a que sea notificado.
        Args:
            timeout (int, optional): Tiempo a esperar máximo. Por defecto es: None.
        Returns:
            flag (bool): Se devuelve si es verdadero (no está esperando).
        """
        self._cond.acquire()
        try:
            signaled = self._flag
            if not signaled:
                signaled = self._cond.wait(timeout)
            return signaled
        finally:
            pass
            self._cond.release()

    def notify(self):
        """Habilita la flag a verdadero y lo notifica. Dejando así los hilos que estuvieran bloqueados ejecutar sus funciones."""
        self._cond.acquire()
        try:
            self._flag = True
            self._cond.notify_all()
        finally:
            pass
            self._cond.release()


###############################################################################


def nothing():  # Literally doing nothing
    pass


def proceso_run():
    # Este hace las peticiones a los demás procesos continuamente
    while True:
        if not proceso.estado:
            handler.wait()
        else:
            segundos = random.randint(0.5, 1)
            threading.Timer(segundos, nothing)
            computar = requests.get(
                f"http://{direcciones[proceso.coordinador]}/api/computar/"
            )
            if computar == False:
                idsMayores = [i for i in idsDireccion.keys() if i > proceso.id]
                for i in idsMayores:
                    eleccion = requests.get(f"http://{direcciones[i]}/api/eleccion")
                    print(eleccion.text)


def main():
    FICHERO = "config.json"
    global proceso, idsDireccion, handler
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
    handler = Handler()

    proceso_run = threading.Thread(target=proceso_run, args=(id, proceso)).start()

    try:
        # Este recibe las peticiones de los demás procesos
        api.run(host=host, port=port)
    except:
        logging.critical("Error al iniciar el servidor.", exc_info=True)

    proceso_run.join()


###############################################################################
# ENDPOINTS
###############################################################################
@api.route("/api/ok/")
def ok():
    print("")


@api.route("/api/eleccion/")
def eleccion():
    print("")


@api.route("/api/coordinador/")
def coordinador():
    print("")


@api.route("/api/arrancar/")
def arrancar():
    proceso.estado = True
    handler.notify()


@api.route("/api/parar/")
def parar():
    proceso.estado = False


@api.route("/api/computar/")
def computar():
    if not proceso.estado:
        return 400
    else:
        segundos = random.randint(0.1, 0.3)
        threading.Timer(segundos, nothing)
        return 200


###############################################################################

if __name__ == "__main__":
    main()
