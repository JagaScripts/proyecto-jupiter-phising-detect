import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select
from datetime import datetime, timezone
from models import Dominio, EstadoDominio

logger = logging.getLogger(__name__)


def _gestiona_fuentes_reputacion(dominio: Dominio, value: list[dict]) -> list[dict]:
    logger.debug(f"Agregando reputacion")
    reputacion_actual = dominio.fuentes_reputacion or []
    
    for nueva_reputacion in value:
        for fuente, score in nueva_reputacion.items():
            existe_fuente = False
            for i, rep_existente in enumerate(reputacion_actual):
                if fuente in rep_existente:
                    logger.debug(f"Existe la fuente '{fuente}'")
                    reputacion_actual[i] = {fuente: score}
                    existe_fuente = True
                    logger.debug(f"Actualizada la fuente de reputacion '{fuente}' con un score de {score}")
                    break
            if not existe_fuente:
                reputacion_actual.append({fuente: score})
                logger.debug(f"Agregada una nueva fuente de reputacion '{fuente}': {score}")
    
    return reputacion_actual


def _calcula_score(fuentes_reputacion: list[dict]) -> int:
    if not fuentes_reputacion:
        return 0
    total_score = 0
    for fuente in fuentes_reputacion:
        for _, score in fuente.items():
            total_score += score
    total_score = math.ceil(total_score / len(fuentes_reputacion))
    return total_score


def crea_dominio(db: Session, nombre: str, ip: str, mx: bool, fuentes_reputacion: list[dict], etiquetas: list[str]) -> Dominio:
    logger.info(f"Creando dominio: '{nombre}' con etiquetas {etiquetas}")
    dominio = Dominio(nombre=nombre, etiquetas=etiquetas)
    dominio.ip_actual = ip
    dominio.tiene_mx = mx
    dominio.fuentes_reputacion = _gestiona_fuentes_reputacion(dominio, fuentes_reputacion)
    dominio.score = _calcula_score(dominio.fuentes_reputacion)
    db.add(dominio)
    db.commit()
    db.refresh(dominio)
    logger.info(f"Dominio '{dominio.nombre}' creado.")
    return dominio


def lista_dominios(db: Session) -> list[Dominio]:
    logger.debug("Mostrando todos los dominios")
    dominios = db.execute(select(Dominio).order_by(Dominio.nombre.asc())).scalars().all()
    logger.info(f"Se han encontrado {len(dominios)} dominios registrados")
    return dominios


def get_dominio(db: Session, nombre: str) -> Dominio | None:
    logger.debug(f"Buscando el dominio {nombre}")
    dominio = db.get(Dominio, nombre)
    if dominio:
        logger.info(f"Dominio '{nombre}' encontrado")
    else:
        logger.warning(f"Dominio '{nombre}' no encontrado")
    return dominio


def update_dominio(db: Session, nombre: str, ip: str, mx: bool, 
                  fuentes_reputacion: list[dict] | None = None,
                  etiquetas: list[str] | None = None,
                  estado_dominio: EstadoDominio | None = None) -> Dominio | None:
    logger.info(f"Se va a actualizar el dominio '{nombre}'")
    dominio = db.get(Dominio, nombre)
    if not dominio:
        return None
    
    dominio.ip_actual = ip
    dominio.tiene_mx = mx
    
    if fuentes_reputacion is not None:
        dominio.fuentes_reputacion = _gestiona_fuentes_reputacion(dominio, fuentes_reputacion)
        flag_modified(dominio, "fuentes_reputacion")
    
    if etiquetas is not None:
        etiquetas_actuales = dominio.etiquetas or []
        dominio.etiquetas = list(set(etiquetas_actuales + etiquetas))
        flag_modified(dominio, "etiquetas")
        logger.debug(f"Actualizadas las etiquetas con '{etiquetas}'")
    
    if estado_dominio is not None:
        dominio.estado_dominio = estado_dominio
        flag_modified(dominio, "estado_dominio")
        logger.debug(f"Actualizado el estado del dominio con el valor '{estado_dominio}'")
    
    dominio.score = _calcula_score(dominio.fuentes_reputacion)
    dominio.modificado_el = datetime.now(timezone.utc).replace(microsecond=0)
    db.commit()
    db.refresh(dominio)
    logger.info(f"Actualizado el dominio '{dominio.nombre}'")
    return dominio


def delete_dominio(db: Session, nombre: str) -> bool:
    logger.debug(f"Se va a eliminar el dominio '{nombre}'")
    dominio = db.get(Dominio, nombre)
    if not dominio:
        logger.warning(f"No existe el dominio '{nombre}'")
        return False
    logger.info(f"Borrado el dominio '{dominio.nombre}'")
    db.delete(dominio)
    db.commit()
    return True


def lista_dom_estado(db: Session, estado: EstadoDominio) -> list[Dominio]:
    logger.debug(f"Se van a buscar los dominios cuyo estado es '{estado}'")
    dominios = db.execute(select(Dominio).where(Dominio.estado_dominio == estado)).scalars().all()
    if not dominios:
        logger.info(f"No existen dominios cuyo estado es '{estado}'")
    else:
        logger.info(f"Se muestran {len(dominios)} dominio/s cuyo/s estado es '{estado}'")
    return dominios


def lista_dom_score(db: Session, score: int) -> list[Dominio]:
    logger.debug(f"Se van a buscar los dominios con reputacion inferior a {score}")
    dominios = db.execute(select(Dominio).where(Dominio.score < score)).scalars().all()
    if not dominios:
        logger.info(f"No existen dominios con una reputación inferior a {score}")
    else:
        logger.info(f"Se muestran {len(dominios)} dominios con una reputación inferior a {score}")
    return dominios


def lista_dom_mx(db: Session, mx: bool) -> list[Dominio]:
    if mx:
        logger.debug(f"Se van a buscar los dominios que tienen servidor de correo activo")
    else:
        logger.debug(f"Se van a buscar los dominios que no tienen servidor de correo activo")
    dominios = db.execute(select(Dominio).where(Dominio.tiene_mx == mx)).scalars().all()
    if not dominios:
        if mx:
            logger.info(f"No existen dominios con servidor de correo activo")
        else:
            logger.info(f"No existen dominios sin servidor de correo activo")
    else:
        if mx:
            logger.info(f"Se muestran {len(dominios)} dominios con servidor de correo activo")
        else:
            logger.info(f"Se muestran {len(dominios)} dominios sin servidor de correo activo")
    return dominios
