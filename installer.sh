#!/bin/bash

sudo mkdir noMirar
cd noMirar/SSDD-Bully-main
sudo apt install python3-pip -y
pip install poetry 
poetry run
cd main
poetry shell
#poetry run bash ./launch.sh #Solo funciona cuando te sales de la terminal de poetry
