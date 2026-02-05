import enum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Column, Enum, BOOLEAN, JSON, DATETIME, Integer, event
from datetime import datetime, timezone


class DecBase(DeclarativeBase):
    pass


class EstadoDominio(enum.Enum):
    LIMPIO = "Limpio"
    SOSPECHOSO = "Sospechoso"
    MALICIOSO = "Malicioso"
    DESCONOCIDO = "Desconocido"


class Dominio(DecBase):
    __tablename__ = "dominios"
    
    nombre = Column(String(50), primary_key=True, nullable=False)
    ip_actual = Column(String(20))
    estado_dominio = Column(Enum(EstadoDominio), default=EstadoDominio.DESCONOCIDO)
    tiene_mx = Column(BOOLEAN, default=False)
    etiquetas = Column(JSON, default=list)
    fuentes_reputacion = Column(JSON, default=list)
    score = Column(Integer, default=0)
    creado_el = Column(DATETIME)
    modificado_el = Column(DATETIME)


@event.listens_for(Dominio, "before_insert")
def before_insert(_, __, target):
    ahora = datetime.now(timezone.utc).replace(microsecond=0)
    target.creado_el = ahora
    target.modificado_el = ahora


@event.listens_for(Dominio, "before_update")
def before_update(_, __, target):
    target.modificado_el = datetime.now(timezone.utc).replace(microsecond=0)
