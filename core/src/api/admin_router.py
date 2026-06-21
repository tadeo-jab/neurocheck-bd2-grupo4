from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.dependencies import get_admin_service
from src.service.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


class PopulateBody(BaseModel):
    estudiantes: list[dict] = []
    materias: list[dict] = []
    prerrequisitos: list[list] = []


@router.get("/sessions/{id_estudiante}")
def get_sessions(id_estudiante: str,
                 service: AdminService = Depends(get_admin_service)):
    return service.get_sesiones_by_id(id_estudiante)


@router.get("/attempts/{id_sesion}")
def get_attempts(id_sesion: str,
                 service: AdminService = Depends(get_admin_service)):
    return service.get_intentos_by_sesion(id_sesion)


@router.get("/events/{id_estudiante}")
def get_events(id_estudiante: str,
               service: AdminService = Depends(get_admin_service)):
    return service.get_events(id_estudiante)


@router.get("/passed/{id_estudiante}")
def get_passed(id_estudiante: str,
               service: AdminService = Depends(get_admin_service)):
    return service.get_passed_count(id_estudiante)


@router.post("/populate")
def populate(body: PopulateBody,
             service: AdminService = Depends(get_admin_service)):
    service.populate(body.estudiantes, body.materias, body.prerrequisitos)
    return {"ok": True}
