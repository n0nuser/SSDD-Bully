import contextlib
import itertools
import sys
import logging
import requests
import threading
from flask import Flask
from random import uniform as randfloat
from threading import Condition, Lock
from aux_functions import generate_node_id, read_config

Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream=sys.stdout, format=Log_Format, level=logging.DEBUG)

logger = logging.getLogger(__name__)
api = Flask(__name__)

###############################################################################
# CLASE PROCESO
###############################################################################
class Proceso:
    def __init__(
        self,
        id: int,
        direccion: str,
        puerto: int,
        eleccion=None,
        coordinador: int = None,
        gestor: bool = False,
        estado: bool = True,
    ):
        if eleccion is None:
            eleccion = {"acuerdo": 0, "eleccion_activa": 1, "eleccion_pasiva": 0}
        self.id = id
        self.direccion = direccion
        self.puerto = puerto
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
            return self._flag or self._cond.wait(timeout)
        finally:
            self._cond.release()

    def notify(self):
        """Habilita la flag a verdadero y lo notifica. Dejando así los hilos que estuvieran bloqueados ejecutar sus funciones."""
        self._cond.acquire()
        try:
            self._flag = True
            self._cond.notify_all()
        finally:
            self._cond.release()


###############################################################################


def nothing():  # Literally doing nothing
    pass


def proceso_run(miPuertoFlask):  # sourcery skip: avoid-builtin-shadow
    global proceso, idsDireccion, handler, direcciones
    # Este hace las peticiones a los demás procesos continuamente
    while True:
        if not proceso.estado:
            handler.wait()
        else:
            # logging.info("El numero de procesos es: " + str(process_number))
            segundos = randfloat(0.5, 1)
            threading.Timer(segundos, nothing)
            # logging.debug("INFORMACION MUY IMPORTANTE:" + str(idsDireccion[proceso.id]))
            idsDireccion[proceso.id] = [proceso.direccion, proceso.puerto]
            pingProcesos()
            if proceso.coordinador is None:
                # logging.info("Array direcciones:" + str(idsDireccion))
                eleccionRespuesta = eleccionCandidato()
                logging.info(
                    "No hay coordinador (http://localhost:"
                    + str(idsDireccion[proceso.id][1])
                    + "/api/eleccion) -> Respuesta eleccion: "
                    + eleccionRespuesta
                )
            else:
                logging.debug(
                    "\n  ###### ["
                    + str(proceso.id)
                    + "] Ya hay coordinador: "
                    + str(proceso.coordinador)
                    + " y en idsDireccion hay "
                    + str(idsDireccion)
                    + " ######"
                )
                try:
                    ip_coordinador = idsDireccion[proceso.coordinador][0]
                    puerto_coordinador = idsDireccion[proceso.coordinador][1]
                    if (puerto_coordinador != proceso.puerto) or (
                        ip_coordinador != proceso.direccion
                    ):
                        computar = requests.get(
                            "http://"
                            + ip_coordinador
                            + ":"
                            + str(puerto_coordinador)
                            + "/api/computar/"
                        ).text
                        if computar == "400":  # Si está en estado de espera
                            idsMayores = [
                                i for i in idsDireccion.keys() if i > proceso.id
                            ]
                            for i in idsMayores:
                                eleccion = requests.get(
                                    "http://" + direcciones[i] + "/api/eleccion"
                                ).text
                                logging.info(
                                    "Había coordinador. Respuesta eleccion: " + eleccion
                                )
                except Exception as e:
                    logging.debug(
                        "\n  ############################### ["
                        + str(proceso.id)
                        + "] ERROR: en idsDireccion hay "
                        + str(idsDireccion)
                        + " ######"
                    )


def pingProcesos():  # sourcery skip: avoid-builtin-shadow
    global idsDireccion, direcciones
    for direccion, port in itertools.product(direcciones, range(process_number)):
        puerto = 8080 + port
        print(str(proceso.id) + " -> ping a " + direccion + ":" + str(puerto))
        if (puerto != proceso.puerto) or (direccion != proceso.direccion):
            print(
                str(proceso.id)
                + " entra a hacer ping a "
                + direccion
                + ":"
                + str(puerto)
            )
            with contextlib.suppress(Exception):
                puerto = 8080 + port
                id = requests.get(
                    "http://" + direccion + ":" + str(puerto) + "/api/id/", timeout=1
                ).text
                idsDireccion[id] = [direccion, puerto]
                print(
                    "pingProcesos(): "
                    + str(proceso.id)
                    + " -> idsDireccion["
                    + str(id)
                    + "] = "
                    + str(idsDireccion[id])
                )
                logging.debug(
                    "RQUEST "
                    + str(proceso.id)
                    + " ("
                    + proceso.direccion
                    + ":"
                    + str(proceso.puerto)
                    + ") -> "
                    + str(id)
                    + " ("
                    + idsDireccion[id][0]
                    + ":"
                    + str(idsDireccion[id][1])
                    + ")"
                )


def main(host, port, id):  # sourcery skip: avoid-builtin-shadow
    FICHERO = "config.json"
    global proceso, idsDireccion, handler, direcciones, process_number
    # Puede dar problema al ser variables globales
    # por el hecho de que los demás hilos accedan
    # a la variable global de otro proceso

    data = read_config(FICHERO)
    direcciones = data["ip_addresses"]

    process_number = data["process_number"]
    idsDireccion = {}  # {id: [direccion, puerto]} -> {8080: ["192.168.1.15", 8080]}

    proceso = Proceso(id, host, port)
    handler = Handler()

    proceso_inicio = threading.Thread(target=proceso_run, args=(port,)).start()

    try:
        # Este recibe las peticiones de los demás procesos
        api.run(host=host, port=port)
    except Exception:
        logging.critical("Error en el servidor.")
        proceso_inicio.join()


###############################################################################
# ENDPOINTS
###############################################################################
@api.route("/api/id/")
def apiId():
    # logging.info(" +proceso.id + " <- Coordinador: " +proceso.coordinador)
    return str(proceso.id)


# @api.route("/api/ok/")
# def ok():
#     return "200"


def eleccionThread():
    global proceso, idsDireccion
    # inicio
    logging.debug(
        "\n ########### ENTRAMOS EN UNA ELECCION ["
        + str(proceso.id)
        + "] ###########\n"
    )
    pingProcesos()
    logging.debug(
        "\n ########### "
        + str(proceso.id)
        + " -> idsDireccion: "
        + str(idsDireccion)
        + "\n"
    )
    idsMayores = [id for id in idsDireccion.keys() if int(id) > proceso.id]
    logging.debug(
        "\n ########### idsMayores ["
        + str(proceso.id)
        + "]: "
        + str(idsMayores)
        + " ###########\n"
    )
    if idsMayores:
        eleccion = []
        for id in idsMayores:
            ip = idsDireccion[id][0]
            port = idsDireccion[id][1]
            # Pregunto a todos los demás si están en estado de espera
            eleccion.append(
                requests.get(
                    "http://" + ip + ":" + str(port) + "/api/eleccion/", timeout=1
                ).text
            )
            # Si alguno me responde un 200
            # esperamos en el endpoint coordinador el id del nuevo coordinador
            # si en un periodo de 1 segundo, no nos ha llegado ese mensaje, empezamos nuevas elecciones

        # Si no existe un proceso con ID mayor que el mío ENCENDIDO
        print("Datos ELECCION: " + str(eleccion))
        if "200" not in eleccion:
            # Me autoproclamo coordinador
            logging.debug(
                "\n################### ELECCION COORDINADOR: "
                + str(proceso.id)
                + " ###################"
            )
            proceso.coordinador = proceso.id
            for direccion, port in itertools.product(
                direcciones, range(process_number)
            ):
                # Y se lo digo a los demás procesos
                requests.get(
                    "http://"
                    + direccion
                    + ":"
                    + str(port)
                    + "/api/coordinador/"
                    + str(proceso.id)
                )
    else:
        # Si no hay ningún proceso con ID mayor que el mío
        # Me autoproclamo coordinador
        proceso.coordinador = proceso.id
        for direccion, port in itertools.product(direcciones, range(process_number)):
            # Y se lo digo a los demás procesos
            try:
                if ((8080 + port) != proceso.puerto) or (
                    direccion != proceso.direccion
                ):
                    print(str(proceso.id) + " -> " + direccion + ":" + str(8080 + port))
                    requests.get(
                        "http://"
                        + direccion
                        + ":"
                        + str(8080 + port)
                        + "/api/coordinador/"
                        + str(proceso.id)
                    )
            except Exception as e:
                print("No se ha podido conectar con " + direccion + ":" + str(port))


@api.route("/api/eleccion/")
def eleccionCandidato():
    eleccionTh = threading.Thread(target=eleccionThread).start()
    # Responder a una petición de elección
    return "200" if proceso.estado else "400"


@api.route("/api/coordinador/<int:id>")
def coordinador(id):
    #   si recibe mensaje coordinador(x)
    #       pi.coordinador ← x
    #       fin
    proceso.coordinador = id
    logging.info(
        "\n##########################"
        + str(proceso.id)
        + " <- Coordinador: "
        + str(proceso.coordinador)
        + "##########################\n"
    )
    return "200"


@api.route("/api/arrancar/")
def arrancar():
    proceso.estado = True
    handler.notify()
    return "200"


@api.route("/api/parar/")
def parar():
    proceso.estado = False
    return "200"


@api.route("/api/computar/")
def computar():
    if not proceso.estado:
        return "400"
    segundos = randfloat(0.1, 0.3)
    threading.Timer(segundos, nothing)
    return "200"


###############################################################################

# sourcery skip: avoid-builtin-shadow
if __name__ == "__main__":
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        id = int(sys.argv[3])
    except IndexError:
        if not host or not port or not id:
            host = "127.0.0.1"
            port = 8080
            id = generate_node_id()
    # logging.info("HOST: " + host + "\nPORT: " + str(port) + "\nID: " + str(id))
    main(host, port, id)
