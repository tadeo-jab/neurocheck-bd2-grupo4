"""
Analytics Router — Consultas 1 a 4 del diseño conceptual (Etapa 1).

GET /api/analytics/student/{id}/profile        ← Consulta 1
GET /api/analytics/student/{id}/sessions       ← Consulta 2
GET /api/analytics/student/{id}/difficulty     ← Consulta 3
GET /api/analytics/student/{id}/recent-events  ← Consulta 4
"""

from fastapi import APIRouter, Depends, Query

from src.dependencies import get_analytics_service
from src.service.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/student/{id_estudiante}/profile")
def get_perfil_completo(
    id_estudiante: str,
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Consulta 1 — Recuperar perfil completo del estudiante.
    Combina datos de MongoDB (auth, métricas) con Neo4j (matrículas, progreso).
    """
    return svc.get_perfil_completo(id_estudiante)


@router.get("/student/{id_estudiante}/sessions")
def get_historial_sesiones(
    id_estudiante: str,
    limite: int = Query(default=50, ge=1, le=200),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Consulta 2 — Obtener historial de sesiones de estudio.
    Devuelve sesiones ordenadas cronológicamente con métricas por sesión.
    """
    return svc.get_historial_sesiones(id_estudiante, limite=limite)


@router.get("/student/{id_estudiante}/difficulty")
def detectar_dificultades(
    id_estudiante: str,
    tema: str | None = Query(default=None, description="ID de materia (opcional)"),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Consulta 3 — Detectar posibles dificultades de aprendizaje.
    Analiza porcentaje de aciertos, abandonos, intentos y tiempo de resolución.
    """
    return svc.detectar_dificultades(id_estudiante, tema=tema)


@router.get("/student/{id_estudiante}/recent-events")
def get_eventos_recientes(
    id_estudiante: str,
    limite: int = Query(default=20, ge=1, le=100),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Consulta 4 — Obtener eventos recientes de un estudiante.
    Devuelve las últimas interacciones educativas en orden cronológico.
    """
    return svc.get_eventos_recientes(id_estudiante, limite=limite)
