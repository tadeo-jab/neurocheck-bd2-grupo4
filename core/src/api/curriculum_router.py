from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.dependencies import get_curriculum_service
from src.service.curriculum_service import CurriculumService

router = APIRouter(prefix="/curriculum", tags=["curriculum"])

# ── Schemas ─────────────────────────────────────────────

class EnrollBody(BaseModel):
    id_estudiante: str
    id_materia: str

# ── Endpoints ───────────────────────────────────────────

@router.get("/enrollments/{id_estudiante}")
def get_enrollments(id_estudiante: str,
                    service: CurriculumService = Depends(get_curriculum_service)):
    return service.get_student_enrollments(id_estudiante)


@router.get("/tree/{id_estudiante}")
def get_tree( id_estudiante: str,
             service: CurriculumService = Depends(get_curriculum_service)):
    return service.get_curriculum_tree(id_estudiante)


@router.get("/subject/{id_materia}/tree/{id_estudiante}")
def get_subject_tree(id_materia: str, id_estudiante: str,
                     service: CurriculumService = Depends(get_curriculum_service)):
    return service.get_subject_tree(id_estudiante, id_materia)


@router.post("/enroll")
def enroll(body: EnrollBody,
           service: CurriculumService = Depends(get_curriculum_service)):
    service.enroll_student(body.id_estudiante, body.id_materia)
    return {"ok": True}
