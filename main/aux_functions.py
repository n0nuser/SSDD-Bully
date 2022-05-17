import os
import json
import logging
from random import randint


def read_config(FICHERO):
    dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(dir, FICHERO)
    try:
        with open(abs_file_path, "r") as f:
            data = f.read()
    except FileNotFoundError:
        logging.critical('No se encuentra el fichero de configuración. Ejemplo: {\n\t"ip_addresses": ["192.168.1.14", "192.168.1.50"],\n\t"process_number": 2,\n\t"min_id": 1,\n\t"max_id": 9999\n}')
        exit()
    return json.loads(data)


def generate_node_id():
    data = read_config("config.json")
    min_id = data["min_id"]
    max_id = data["max_id"]
    return randint(min_id, max_id)
