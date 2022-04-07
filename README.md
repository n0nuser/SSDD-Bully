# Carrera 100 metros - Concurrencia + REST

## Instalación entorno virtual

Para instalar Poetry:

```
pip install poetry
```

Para instalar las dependencias:

```
poetry install
```

Para entrar al entorno virtual:

```
poetry shell
```

Y ya se estaría dentro del entorno virtual.

## Cómo ejecutar

```
# Para lanzar el servidor
poetry run start

# Para hacer sudar a los atletas...
python main/client.py
```

## Problemas encontrados

En el primer commit utilizamos FastAPI y no nos funcionaba, esto es debido a que es un servidor asíncrono, y para hacer concurrencia el servidor debe ser síncrono, por lo que en este último commit se ha utilizado Flask.

Las versiones utilizadas deben coincidir con las de clase, por lo que la versión de Python es la 3.5.3 y la versión de Flask acorde a la de Python es la 1.1.x.