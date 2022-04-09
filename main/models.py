from threading import Thread, Condition, Lock
from time import sleep
import requests
from random import uniform as float_range
from threading import Lock

# numAtletas = 4
# HOST = "127.0.0.1"
# PORT = 8080
# FICHERO = "resultados.log"


# class Shot:
#     """Clase manejadora de los hilos. Define las funciones para la gestión de la concurrencia y notificación a los demás hilos."""

#     def __init__(self):
#         """ """
#         self._cond = Condition(Lock())
#         self._flag = False

#     def is_set(self):
#         """Devuelve el valor de la flag.
#         Returns:
#             flag (bool): Condición de espera.
#         """
#         return self._flag

#     def wait(self, timeout=None):
#         """Si el flag es falso, espera a que sea notificado.
#         Args:
#             timeout (int, optional): Tiempo a esperar máximo. Por defecto es: None.
#         Returns:
#             flag (bool): Se devuelve si es verdadero (no está esperando).
#         """
#         self._cond.acquire()
#         try:
#             signaled = self._flag
#             if not signaled:
#                 signaled = self._cond.wait(timeout)
#             return signaled
#         finally:
#             pass
#             self._cond.release()

#     def notify(self):
#         """Habilita la flag a verdadero y lo notifica. Dejando así los hilos que estuvieran bloqueados ejecutar sus funciones."""
#         self._cond.acquire()
#         try:
#             self._flag = True
#             self._cond.notify_all()
#         finally:
#             pass
#             self._cond.release()


# class Atleta(Thread):
#     """Clase del atleta, hereda de la clase Thread."""

#     def __init__(
#         self,
#         dorsal: str,
#     ):
#         self.dorsal = dorsal
#         Thread.__init__(self)

#     def start_race(self):
#         with open(FICHERO, "a+") as f:

#             preparado = requests.get("http://" + HOST + ":" + str(PORT) + "/preparado")
#             print(preparado.text)
#             f.write(self.dorsal + ": " + preparado.text + "\n")

#             listo = requests.get("http://" + HOST + ":" + str(PORT) + "/listo")
#             print(listo.text)
#             f.write(self.dorsal + ": " + listo.text + "\n")

#             """Espera un tiempo entre 9.56 y 11.76 segundos y lo imprime por pantalla."""
#             sleep(float_range(9.56, 11.76))

#             llegada = requests.get("http://" + HOST + ":" + str(PORT) + "/llegada/" + self.dorsal)
#             print(llegada.text)
#             f.write(self.dorsal + ": " + llegada.text + "\n")

#     def run(self):
#         """Método que sobrescribe al propio de la clase Thread.
#         Realiza el bloqueo hasta recibir la notificación, entonces ejecuta ciertas funciones.
#         """
#         self.start_race()


# class Variables:
#     def __init__(
#         self, numPreparados: int = 0, numListos: int = 0, numFinalizados: int = 0
#     ):
#         self.numPreparados = numPreparados
#         self.numListos = numListos
#         self.numFinalizados = numFinalizados

#     def actualizar(self, variable: str) -> int:
#         if variable == "preparados":
#             self.numPreparados = self.numPreparados + 1
#             return self.numPreparados
#         elif variable == "listos":
#             self.numListos = self.numListos + 1
#             return self.numListos
#         else:
#             self.numFinalizados = self.numListos + 1
#             return self.numFinalizados

#     def reiniciar(self) -> None:
#         self.numPreparados = 0
#         self.numListos = 0
#         self.numFinalizados = 0


class Proceso(Thread):
    def __init__(
        self,
        id: int,
        eleccion: dict = {"acuerdo": 0, "eleccion_activa": 0, "eleccion_pasiva": 0},
        coordinador: int = None,
        gestor: bool = False,
        estado: bool = True,
    ):
        self.id = id
        self.coordinador = coordinador
        self.gestor = gestor
        self.eleccion = eleccion
        self.estado = estado  # True = arrancado, False = parado

    def ok():
        print("")

    def eleccion(higher_nodes_array, node_id):
        status_code_array = []
        for each_port in higher_nodes_array:
            url = "http://localhost:%s/proxy" % each_port
            data = {"node_id": node_id}
            post_response = requests.post(url, json=data)
            status_code_array.append(post_response.status_code)
        if 200 in status_code_array:
            return 200

    def coordinador():
        print("")

    def arrancar(self):
        self.estado = True
        # hacer notify

    def parar(self):
        self.estado = False

    def computar(self):
        if self.estado == False:
            return False
        else:
            # Cambiar por threading.timer()
            sleep(float_range(0.1, 0.3))
            return True

    def run(self):
        while True:
            if self.estado == False:
                # Hacer un Wait
                pass
            else:
                # Cambiar por threading.timer()
                sleep(float_range(0.5, 1))
                if self.id == self.coordinador:
                    if self.computar() == False:
                        self.eleccion()


class Gestor:
    # HACER CLIENTE QUE PREGUNTE A TODOS SI SON GESTORES
    # EL QUE DE TRUE, GUARDAR SU INFO Y PETICION DE ARRANCAR O PARAR

    def __init__(self, jefazo: bool):
        self.jefazo = jefazo

    def soy_coordinador(self):
        return self.jefazo

    def arrancar(self, id):
        # GESTION LISTA DE OTROS PROCESOS CON SUS HOST Y PORT
        if self.jefazo:
            request = requests.get(
                "http://" + HOST + ":" + str(PORT) + "/arrancar/?id=" + str(id)
            )
            print(request.text)

    def parar(self, id):
        # GESTION LISTA DE OTROS PROCESOS CON SUS HOST Y PORT
        if self.jefazo:
            request = requests.get(
                "http://" + HOST + ":" + str(PORT) + "/parar/?id=" + str(id)
            )
            print(request.text)
