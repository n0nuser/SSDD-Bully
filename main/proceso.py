import sys
import json
import random
import logging
import requests
import threading
from flask import Flask
from random import uniform as randfloat
from threading import Thread, Condition, Lock
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


def proceso_run(miPuertoFlask):
    # Este hace las peticiones a los demás procesos continuamente
    while True:
        if not proceso.estado:
            handler.wait()
        else:
            print("El numero de procesos es: " + str(process_number))
            segundos = randfloat(0.5, 1)
            threading.Timer(segundos, nothing)
            idsDireccion[proceso.id] = ["localhost", miPuertoFlask]
            for direccion in direcciones:
                for port in range(process_number):
                    try:
                        puerto = 8080 + port
                        id = requests.get(
                            f"http://{direccion}:{puerto}/api/id", timeout=1
                        ).text
                        print(id)
                        idsDireccion[id] = [direccion, puerto]
                    except:
                        print(
                            "NO HACE LA PETICIÓN DE BUSCAR A "
                            + str(direccion)
                            + ":"
                            + str(puerto)
                        )
                        pass

            if proceso.coordinador == None:
                print(idsDireccion)
                miPuerto = idsDireccion[proceso.id][1]
                eleccion = requests.get(f"http://localhost:{miPuerto}/api/eleccion")
                print(eleccion.text)

            ip_coordinador = idsDireccion[proceso.coordinador][0]
            puerto_coordinador = idsDireccion[proceso.coordinador][1]
            computar = requests.get(
                f"http://{ip_coordinador}:{puerto_coordinador}/api/computar/"
            ).text
            if computar == "400":  # Si está en estado de espera
                idsMayores = [i for i in idsDireccion.keys() if i > proceso.id]
                for i in idsMayores:
                    eleccion = requests.get(
                        f"http://{direcciones[i]}/api/eleccion"
                    ).text
                    print(eleccion)


def main(host, port, id):
    FICHERO = "config.json"
    global proceso, idsDireccion, handler, direcciones, process_number
    # Puede dar problema al ser variables globales
    # por el hecho de que los demás hilos accedan
    # a la variable global de otro proceso

    try:
        host = sys.argv[1]
        port = sys.argv[2]
        id = sys.argv[3]
    except IndexError:
        if not host or not port or not id:
            host = "127.0.0.1"
            port = 8080
            id = generate_node_id()
    print(f"HOST: {host}\nPORT: {port}\nID: {id}")

    data = read_config(FICHERO)
    direcciones = data["ip_addresses"]

    process_number = data["process_number"]
    idsDireccion = {}  # {id: [direccion, puerto]} -> {8080: ["192.168.1.15", 8080]}

    proceso = Proceso(id)
    handler = Handler()

    proceso_inicio = threading.Thread(target=proceso_run, args=(port,)).start()

    try:
        # Este recibe las peticiones de los demás procesos
        api.run(host=host, port=port)
    except:
        logging.critical("Error al iniciar el servidor.", exc_info=True)

    proceso_inicio.join()


###############################################################################
# ENDPOINTS
###############################################################################
@api.route("/api/id/")
def id():
    return str(proceso.id)


@api.route("/api/ok/")
def ok():
    print("No sabemos qué hacer con este")


def eleccion():
    # inicio
    idsMayores = [id for id in idsDireccion.keys() if id > proceso.id]
    for id in idsMayores:
        ip = idsDireccion[id][0]
        port = idsDireccion[id][1]
        # pj.eleccion() para todo pj con j>i
        # esperar mensaje respuesta (timeout 1s)
        eleccion = requests.get(f"http://{ip}:{port}/api/eleccion/", timeout=1).text
        # if eleccion==200:
        # esperamos en el endpoint coordinador el id del nuevo coordinador
        # si en un periodo de 1 segundo, no nos ha llegado ese mensaje, empezamos nuevas elecciones

    if eleccion == "400":
        # si no recibe mensaje respuesta tras timeout
        #     pi.coordinador ← i //se hace nuevo coordinador
        proceso.coordinador = proceso.id
        for direccion in direcciones:
            for port in range(process_number):
                #     pj.coordinador(i) para todo pj (j=1...numProcesos)
                requests.get(f"http://{direccion}:{port}/api/coordinador/{proceso.id}")


@api.route("/api/eleccion/")
def eleccionCandidato():
    eleccion = threading.Thread(target=eleccion).start()

    # Responder a una petición de elección
    if proceso.estado:
        return "200"
    else:
        return "400"


@api.route("/api/coordinador/<int:id>")
def coordinador(id):
    #   si recibe mensaje coordinador(x)
    #       pi.coordinador ← x
    #       fin
    proceso.coordinador = id


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
        return "400"
    else:
        segundos = randfloat(0.1, 0.3)
        threading.Timer(segundos, nothing)
        return "200"


###############################################################################

if __name__ == "__main__":
    main()
