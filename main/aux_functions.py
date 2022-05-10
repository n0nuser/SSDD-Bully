import os
import json
import time
import logging
from random import randint


def read_config(FICHERO):
    dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(dir, FICHERO)
    try:
        with open(abs_file_path, "r") as f:
            data = f.read()
    except FileNotFoundError:
        logging.critical("No se encuentra el fichero de configuración.")
        exit()
    return json.loads(data)


def generate_node_id():
    millis = int(round(time.time() * 1000))
    node_id = millis + randint(800000000000, 900000000000)
    return node_id
