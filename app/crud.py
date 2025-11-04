import models, schemas
import logging
import math
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select
from datetime import datetime, timezone

logger = logging.getLogger("dominio")

# Función privada que comprueba si existe una fuente de reputacion asociada a un dominio. Si existe la actualiza
def _gestiona_fuentes_reputacion(dominio: models.Dominio, value: list[dict]) -> list[dict]:
	logger.debug(f"[+] Agregando reputacion")
	reputacion_actual = dominio.fuentes_reputacion or [] # Obtenemos la reputacion que está almecenada para el dominio
	# Iteramos por cada nueva reputacion
	for nueva_reputacion in value:
		# Obtenemos la clave-valor de cada nueva reputacion
		for fuente, score in nueva_reputacion.items():
			existe_fuente = False
			# Iteramos por la lisat de la reputacion actual y obtenemos el indice por si tenemos que cambiar el valor de una fuente
			for i, rep_existente in enumerate(reputacion_actual):
				if fuente in rep_existente:
					logger.debug(f"[+] Existe la fuente '{fuente}'")
					reputacion_actual[i] = {fuente: score}
					existe_fuente = True
					logger.debug(f"[+] Actualizada la fuente de reputacion '{fuente}' con un score de {score}")
					break
			if not existe_fuente:
				reputacion_actual.append({fuente: score})
				logger.debug(f"[+] Agregada una nueva fuente de reputacion '{fuente}': {score}")
	
	return reputacion_actual

# Funcion privada para calcular el score en base a los scores de las distintas fuentes de reputación
def _calcula_score(fuentes_reputacion: list[dict]) -> int:
	total_score = 0
	for fuente in fuentes_reputacion:
		for _, score in fuente.items():
			total_score += score
	# Redondeamos al alza. De no hacerlo asi un score de 0.5 se quedaría en 0 y seria un falso negativo
	total_score = math.ceil(total_score/len(fuentes_reputacion)) 
	
	return total_score

# Función para crear un dominio
def crea_dominio(db:Session,
				 datos:schemas.CrearDominio,
				 ip: str,
				 mx: bool,
				 fuentes_reputacion: list[dict]
	) -> models.Dominio:

	logger.info(f"[+] Creando dominio: '{datos.nombre} con las etiquetas {datos.etiquetas}'")
	dominio = models.Dominio(**datos.model_dump())
	dominio.ip_actual = ip
	dominio.tiene_mx = mx
	dominio.fuentes_reputacion = _gestiona_fuentes_reputacion(dominio, fuentes_reputacion)
	# Llamamos a la funcion privada que calcula la media de los score de todas las fuente de reputacion
	dominio.score = _calcula_score(dominio.fuentes_reputacion)
	db.add(dominio)
	db.commit()
	db.refresh(dominio)
	logger.info(f"[+] Dominio '{dominio.nombre}' creado.")
	
	return dominio

# Función para listar todos los dominios que hay registrados
def lista_dominios(db: Session) -> models.Dominio:
	logger.debug("[+] Mostrando todos los dominios")
	dominios = db.execute(select(models.Dominio).order_by(models.Dominio.nombre.asc())).scalars().all()
	if len(dominios) > 0:
		logger.info(f"[+] Se han encontrado {len(dominios)} dominios registrados")
	else:
		logger.info(f"[-] No se han encontrado dominios registrados")
	
	return dominios

# Función para obtener un dominio registrado
def get_dominio(db: Session, nombre: str) -> models.Dominio | None:
	logger.debug(f"[+] Buscando el dominio {nombre}")
	dominio = db.get(models.Dominio, nombre)
	if dominio:
		logger.info(f"[+] Dominio '{nombre}' encontrado")
		return dominio
	else:
		logger.warning(f"[-] Dominio '{nombre}' no encontrado")
		return None

# Función para actualizar un dominio registrado
def update_dominio(db: Session,
				   nombre: str,
				   datos: schemas.ActualizaDominio,
				   ip: str,
				   mx: bool
	)-> models.Dominio | None:

	logger.info(f"[+] Se va a actualizar el dominio '{nombre}'")
	dominio = db.get(models.Dominio, nombre)
	dominio.ip_actual = ip
	dominio.tiene_mx = mx
	
	for field, value in datos.model_dump(exclude_unset=True).items():
		# Se van a validar indivualmente cada dato que se va a actualizar
		if field == "fuentes_reputacion" and value is not None:
			dominio.fuentes_reputacion = _gestiona_fuentes_reputacion(dominio, value)
			flag_modified(dominio, "fuentes_reputacion") # Indica a SQLAlchemy que ese valor ha cambiado sino no detecta el cambio
		
		if field == "etiquetas" and value is not None:
			etiquetas_actuales = dominio.etiquetas or []
			dominio.etiquetas = list(set(etiquetas_actuales + value)) # Con el set no permitimos valores duplicados
			flag_modified(dominio, "etiquetas") # Indica a SQLAlchemy que ese valor ha cambiado sino no detecta el cambio
			logger.debug(f"[+] Actualizadas las etiquetas con '{value}'")

		if field == "estado_dominio" and value is not None:
			dominio.estado_dominio = value
			flag_modified(dominio, "etiquetas") # Indica a SQLAlchemy que ese valor ha cambiado sino no detecta el cambio
			logger.debug(f"[+] Actualizado el estado del dominio con el valor '{value}'")
	# Llamamos a la funcion privada que calcula la media de los score de todas las fuente de reputacion
	dominio.score = _calcula_score(dominio.fuentes_reputacion)
	dominio.modificado_el = datetime.now(timezone.utc).replace(microsecond=0) # Cambiamos la fecha de actualizacion
	db.commit()
	db.refresh(dominio)
	logger.info(f"[+] Actualizado el dominio '{dominio.nombre}'")
	
	return dominio

# Función para eliminar un dominio
def delete_dominio(db: Session, nombre: str) -> bool:
	logger.debug(f"[+] Se va a eliminar el dominio '{nombre}'")
	dominio = db.get(models.Dominio, nombre)
	if not dominio:
		logger.warning(f"[-] No existe el dominio '{nombre}'")
		return False
	logger.info(f"[+] Borrado el dominio '{dominio.nombre}'")
	db.delete(dominio)
	db.commit()
	return True

# Función para mostrar los dominios que tienen un estado determinado
def lista_dom_estado(db: Session, estado: models.EstadoDominio) -> list[models.Dominio] | None:
	logger.debug(f"[+] Se van a buscar los dominios cuyo estado es '{estado}'")
	dominios = db.execute(select(models.Dominio).where(models.Dominio.estado_dominio == estado)).scalars().all()
	if not dominios:
		logger.info(f"[-] No existen dominios cuyo estado es '{estado}'")
		return dominios
	else:
		logger.info(f"[+] Se muestran {len(dominios)} dominio/s cuyo/s estado es '{estado}'")
	return dominios

# Función para mostrar los dominios que tienen menos del score determinado
def lista_dom_score(db: Session, score: int) -> list[models.Dominio] | None:
	logger.debug(f"[+] Se van a buscar los dominios con reputacion inferior a {score}")
	dominios = db.execute(select(models.Dominio).where(models.Dominio.score < score)).scalars().all()
	if not dominios:
		logger.info(f"[-] No existen dominios con una reputación inferior a {score}")
		return dominios
	else:
		logger.info(f"[+] Se muestran {len(dominios)} dominios con una reputación inferior a {score}")
	return dominios

# Función para mostrar los dominios que tienen menos del score determinado
def lista_dom_mx(db: Session, mx: bool) -> list[models.Dominio] | None:
	if  mx:
		logger.debug(f"[+] Se van a buscar los dominios que tienen servidor de correo activo")
	else:
		logger.debug(f"[+] Se van a buscar los dominios que no tienen servidor de correo activo")
	dominios = db.execute(select(models.Dominio).where(models.Dominio.tiene_mx == mx)).scalars().all()
	if not dominios:
		if mx:
			logger.info(f"[-] No existen dominios con servidor de correo activo")
		else:
			logger.info(f"[-] No existen dominios sin servidor de correo activo")
		return None
	else:
		if mx:
			logger.info(f"[+] Se muestran {len(dominios)} dominios con servidor de correo activo")
		else:
			logger.info(f"[+] Se muestran {len(dominios)} dominios sin servidor de correo activo")
	
	return dominios

