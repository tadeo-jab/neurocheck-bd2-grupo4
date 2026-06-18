from datetime import datetime

from pyparsing import Optional, Literal
from pydantic import BaseModel


class Estudiante(BaseModel):
    id: str
    estilo_preferido: Literal["visual", "auditivo", "kinestésico", "textual"]
    nombre: str
    email: str
    password_hash: str



class Intento(BaseModel):
    id: str
    estudiante: Estudiante
    id_sesion: str
    id_materia: str
    id_contenido: str
    tipo_contenido: Literal["recurso", "actividad"]
    inicio: datetime
    
    fin: datetime | None = None
    duracion_segundos: int
    pausas: int
    duracion_pausa_segundos: int
    terminado: bool
    auto_percepcion: int | None = None  # 1-5
    
    # Solo para actividades
    aciertos: int | None = None
    errores: int | None = None
    puntaje: float | None = None
    aprobado: bool | None = None



class Sesion(BaseModel):
    id: str
    estudiante: Estudiante
    fecha_ini: datetime
    fecha_fin: datetime | None = None
    intentos_estudio: list[Intento] = []
    fatiga_estimada: float



class EventoInteraccion(BaseModel):
    id: str
    id_usuario: Estudiante
    sesion: Sesion
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


class Pregunta(BaseModel):
    id: str
    texto: str
    opciones: list[str]
    respuesta_correcta: int
    puntaje: float

class Actividad(BaseModel):
    id: str
    nombre: str
    tipo: str  # "quiz", "ejercicio", "proyecto"
    preguntas: list[Pregunta] = []
    dificultad: float
    puntaje_maximo: float


class CaminoAprendizaje(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    secuencia: list[dict] = [Literal["recurso", "actividad"], str] # Ej. [{"tipo": "recurso", "id": "rec123"}, {"tipo": "actividad", "id": "act456"}]


class Curriculum(BaseModel):
    id_materia: str  # id_materia
    nombre: str
    tiempo_estimado_horas: int
    caminos: dict[
        Literal["visual", "auditivo", "kinestesico", "escrito"],
        CaminoAprendizaje
    ]




