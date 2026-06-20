from fastapi import APIRouter, Depends, Header
from fastapi.responses import Response
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
    terminado: bool
    auto_percepcion: int | None = None
    respuestas: dict[str, int] | None = None

# ── Endpoints ───────────────────────────────────────────

@router.get("/course/{id_materia}/{id_estudiante}")
def get_course(id_materia: str, id_estudiante: str,
               service: StudyService = Depends(get_study_service)):
    camino, progress = service.get_subject_course(id_estudiante, id_materia)
    return {"camino": camino, "progreso": progress}


@router.get("/resource/{id_recurso}/file")
def get_resource_file(id_recurso: str,
                      service: StudyService = Depends(get_study_service)):
    recurso = service.get_resource(id_recurso)
    return Response(
        content=recurso.recurso_bin,
        media_type=recurso.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{recurso.nombre_archivo}"'},
    )


@router.get("/activity/{id_actividad}")
def get_activity(id_actividad: str,
                 service: StudyService = Depends(get_study_service)):
    return service.get_activity(id_actividad)


@router.post("/attempt/start")
def start(body: StartAttemptBody,
          authorization: str = Header(),
          service: StudyService = Depends(get_study_service)):
    token = authorization.removeprefix("Bearer ")
    return service.start_attempt(token, body.id_materia, body.id_contenido,
                                 body.tipo_contenido, body.duracion_total)


@router.put("/attempt/{intento_id}/pause")
def pause(intento_id: str, service: StudyService = Depends(get_study_service)):
    return {"restante": service.pause_attempt(intento_id)}


@router.put("/attempt/{intento_id}/resume")
def resume(intento_id: str, service: StudyService = Depends(get_study_service)):
    return {"restante": service.resume_attempt(intento_id)}


@router.post("/attempt/{intento_id}/close")
def close(intento_id: str, body: CloseAttemptBody,
          service: StudyService = Depends(get_study_service)):
    result = service.close_attempt(intento_id, **body.model_dump(exclude_none=True))
    return {"ok": True, "warning": result["warning"], "precuela": result["precuela"],
            "aprobado": result["aprobado"], "puntaje": result["puntaje"],
            "curso_aprobado": result["curso_aprobado"]}
