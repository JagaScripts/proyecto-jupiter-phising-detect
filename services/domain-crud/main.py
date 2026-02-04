import logging
import sys
sys.path.append('/app/shared')

from fastapi import FastAPI, HTTPException, Depends
from database import SessionLocal, engine, get_db
from models import DecBase, EstadoDominio
import crud
from shared.schemas import CrearDominio, ActualizaDominio, DominioSalida

app = FastAPI(title="Domain CRUD Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
def startup_event():
    DecBase.metadata.create_all(bind=engine)
    logger.info("Base de datos inicializada")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "domain-crud"}


@app.post("/dominios", response_model=DominioSalida)
def create_domain(datos: CrearDominio, db=Depends(get_db)):
    """Crear dominio (sin consultas externas)"""
    logger.debug(f"POST /dominios datos: {datos}")
    dominio = crud.get_dominio(db, datos.nombre)
    if dominio:
        logger.info(f"El dominio {datos.nombre} ya existe")
        raise HTTPException(status_code=400, detail=f"El dominio {datos.nombre} ya existe.")
    
    # Crear con datos vacíos (serán completados por el gateway)
    dominio = crud.crea_dominio(db, datos.nombre, "", False, [], datos.etiquetas)
    return dominio


@app.get("/dominios", response_model=list[DominioSalida])
def list_domains(db=Depends(get_db)):
    """Listar todos los dominios"""
    logger.debug("GET /dominios llamada")
    dominios = crud.lista_dominios(db)
    return dominios


@app.get("/dominios/{nombre_dominio}", response_model=DominioSalida)
def get_domain(nombre_dominio: str, db=Depends(get_db)):
    """Obtener un dominio específico"""
    logger.debug(f"GET /dominios/{nombre_dominio} llamada")
    dominio = crud.get_dominio(db, nombre_dominio)
    if not dominio:
        raise HTTPException(status_code=404, detail=f"Dominio '{nombre_dominio}' no encontrado")
    return dominio


@app.patch("/dominios/{nombre_dominio}", response_model=DominioSalida)
def update_domain(nombre_dominio: str, datos: ActualizaDominio, db=Depends(get_db)):
    """Actualizar dominio (sin consultas externas)"""
    logger.debug(f"PATCH /dominios/{nombre_dominio} datos: {datos} llamada")
    dominio = crud.get_dominio(db, nombre_dominio)
    if not dominio:
        logger.info(f"El dominio {nombre_dominio} no existe")
        raise HTTPException(status_code=404, detail=f"El dominio {nombre_dominio} no existe")
    
    # Actualizar con datos vacíos (serán completados por el gateway)
    dominio = crud.update_dominio(
        db, nombre_dominio, "", False,
        fuentes_reputacion=datos.fuentes_reputacion,
        etiquetas=datos.etiquetas,
        estado_dominio=datos.estado_dominio
    )
    if not dominio:
        raise HTTPException(status_code=400, detail=f"Fallo al actualizar el dominio '{nombre_dominio}'")
    return dominio


@app.patch("/dominios/{nombre_dominio}/complete")
def complete_domain_data(nombre_dominio: str, ip: str, tiene_mx: bool, fuentes_rep: list[dict], db=Depends(get_db)):
    """Completar datos del dominio desde servicios externos (usado por gateway)"""
    dominio = crud.get_dominio(db, nombre_dominio)
    if not dominio:
        raise HTTPException(status_code=404, detail=f"Dominio '{nombre_dominio}' no encontrado")
    
    dominio = crud.update_dominio(db, nombre_dominio, ip, tiene_mx, fuentes_reputacion=fuentes_rep)
    return dominio


@app.delete("/dominios/{nombre_dominio}")
def delete_domain(nombre_dominio: str, db=Depends(get_db)):
    """Eliminar dominio"""
    logger.debug(f"DELETE /dominios/{nombre_dominio} llamada")
    if not crud.delete_dominio(db, nombre_dominio):
        raise HTTPException(status_code=404, detail=f"Dominio '{nombre_dominio}' no encontrado")
    return {"message": f"Dominio '{nombre_dominio}' borrado"}


@app.get("/dominios/filtro/estado/{estado}", response_model=list[DominioSalida])
def get_domain_state(estado: str, db=Depends(get_db)):
    """Filtrar dominios por estado"""
    try:
        estado_enum = EstadoDominio(estado)
    except ValueError:
        valores_validos = [valor.value for valor in EstadoDominio]
        raise HTTPException(
            status_code=422,
            detail=f"El estado '{estado}' no está permitido. Elige uno entre {valores_validos}"
        )
    dominios = crud.lista_dom_estado(db, estado_enum)
    return dominios


@app.get("/dominios/filtro/reputacion/{score}", response_model=list[DominioSalida])
def get_domain_score(score: int, db=Depends(get_db)):
    """Filtrar dominios por score menor al indicado"""
    logger.debug(f"GET /dominios/filtro/reputacion/{score} llamada")
    dominios = crud.lista_dom_score(db, score)
    return dominios


@app.get("/dominios/filtro/mx/{tiene_mx}", response_model=list[DominioSalida])
def get_domain_mx(tiene_mx: bool, db=Depends(get_db)):
    """Filtrar dominios por disponibilidad de MX"""
    logger.debug(f"GET /dominios/filtro/mx/{tiene_mx} llamada")
    dominios = crud.lista_dom_mx(db, tiene_mx)
    return dominios


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
