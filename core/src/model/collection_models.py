from datetime import datetime
from pydantic import BaseModel


class SesionEstudiante(BaseModel):
    id: str
    fecha_ini: datetime
    fecha_fin: datetime | None = None
    intentos_estudio: list[str] = []
    intentos_actividades: list[str] = []
    fatiga_estimada: float


class Estudiante(BaseModel):
    id: str
    estilo_preferido: str
    nombre: str
    email: str
    password_hash: str



class IntentoEstudio(BaseModel):
    id: str
    tiempo: datetime
    pausas: int
    duracion_total: int
    terminado: bool
    id_recurso: str
    id_materia: str
    id_estudiante: str
    id_sesion: str


class IntentoActividad(BaseModel):
    id: str
    tiempo: datetime
    duracion_total: int
    pausas: int
    aciertos: int
    errores: int
    puntaje: float
    aprobado: bool
    id_actividad: str
    id_materia: str
    id_estudiante: str
    id_sesion: str


class EventoInteraccion(BaseModel):
    id: str
    id_usuario: str
    id_sesion: str
    tipo_evento: str
    timestamp: datetime


class Recurso(BaseModel):
    id: str
    nombre: str
    tipo: str  # "pdf", "video", etc.
    recurso_bin: bytes | None = None  # bson.Binary en MongoDB (< 16 MB); para archivos mas grandes usar GridFS
    mime_type: str  # ej. "application/pdf", "video/mp4"
    nombre_archivo: str
    link_aux: str | None = None


class Actividad(BaseModel):
    id: str
    nombre: str
    tipo: str
    preguntas: list[dict] = []




