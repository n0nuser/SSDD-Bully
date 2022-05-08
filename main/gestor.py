#!/usr/bin/python3.5
import sys
import os
import requests


def changeAddress():
    ip = input("Introduzca una dirección IP: ")
    port = int(input("Introduzca un puerto: "))
    return ip, port


def idProceso(ip, port):
    return requests.get("http://" + str(ip) + ":" + str(port) + "/api/id")


def eleccion(ip, port):
    return requests.get("http://" + str(ip) + ":" + str(port) + "/api/eleccion")


def coordinador(ip, port):
    return requests.get("http://" + str(ip) + ":" + str(port) + "/api/coordinador")


def arrancar(ip, port):
    return requests.get("http://" + str(ip) + ":" + str(port) + "/api/arrancar")


def parar(ip, port):
    return requests.get("http://" + str(ip) + ":" + str(port) + "/api/parar")


def computar(ip, port):
    return requests.get("http://" + str(ip) + ":" + str(port) + "/api/computar")


def estado(ip, port):
    return requests.get("http://" + str(ip) + ":" + str(port) + "/api/estado")


def exit():
    print("Saliendo...")
    sys.exit()


def menu():
    ip = "127.0.0.1"
    port = 8080
    endpoints = [
        "Cambiar proceso",
        "ID",
        "Eleccion",
        "Coordinador",
        "Arrancar",
        "Parar",
        "Computar",
        "Consultar Estado",
        "Salir",
    ]
    funciones = [
        changeAddress,
        idProceso,
        eleccion,
        coordinador,
        arrancar,
        parar,
        computar,
        estado,
        exit,
    ]
    while True:
        print("\n\nGESTOR DE ELECCIONES\n====================")
        for index, value in enumerate(endpoints):
            print(str(index + 1) + ".- " + str(value))
        print("====================\n")
        print("Proceso seleccionado: (" + str(ip) + ":" + str(port) + ")")
        opcion = int(input("Seleccione una opción: "))
        if opcion == 1:
            ip, port = changeAddress()
        elif len(endpoints) == opcion:
            if os.geteuid() != 0:
                os.system("sudo pkill python3.5")
            exit()
        else:
            print("\n" + funciones[opcion - 1](ip, port).text)


if __name__ == "__main__":
    menu()
