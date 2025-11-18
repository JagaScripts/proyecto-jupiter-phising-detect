import enum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Column, Enum, BOOLEAN, JSON, DATETIME, Integer, event
from datetime import datetime, timezone

# Declaramos una clase base
class DecBase(DeclarativeBase):
    pass

# Definimos los estados de dominio posibles. Son de tipo Enum
class EstadoDominio(enum.Enum):
    LIMPIO = "Limpio"
    SOSPECHOSO = "Sospechoso"
    MALICIOSO = "Malicioso"
    DESCONOCIDO = "Desconocido" 

# Creamos la clase Dominio que se usará para la base de datos
class Dominio(DecBase):
    __tablename__ = "dominios"
    # Definimos los campos que va a tener y el formato
    # No creamos un ID porque se va a tomar como referencia el dominio y será unico
    # Si aumentasen las tablas y la complejidad sería mejor usar IDs en cada tabla
    nombre = Column(String(50), primary_key=True, nullable=False)
    ip_actual = Column(String(20))
    estado_dominio = Column(Enum(EstadoDominio), default=EstadoDominio.DESCONOCIDO)
    tiene_mx = Column(BOOLEAN, default=False)
    etiquetas = Column(JSON, default=list) # Este campo seran listas y por eso se declaran de tipo JSON
    fuentes_reputacion = Column(JSON, default=list) # Este campo seran listas de diccionarios también se declaran de tipo JSON
    score = Column(Integer, default=0)
    creado_el = Column(DATETIME)
    modificado_el = Column(DATETIME)

# Debido a que en ocasiones la fecha de registro es anterior a la fecha de creación y es un problema de 
# sqlalchemy, se van a usar eventos para sincronizar las fechas

# Este evento salta antes de insertar un dato en la BD
@event.listens_for(Dominio, "before_insert")
def before_insert(_, __, target):
    ahora = datetime.now(timezone.utc).replace(microsecond=0)
    # Aquí nos aseguramos que tanto creacion como actualizacion tienen la misma fecha/hora
    target.creado_el = ahora
    target.modificado_el = ahora

# Este evento salta antes de actualizar un dato en la BD
@event.listens_for(Dominio, "before_update")
def before_update(_, __, target):
    # Solo modificamo el dato de fecha de modificación
    target.modificado_el = datetime.now(timezone.utc).replace(microsecond=0)

