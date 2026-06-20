from fastapi import APIRouter, Depends

from src.dependencies import get_admin_service
from src.service.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/sessions/{id_estudiante}")
def get_sessions(id_estudiante: str,
                 service: AdminService = Depends(get_admin_service)):
    return service.get_sesiones_by_id(id_estudiante)


@router.get("/attempts/{id_sesion}")
def get_attempts(id_sesion: str,
                 service: AdminService = Depends(get_admin_service)):
    return service.get_intentos_by_sesion(id_sesion)
