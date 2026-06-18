from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Estudiante(BaseModel):
    id: str
    nombre: str
    estilo_preferido: Literal["visual", "auditivo", "kinestésico", "textual"]


class Materia(BaseModel):
    id: str
    nombre: str
    descripcion: str
    nivel_dificultad: float
    tiempo_estimado: int
    frecuencia_uso: str


class Recurso(BaseModel):
    id: str
    tipo: str
    duracion_estimada: int
    carga_cognitiva: float
    estilo_aprendizaje_opt: Literal["visual", "auditivo", "kinestésico", "textual"]


class Actividad(BaseModel):
    id: str
    nombre: str
    descripcion: str
    tipo: str
    dificultad: float
    duracion_estimada: int
    puntaje_maximo: float
