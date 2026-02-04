import asyncio
import logging
import schemas, crud
from fastapi import FastAPI, HTTPException, Depends
from database import SessionLocal, engine
from models import DecBase, EstadoDominio
from fastapi.concurrency import run_in_threadpool
from servicios_ext import tiene_mx, obtiene_ip, fuentes_reputacion
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger("dominio")

app = FastAPI(title="Dominios")
logger.info("FastAPI inicializada")

@app.on_event("startup")
def startup_event():
    DecBase.metadata.create_all(bind=engine)
    logger.debug("Se crea la Base de Datos si no existe")

# Funcion que inicia la sesiona a la base de datos creada en el archivo database.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuramos un mensaje de Bienvenida para la raiz de la API
@app.get("/")
def bienvenida():
    return {"message": "Bienvenido a la API de Dominios"}

# Configuramos el Endpoint para crear un dominio en la base de datos. 
# Usamos una función asincrona para trabajar con las consultas externas
@app.post("/dominio", response_model=schemas.DominioSalida)
async def create_domain(datos: schemas.CrearDominio, db=Depends(get_db)):
    logger.debug(f"POST /dominio datos: {datos}")
    # Primero buscamos el dominio en la BD. Si existe evitamos realizar las consultas externas
    dominio = crud.get_dominio(db, datos.nombre)
    if dominio:
        logger.info(f"[-] El dominio {datos.nombre} ya existe")
        raise HTTPException(status_code=400, detail=f"[-] El dominio {datos.nombre} ya existe.")
    
    logger.debug("[+] Iniciando tareas asincronas")
    # Creamos las tareas en hilos diferentes
    tarea_ip = run_in_threadpool(obtiene_ip, datos.nombre)
    tarea_mx = run_in_threadpool(tiene_mx, datos.nombre)
    tarea_fuentes_reputacion = run_in_threadpool(fuentes_reputacion, datos.nombre)
    # Esperamos que se hayan ejecutado las tres y guardamos los resultados 
    ip, mx, f_reputacion = await asyncio.gather(tarea_ip, tarea_mx, tarea_fuentes_reputacion)

    try:
        # Se crea el dominio llamando a la funcion que se encuetra en el archivo crud.py
        # La funcion devuelve el dominio que es de tipo schemas.DominioSalida
        dominio = crud.crea_dominio(db, datos, ip, mx, f_reputacion) 
        return dominio # Devuelve un domino con el formato definido en schemas.DominioSalida
    except ValueError as e:
        # Si la consulta fallase devolverá un código 400 y lanza un warning para revisar
        logger.warning(f"Error al crear el dominio: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Configuramos el Endpoint para que muestre todos los dominios guardados en la BD.
@app.get("/dominios", response_model=list[schemas.DominioSalida])
def list_domaind(db=Depends(get_db)):
    logger.debug("GET /dominios llamada")
    # Se llama a la funcion del archivo crud.py para listar todos los dominios de la BD
    dominios = crud.lista_dominios(db) 
    return dominios # Devuelve una lista de dominios con el formato definido en schemas.DominioSalida

# Configuramos el Endpoint para que nos devuelva el dominio solicitado si existe en la BD
@app.get("/dominio/{nombre_dominio}", response_model=schemas.DominioSalida)
def get_domain(nombre_dominio: str, db=Depends(get_db)):
    logger.debug(f"GET /dominio/{nombre_dominio} llamada")
    # Se llama a la funcion del archivo crud.py para obtener el dominio solicitado de la BD
    dominio = crud.get_dominio(db, nombre_dominio)
    # Si el dominio no existe se lanza una excepción
    if not dominio:
        raise HTTPException(status_code=404, detail=f"Dominio '{nombre_dominio}' no encontrado")
    return dominio # Devuelve un domino con el formato definido en schemas.DominioSalida

# Configuramos el Endpoint para actualizar un dominio de la base de datos con los valores pasados.
# También usamos una función asincrona porque hace llamadas a servicios externos
@app.patch("/dominio/{nombre_dominio}", response_model=schemas.DominioSalida)
async def update_domain(nombre_dominio: str, datos: schemas.ActualizaDominio, db=Depends(get_db)):
    logger.debug(f"PATCH /dominio/{nombre_dominio} datos: {datos} llamada")
    # Verificamos que el dominio exite. Si no existe lanzamos una excepcion
    dominio = crud.get_dominio(db, nombre_dominio)
    if not dominio:
        logger.info(f"[-] El dominio {nombre_dominio} no existe")
        raise HTTPException(status_code=404, detail=f"[-] El dominio {nombre_dominio} no existe")

    logger.debug("[+] Iniciando tareas asincronas")
    # Creamos los hilos donde se van a ejecutar las tareas
    tarea_ip = run_in_threadpool(obtiene_ip, nombre_dominio)
    tarea_mx = run_in_threadpool(tiene_mx, nombre_dominio)
    tarea_fuentes_reputacion = run_in_threadpool(fuentes_reputacion, nombre_dominio)
    # Esperamos que terminen todas y se almacenan las respuestas
    ip, mx, f_reputacion = await asyncio.gather(tarea_ip, tarea_mx, tarea_fuentes_reputacion)
    # Creamos una lista vacía para el caso que no hay fuentes de reputación almacenadas.
    if datos.fuentes_reputacion is None:
        datos.fuentes_reputacion = []
    # Fusionamos las listas de reputacion que están almacenadas en la BD con las que pasa el usuario
    datos.fuentes_reputacion.extend(f_reputacion)
    # Se llama a la funcion del archivo crud.py para actualizar el dominio en la BD
    dominio = crud.update_dominio(db, nombre_dominio, datos, ip, mx)
    if not dominio:
       raise HTTPException(status_code=400, detail=f"Fallo al actualizar el dominio '{nombre_dominio}'")
    return dominio # Devuelve un domino con el formato definido en schemas.DominioSalida 

# Configuramos el Endpoint para borrar un dominio de la BD.
@app.delete("/dominio/{nombre_dominio}")
def delete_domain(nombre_dominio: str, db=Depends(get_db)):
    logger.debug(f"DELETE /dominio/{nombre_dominio} llamada")
    dominio = crud.delete_dominio(db, nombre_dominio)
    if not dominio:
        raise HTTPException(status_code=404, detail=f"Dominio '{nombre_dominio}' no encontrado")
    return {"message": f"Dominio '{nombre_dominio}' borrado"}

# Configuramos el Endpoint para obtener los dominios de la BD segun el estado.
@app.get("/dominios/estado/{estado}", response_model=list[schemas.DominioSalida])
def get_domain_state(estado: str, db=Depends(get_db)):
    try:
        estado_enum = EstadoDominio(estado)
    except ValueError:
        logger.info(f"El usuario ha introducido un estado '{estado}' no permitido")
        valores_validos = [valor.value for valor in EstadoDominio]
        raise HTTPException(
            status_code=422,
            detail=f"El estado '{estado}' no está permitido. Elige uno entre los siguientes {valores_validos}"
        )
    dominios = crud.lista_dom_estado(db, estado_enum)
    return dominios # Devuelve una lista con los dominios en el formato definido en schemas.DominioSalida

# Configuramos el Endpoint para obtener los dominios de la BD con un score menor al indicado.
@app.get("/dominios/reputacion/{score}", response_model=list[schemas.DominioSalida])
def get_domain_score(score: int, db=Depends(get_db)):
    logger.debug(f"GET /dominio/reputacion/{score} llamada")
    dominios = crud.lista_dom_score(db, score)
    return dominios # Devuelve una lista con los dominios en el formato definido en schemas.DominioSalida

# Configuramos el Endpoint para obtener los dominios de la BD segun la disponibilidad de servidor de correo.
@app.get("/dominios/mx/{tiene_mx}", response_model=list[schemas.DominioSalida])
def get_domain_mx(tiene_mx: bool, db=Depends(get_db)):
    logger.debug(f"GET /dominio/mx/{tiene_mx} llamada")
    dominios = crud.lista_dom_mx(db, tiene_mx)
    return dominios # Devuelve una lista con los dominios en el formato definido en schemas.DominioSalida
