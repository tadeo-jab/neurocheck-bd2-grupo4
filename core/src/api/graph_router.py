"""
Graph Router — Consultas 5 a 7 del diseño conceptual (Etapa 1).

GET /api/graph/subject/{id}/prerequisites               ← Consulta 5
GET /api/graph/student/{id}/optimal-path/{subject_id}  ← Consulta 6
GET /api/graph/subject/{id}/alternatives                ← Consulta 7
"""

from fastapi import APIRouter, Depends

from src.dependencies import get_graph_service
from src.service.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/subject/{id_materia}/prerequisites")
def get_prerrequisitos(
    id_materia: str,
    svc: GraphService = Depends(get_graph_service),
):
    """
    Consulta 5 — Encontrar prerrequisitos de un tema.
    Recorre el grafo de conocimiento (Neo4j) para obtener todos los
    prerrequisitos directos e indirectos de la materia solicitada.
    """
    return svc.get_prerrequisitos(id_materia)


@router.get("/student/{id_estudiante}/optimal-path/{id_materia_objetivo}")
def get_ruta_optima(
    id_estudiante: str,
    id_materia_objetivo: str,
    svc: GraphService = Depends(get_graph_service),
):
    """
    Consulta 6 — Calcular ruta óptima de aprendizaje.
    Determina la secuencia pedagógica de materias que el estudiante debe
    completar para alcanzar el objetivo, excluyendo lo ya cursado.
    """
    return svc.get_ruta_optima(id_estudiante, id_materia_objetivo)


@router.get("/subject/{id_materia}/alternatives")
def get_caminos_alternativos(
    id_materia: str,
    svc: GraphService = Depends(get_graph_service),
):
    """
    Consulta 7 — Buscar caminos alternativos de aprendizaje.
    Devuelve rutas alternativas disponibles en el grafo cuando un
    estudiante presenta dificultades con una materia.
    """
    return svc.get_caminos_alternativos(id_materia)
