import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import logging
from models import EstadoDominio

logger = logging.getLogger("dominio")

# Clase para validar los datos cuando creamos un dominio
class CrearDominio(BaseModel):
    # El dominio no puede tener menos de 3 ni mas de 50 letras
    nombre: str = Field(..., min_length=3, max_length=50)
    # Las etiquetas deben ser una lista de strings
    etiquetas: list[str] = Field(default_factory=list)
    # Vamos a definir con una regla de regex como debe ser el dominio
    @field_validator("nombre")
    def valida_dominio(cls, nombre):
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        # Si no cumple el patrón lanzamos usa excepción
        if not re.match(pattern, nombre):
            logger.info(f"El usuario ha introducido el dominio '{nombre}' que no cumple el patron ")
            raise ValueError("Formato de dominio inválido")
        return nombre.lower()
    # definimos como deben ser los datos que el usuario envia como etiquetas
    @field_validator("etiquetas", mode="before")
    def valida_etiquetas(cls, etiquetas):
        # Si los datos no son de tipo list se lanza una excepcion
        if not isinstance(etiquetas, list):
            logger.info(f"El usuario ha introducido etiquetas '{etiquetas}' en un formato incorrecto")
            raise ValueError("Las etiquetas deben estar en formato lista. ['etiqueta1', 'etiqueta2', ...]")
        return etiquetas

# Clase para validar los datos que el usuario envia para actualizar un dominio
class ActualizaDominio(BaseModel):
    # Se va a poder actualizar las fuentes de reputacion, las etiquetas y el estado del dominio
    # siendo todas ellas opcionales
    fuentes_reputacion: list[dict]| None = None
    etiquetas: list[str] | None = None
    estado_dominio: EstadoDominio | None = None 

    # Vamos a controlar de forma unitaria los datos que el usuario envia
    # Esta comprobación se realiza antes convertirlo al modelo de Dominio
    @field_validator("fuentes_reputacion", mode="before")
    def valida_reputacion(cls, fuentes_reputacion):
        if fuentes_reputacion is None:
            return None
        # Verificamos que la fuente de reputacion sea de tipo lista, sino lanzamos excepcion
        if not isinstance(fuentes_reputacion, list):
            logger.info(f"El usuario ha introducido la reputación {fuentes_reputacion} en un formato incorrecto")
            raise ValueError("La reputacion debe ser una lista de diccionario/s. Ejemplo: [{'fuente': valor}]")
        # Validamos cada fuente de reputacion sea un diccionario, si no lanzamos excepcion
        for dato in fuentes_reputacion:
            if not isinstance (dato, dict):
                logger.info(f"El usuario ha introducido una fuente de reputación {dato} en un formato incorrecto")
                raise ValueError("La reputacion debe estar en formato diccionario. {'fuente': valor}")
            # Si la fuente es un diccionario ahora validamos que en par clave/valor, valor sea de tipo Entero
            # si no lo es, lanzamos excepcion
            for _, valor in dato.items():
                if not isinstance(valor, int):
                    logger.info(f"El usuario ha introducido el score {valor} de una fuente de reputación en un formato incorrecto")
                    raise ValueError(f"El valor {valor} debe ser de tipo entero")
        return fuentes_reputacion

    # Vamos a controlar que las etiquetas sean de tipo lista, si no lanzamos excepcion
    @field_validator("etiquetas", mode="before")
    def valida_etiquetas(cls, etiquetas):
        if etiquetas is None:
            return None
        if not isinstance(etiquetas, list):
            logger.info(f"El usuario ha introducido etiquetas '{etiquetas}' en un formato incorrecto")
            raise ValueError("Las etiquetas deben estar en formato lista. ['etiqueta1', 'etiqueta2', ...]")
        return etiquetas
    
    # Vamos a verificar que el estado dominio es del tipo definido como EstadoDominio en el archivo models.py
    @field_validator("estado_dominio", mode="before")
    def valida_estado_dominio(cls, estado_dominio):
        # Verificamos que es del tipo EstadoDominio
        if not isinstance(estado_dominio, EstadoDominio):
            # Guardamos los estados de dominio válidos
            valores_validos = [valor.value for valor in EstadoDominio]
            # Verificamos qeu el estado pasado por el usuario corresponde con alguno de lso permitidos, sino lanzamos excepcion
            if estado_dominio not in valores_validos:
                logger.info(f"El usuario ha introducido un estado {estado_dominio} no permitido")
                raise ValueError(f"El estado {estado_dominio} no está permitido. Elige uno entre los siguientes {valores_validos}")
            return estado_dominio

# Creamos esta clase para dar formato a como se devuelven los dominios
# Sin esta clase los campos aparecen desordenados
class DominioSalida(BaseModel):
    # Se declaran los campos que se van a devolver
    nombre: str
    ip_actual: str | None
    tiene_mx: bool | None
    estado_dominio: str | None
    fuentes_reputacion: list[dict] | None
    score: int | None
    etiquetas: list[str] | None
    creado_el: datetime
    modificado_el: datetime
    
    model_config = {
        "from_attributes": True # Indicamos que los datos se coloquen por el atributo
    }