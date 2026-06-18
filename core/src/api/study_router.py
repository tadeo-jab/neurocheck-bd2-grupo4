from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from src.dependencies import get_study_service
from src.service.study_service import StudyService

router = APIRouter(prefix="/study", tags=["study"])

# ── Schemas ─────────────────────────────────────────────

class StartAttemptBody(BaseModel):
    id_materia: str
    id_contenido: str
    tipo_contenido: str
    duracion_total: int = 0

class CloseAttemptBody(BaseModel):
    terminado: bool = True
    auto_percepcion: int | None = None
    aciertos: int | None = None
    errores: int | None = None
    puntaje: float | None = None
    aprobado: bool | None = None

# ── Endpoints ───────────────────────────────────────────

@router.get("/subject/{id_materia}/course")
def get_course(id_materia: str, id_estudiante: str,
               service: StudyService = Depends(get_study_service)):
    return service.get_subject_course(id_estudiante, id_materia)


@router.post("/attempt/start")
def start(body: StartAttemptBody,
          authorization: str = Header(),
          service: StudyService = Depends(get_study_service)):
    token = authorization.removeprefix("Bearer ")
    return service.start_attempt(token, body.id_materia, body.id_contenido,
                                 body.tipo_contenido, body.duracion_total)


@router.post("/attempt/{intento_id}/pause")
def pause(intento_id: str, service: StudyService = Depends(get_study_service)):
    return {"restante": service.pause_attempt(intento_id)}


@router.post("/attempt/{intento_id}/resume")
def resume(intento_id: str, service: StudyService = Depends(get_study_service)):
    return {"restante": service.resume_attempt(intento_id)}


@router.post("/attempt/{intento_id}/close")
def close(intento_id: str, body: CloseAttemptBody,
          service: StudyService = Depends(get_study_service)):
    service.close_attempt(intento_id, **body.model_dump(exclude_none=True))
    return {"ok": True}
