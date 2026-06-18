from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.dependencies import get_mates_service
from src.service.mates_service import MatesService

router = APIRouter(prefix="/mates", tags=["mates"])

# ── Schemas ─────────────────────────────────────────────

class MateRequestBody(BaseModel):
    student_id_a: str
    student_id_b: str

# ── Endpoints ───────────────────────────────────────────

@router.get("/{id_estudiante}")
def get_mates(id_estudiante: str,
              service: MatesService = Depends(get_mates_service)):
    return service.get_student_mates(id_estudiante)


@router.get("/{id_estudiante}/suggested")
def suggested(id_estudiante: str,
              service: MatesService = Depends(get_mates_service)):
    return service.suggested_mates(id_estudiante)


@router.post("/request")
def send_request(body: MateRequestBody,
                 service: MatesService = Depends(get_mates_service)):
    service.send_mate_request(body.student_id_a, body.student_id_b)
    return {"ok": True}
