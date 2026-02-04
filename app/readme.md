# API para la gestion y reputación de dominios

## DESCRIPCION

El proyecto sirve para gestionar dominios y analizar la reputación mediante consultas a los servicios externos VirusTotal (VT) y Urlscan.

La API permite crear, listar, actualizar y elimanar dominos de la base de datos mostrando información como:

- IP actual del dominio
- Indica si dispone o no de servidor de correo (MX)
- Muestra un score de puntución, calculado a partir de las fuentes de reputación
- Consulta las fuentes de reputacion de VT y Urlscan de forma automática cía API
- Permite actualizar/añadir fuentes de forma manual
- Permite añadir etiquetas

## FUNCIONES

### Crear Dominio

Nos permite crear un domino pasando el nombre del dominio y opcionalmente se le pueden añadir etiquetas. El resto de datos se obtienen de forma automática.

### Actualizar Dominio

Permite actualizar un dominio grabado previamente, pasando de forma opcional etiquetas, fuentes de reputacion, y estado del dominio. Igualmente se vuelven a actualizar el resto de datos incluyendo la fecha de la actualización.

### Lista todos los dominios

Permite obtener todos los dominos almacenados en la base de datos.

### Lista un dominio

Permite obtener los datos del dominio solicitado.

### Lista dominios según estado

Permite obtener todos los dominios que están guardados con el estado solicitado.

### Lista dominios según score

Permite obtener todos los dominios que están guardados y tienen un score que el solicitado.

### Lista domino segun MX

Permite obtener todos los dominos que están guardados y tienen o no MX, según se indique.

### Borrar dominio

Permite borrar un dominio de la base de datos

## ARCHIVOS DEL PROYECTO

- crud.py -> Contiene las funciones de CRUD y hace los calculos del score de reputacion
- database.py -> Contiene la configuracion de la base de datos SQLite
- main.py -> Es el archivo donde se inicial FastAPI y se definen los endpoints
- models.py -> Se define con SQLAlchemy la estructura y los campos de la Base de datos
- schemas.py -> Se definen los modelos para la validacion de datos con Pydantic
- servicios_ex.py -> Contiene las funciones que conectan con las APIs VT y Urlscan y obtienen datos DNS
- requirements.txt -> Contiene todas las librerías necesarias para que la API y el Script funcionen
- test_api_dominios.py -> Es un Script para probar la API con consultas requests
- .ven.ejemplo -> Es un archivo de ejemplo con el nombre de las variables de entorno para las API KEYs

Una vez iniciado FastAPI se crean los siguientes archivos:

- dominios.db -> Es la base de datos que contiene los dominios guardados
- debug.log -> En este archivo se registran todos los logs desde el nivel Debug hasta Critical
- warning.log -> En este archico se registran todos los logs con niveles warining y critical

## INSTALACION

- Guardamos todos los archivos en un directorio
- Nos situamos en el directorio con el comando cd
- Es aconsejable crear un entorno virtual con el comando python -m venv [nombre_entorno]. ejem: python -m venv dominios
- Si hemos creado el entorno debemos activarlo con \.\[nombre_entorno]\Script\Activate. ejem: .\dominios\Script\Activate
- En cualquier caso, con o sin entorno virtual, instalamos las dependencias con el comando pip install -r requirements.txt
- Arrancamos la API con el comando uvicorn main:app
- Abrimos otra terminal y ejecutamos el comando python test_api_dominios.py
