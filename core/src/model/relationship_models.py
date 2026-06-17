from datetime import datetime
from pydantic import BaseModel


class Requiere(BaseModel):
    peso: float
    obligatorio: bool


class Alternativa(BaseModel):
    peso_adicional: float
    estilo_favorecido: str


class Profundiza(BaseModel):
    peso_adicional: float


class Explica(BaseModel):
    cobertura: float
    relevancia: float


class Evalua(BaseModel):
    umbral_aprobacion: float


class Completo(BaseModel):
    aprobado: bool
    puntaje: float
    intentos: int


class Estudio(BaseModel):
    completado: bool
    intentos: int


class AnotadoEn(BaseModel):
    completado: bool
    fecha_inicio: datetime
    fecha_fin: datetime | None = None
    estilo_actual: str


class CompañeroDe(BaseModel):
    solicitud_aceptada: bool
    fecha_desde: datetime


class EstudioCon(BaseModel):
    id_recurso: str
    id_intento: str
    exito: bool


class EvaluadoCon(BaseModel):
    id_actividad: str
    id_intento: str
    aprobados: bool

