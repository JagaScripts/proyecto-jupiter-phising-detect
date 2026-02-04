"""Esquemas compartidos entre microservicios"""
import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class EstadoDominio(str, Enum):
    LIMPIO = "Limpio"
    SOSPECHOSO = "Sospechoso"
    MALICIOSO = "Malicioso"
    DESCONOCIDO = "Desconocido"


class CrearDominio(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50)
    etiquetas: list[str] = Field(default_factory=list)

    @field_validator("nombre")
    def valida_dominio(cls, nombre):
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(pattern, nombre):
            raise ValueError("Formato de dominio inválido")
        return nombre.lower()

    @field_validator("etiquetas", mode="before")
    def valida_etiquetas(cls, etiquetas):
        if not isinstance(etiquetas, list):
            raise ValueError("Las etiquetas deben estar en formato lista")
        return etiquetas


class ActualizaDominio(BaseModel):
    fuentes_reputacion: list[dict] | None = None
    etiquetas: list[str] | None = None
    estado_dominio: EstadoDominio | None = None

    @field_validator("fuentes_reputacion", mode="before")
    def valida_reputacion(cls, fuentes_reputacion):
        if fuentes_reputacion is None:
            return None
        if not isinstance(fuentes_reputacion, list):
            raise ValueError("La reputacion debe ser una lista de diccionarios")
        for dato in fuentes_reputacion:
            if not isinstance(dato, dict):
                raise ValueError("La reputacion debe estar en formato diccionario")
            for _, valor in dato.items():
                if not isinstance(valor, int):
                    raise ValueError(f"El valor {valor} debe ser de tipo entero")
        return fuentes_reputacion

    @field_validator("etiquetas", mode="before")
    def valida_etiquetas(cls, etiquetas):
        if etiquetas is None:
            return None
        if not isinstance(etiquetas, list):
            raise ValueError("Las etiquetas deben estar en formato lista")
        return etiquetas


class DominioSalida(BaseModel):
    nombre: str
    ip_actual: str | None
    tiene_mx: bool | None
    estado_dominio: str | None
    fuentes_reputacion: list[dict] | None
    score: int | None
    etiquetas: list[str] | None
    creado_el: datetime
    modificado_el: datetime

    model_config = {"from_attributes": True}


class DatosReputacion(BaseModel):
    """Datos de reputación de servicios externos"""
    fuentes: list[dict]


class DatosDNS(BaseModel):
    """Datos DNS del dominio"""
    ip: str | None
    tiene_mx: bool
