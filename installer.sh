#!/bin/bash

sudo apt update
sudo apt install python3-pip -y
pip3 install poetry

mkdir pendrive
mkdir noMirar
sudo mount /dev/sdb1 pendrive
sudo unzip pendrive/SSDD-Bully.zip -d noMirar

cd noMirar/
poetry install
cd main
poetry run bash launch.sh