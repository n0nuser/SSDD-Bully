from aux_functions import generate_node_id, read_config
from flask import Flask
from random import uniform as randfloat
from threading import Condition, Lock
import contextlib
import itertools
import logging
import requests
import sys
import threading
import socket

api = Flask(__name__)
flask_logger = logging.getLogger("werkzeug")
flask_logger.setLevel(logging.ERROR)

Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream=sys.stdout, format=Log_Format, level=logging.INFO)
logger = logging.getLogger(__name__)


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
        estado: bool = True,
    ):
        if eleccion is None:
            eleccion = {
                "acuerdo": False,
                "eleccion_activa": True,
                "eleccion_pasiva": False,
            }
        self.id = id
        self.direccion = direccion
        self.puerto = puerto
        self.eleccion = eleccion
        self.coordinador = coordinador
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


def nothing():
    """
    Función que no hace nada.
    """
    pass


def proceso_run():  # sourcery skip: avoid-builtin-shadow
    global proceso, idsDireccion, handler, direcciones
    """
    Hilo principal que maneja el funcionamiento del proceso.
    """
    while True:
        # Si el equipo está "apagado" queda en estado de espera
        if proceso.estado == False:
            handler.wait()
        else:
            logging.debug("El numero de procesos es: " + str(process_number))

            # Espera un tiempo aleatorio entre 0.5 y 1 segundos
            segundos = randfloat(0.5, 1)
            threading.Timer(segundos, nothing)

            # Se introduce en el diccionario de direcciones el puerto y dirección del proceso actual
            idsDireccion[proceso.id] = [proceso.direccion, proceso.puerto]

            # Busca procesos
            pingProcesos()

            # Si no hay coordinador (caso inicial)
            if proceso.coordinador is None:
                logging.debug("Array direcciones:" + str(idsDireccion))
                logging.info("ELECCION (" + str(proceso.id) + "): elección activa (coordinador None)")
                # Se empieza un proceso de elección activa
                proceso.eleccion = {
                    "acuerdo": False,
                    "eleccion_activa": True,
                    "eleccion_pasiva": False,
                }
                # Se busca el proceso con mayor ID para ser el coordinador
                eleccionRespuesta = eleccionCandidato()
                logging.debug("No hay coordinador (http://localhost:" + str(idsDireccion[proceso.id][1]) + "/api/eleccion) -> Respuesta eleccion: " + eleccionRespuesta)
            # Ya existe un coordinador
            else:
                logging.debug("[" + str(proceso.id) + "] Ya hay coordinador: " + str(proceso.coordinador) + " y en idsDireccion hay " + str(idsDireccion))
                try:
                    ip_coordinador = idsDireccion[proceso.coordinador][0]
                    puerto_coordinador = idsDireccion[proceso.coordinador][1]

                    # Si no soy el coordinador, llamo al computar del coordinador
                    # para verificar si está encendido o apagado
                    if (puerto_coordinador != proceso.puerto) or (ip_coordinador != proceso.direccion):
                        computar = requests.get("http://" + ip_coordinador + ":" + str(puerto_coordinador) + "/api/computar/").text
                        # Si está en estado de espera
                        if computar == "400":  # Si está en estado de espera
                            logging.info("ELECCION (" + str(proceso.id) + "): elección activa (coordinador apagado)")
                            proceso.eleccion = {
                                "acuerdo": False,
                                "eleccion_activa": True,
                                "eleccion_pasiva": False,
                            }
                            # Si el proceso no está apagado, se busca el proceso con mayor ID para ser el coordinador
                            if proceso.estado:
                                eleccionTh = threading.Thread(target=eleccionThread).start()
                        # Si el coordinador está activo, la elección está en acuerdo
                        else:
                            logging.info("ELECCION (" + str(proceso.id) + "): acuerdo")
                            proceso.eleccion = {
                                "acuerdo": True,
                                "eleccion_activa": False,
                                "eleccion_pasiva": False,
                            }
                except Exception as e:
                    logging.debug(
                        (((("[" + str(proceso.id)) + "] ERROR: en idsDireccion hay ") + str(idsDireccion) + " -> (") + str(proceso.coordinador) + ")"),
                        exc_info=True,
                    )


def pingProcesos():
    """
    Conociendo el número de puertos, hace una petición a cada dirección para recoger el ID de ese proceso.
    Entonces, lo guarda en el diccionario de direcciones.
    """
    global proceso, idsDireccion, direcciones
    # El producto de los puertos y las direcciones
    for direccion, port in itertools.product(direcciones, range(process_number)):
        puerto = 8080 + port
        # Si no soy yo, hago la petición
        if (puerto != proceso.puerto) or (direccion != proceso.direccion):
            logging.debug(str(proceso.id) + " -> ping a " + direccion + ":" + str(puerto))
            with contextlib.suppress(Exception):
                id = int(
                    requests.get(
                        "http://" + direccion + ":" + str(puerto) + "/api/id/",
                        timeout=1,
                    ).text
                )
                # Guardo el ID del puerto y dirección al que acabo de preguntar
                idsDireccion[id] = [direccion, puerto]


def main(host, portFlask, id):
    global proceso, idsDireccion, handler, direcciones, process_number
    FICHERO = "config.json"

    # Lee la configuración del fichero
    data = read_config(FICHERO)
    direcciones = data["ip_addresses"]
    process_number = data["process_number"]
    idsDireccion = {}  # {id: [direccion, puerto]} -> {8080: ["192.168.1.15", 8080]}

    # Instancia la clase Proceso
    proceso = Proceso(id, host, portFlask)

    # Instancia el manejador de eventos
    handler = Handler()

    # Crea un hilo para la gestión principal del proceso
    proceso_inicio = threading.Thread(target=proceso_run).start()

    try:
        # Lanza el servidor Flask (REST API)
        api.run(host=host, port=portFlask)
    except Exception:
        logging.critical("Error en el servidor (" + str(host) + ":" + str(port) + ")")
        proceso_inicio.join()


###############################################################################
# MÉTODOS AUXILIARES DE LOS ENDPOINT
###############################################################################

def eleccionThread():
    """
    Gestiona las peticiones de elecciones.
    """
    global proceso, idsDireccion
    if proceso.estado:
        logging.debug("#" + str(proceso.id) + " -> idsDireccion: " + str(idsDireccion))
        idsMayores = [id for id in idsDireccion.keys() if int(id) > proceso.id]
        logging.debug("idsMayores [" + str(proceso.id) + "]: " + str(idsMayores))

        # Sólo hace las peticiones a los procesos con un ID mayor que el suyo
        if idsMayores:
            eleccion = []
            for id in idsMayores:
                ip = idsDireccion[id][0]
                port = idsDireccion[id][1]
                # Pregunto a todos los demás si están en estado de espera, y estos inician la elección en caso negativo
                eleccion.append(requests.get("http://" + ip + ":" + str(port) + "/api/eleccion/", timeout=1).text)

                # Si alguno me responde un 200
                # esperamos en el endpoint coordinador el id del nuevo coordinador
                # si en un periodo de 1 segundo, no nos ha llegado ese mensaje, empezamos nuevas elecciones

            # Si no existe un proceso con ID mayor que el mío ENCENDIDO que me de el OK
            if "200" not in eleccion:
                # Me autoproclamo coordinador
                proceso.coordinador = proceso.id
                logging.info(
                    str(proceso.id) + " <- Coordinador: " + str(proceso.coordinador)
                )
                for direccion, port in itertools.product(
                    direcciones, range(process_number)
                ):
                    puerto = 8080 + port
                    # Y se lo digo a los demás procesos
                    requests.get(
                        "http://"
                        + direccion
                        + ":"
                        + str(puerto)
                        + "/api/coordinador/"
                        + str(proceso.id)
                    )
                proceso.eleccion = {
                    "acuerdo": True,
                    "eleccion_activa": False,
                    "eleccion_pasiva": False,
                }
            else:
                logging.info("ELECCION (" + str(proceso.id) + "): elección pasiva")
                # Si existe, la eleccion es pasiva
                proceso.eleccion = {
                    "acuerdo": False,
                    "eleccion_activa": False,
                    "eleccion_pasiva": True,
                }
        else:
            # Si no hay ningún proceso con ID mayor que el mío
            # Me autoproclamo coordinador
            proceso.coordinador = proceso.id
            logging.info(str(proceso.id) + " <- Coordinador: " + str(proceso.coordinador))
            for direccion, port in itertools.product(direcciones, range(process_number)):
                # Y se lo digo a los demás procesos
                with contextlib.suppress(Exception):
                    puerto = 8080 + port
                    if (puerto != proceso.puerto) or (direccion != proceso.direccion):
                        requests.get(
                            "http://"
                            + direccion
                            + ":"
                            + str(puerto)
                            + "/api/coordinador/"
                            + str(proceso.id)
                        )
            proceso.eleccion = {
                "acuerdo": True,
                "eleccion_activa": False,
                "eleccion_pasiva": False,
            }
    else:
        pass


###############################################################################
# ENDPOINTS
###############################################################################
@api.route("/api/id/")
def apiId():
    """Devuelve su ID si está activo"""
    global proceso
    return str(proceso.id) if proceso.estado else ""


@api.route("/api/eleccion/")
def eleccionCandidato():
    """
    Si está en estado de espera devuelve 400, si no, inicia la elección y devuelve 200.
    """
    global proceso
    if proceso.estado:
        eleccionTh = threading.Thread(target=eleccionThread).start()
        return "200"
    else:
        return "400"


@api.route("/api/coordinador/<int:id>")
def coordinador(id):
    """Asigna el coordinador a el proceso actual."""
    global proceso
    proceso.coordinador = id
    proceso.eleccion = {
        "acuerdo": True,
        "eleccion_activa": False,
        "eleccion_pasiva": False,
    }
    logging.info(str(proceso.id) + " <- Coordinador: " + str(proceso.coordinador))
    return "200"


@api.route("/api/estado/")
def estado():
    """Devuelve información del estado del proceso."""
    global proceso
    texto = "ID: " + str(proceso.id)
    texto += "\nEncendido (estado): " + str(proceso.estado)
    texto += "\nCoordinador: " + str(proceso.coordinador)
    for key, value in proceso.eleccion.items():
        if value == 1:
            texto += "\nEstado elección: " + str(key)
    return texto


@api.route("/api/arrancar/")
def arrancar():
    global proceso
    handler.notify()
    if proceso.estado:
        return "400"
    logging.info(str(proceso.id) + " -> Arrancado")
    proceso.estado = True
    eleccionTh = threading.Thread(target=eleccionThread).start()
    return "200"


@api.route("/api/parar/")
def parar():
    """Pone el estado del proceso a False de tal forma que en el hilo del proceso principal, se hará el Wait y quedará bloqueado."""
    global proceso
    if not proceso.estado:
        return "400"
    logging.info(str(proceso.id) + " -> Parado")
    proceso.estado = False
    return "200"


@api.route("/api/computar/")
def computar():
    """Devuelve si está apagado o no."""
    global proceso
    if not proceso.estado:
        return "400"
    segundos = randfloat(0.1, 0.3)
    threading.Timer(segundos, nothing)
    return "200"


###############################################################################
# MAIN
###############################################################################

if __name__ == "__main__":
    # Se recoge el puerto por argumento
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <port>")
        sys.exit()
    port = int(sys.argv[1])

    # Coge la dirección IP (que tiene conexión a internet) del equipo
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host = s.getsockname()[0]

    # Genera un ID aleatorio
    id = generate_node_id()

    logging.info("HOST: " + host + "PORT: " + str(port) + "ID: " + str(id))
    main(host, port, id)
