from aux_functions import generate_node_id, read_config
from proceso import main
import threading
import logging
import json
import os

if __name__ == "__main__":
    FICHERO = "config.json"
    data = read_config(FICHERO)
    process_number = data["process_number"]
    for i in range(process_number):
        HOST = "127.0.0.1"
        PORT = str(8080 + i)
        ID = generate_node_id()

        threading.Thread(target=main, args=(HOST, PORT, ID)).start()
