from datetime import datetime
from pydantic import BaseModel


class Estudiante(BaseModel):
    id: str
    nombre: str
    estilo_preferido: str


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
    estilo_aprendizaje_opt: str


class Actividad(BaseModel):
    id: str
    nombre: str
    descripcion: str
    tipo: str
    dificultad: float
    duracion_estimada: int
    puntaje_maximo: float
