from aux_functions import generate_node_id, read_config
from proceso import main
import threading
import logging
import time

if __name__ == "__main__":
    FICHERO = "config.json"
    data = read_config(FICHERO)
    process_number = data["process_number"]
    processes = []
    HOST = "127.0.0.1"
    for i in range(process_number):
        PORT = str(8080 + i)
        ID = generate_node_id()
        processes.append(threading.Thread(target=main, args=(HOST, PORT, ID)))
        processes[i].start()
    while True:
        time.sleep(1)
        for process in processes:
            logging.debug(str(process.native_id) + " : " + str(process.is_alive()))
