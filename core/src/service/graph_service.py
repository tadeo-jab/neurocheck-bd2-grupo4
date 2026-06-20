"""
GraphService — implementa los 3 patrones de consulta Neo4j declarados en Etapa 1.

Consulta 5: Encontrar prerrequisitos de un tema
Consulta 6: Calcular ruta óptima de aprendizaje
Consulta 7: Buscar caminos alternativos de aprendizaje
"""

from src.db.neo4j import Neo4jService
from src.repository.neo4j.materia_repository import MateriaRepository
from src.repository.neo4j.materia_estudiante_repository import MateriaEstudianteRepository


class GraphService:

    def __init__(self, neo4j: Neo4jService):
        self._materia_repo = MateriaRepository(neo4j)
        self._mat_est_repo = MateriaEstudianteRepository(neo4j)

    # ── Consulta 5 — Prerrequisitos de un tema ─────────────

    def get_prerrequisitos(self, id_materia: str) -> dict:
        """
        Identifica todos los conocimientos previos (directos e indirectos)
        necesarios para abordar la materia solicitada.
        """
        materia = self._materia_repo.get_materia(id_materia)
        if not materia:
            raise ValueError(f"Materia {id_materia} no encontrada.")

        prereqs = self._materia_repo.get_all_prerequisites(id_materia)

        return {
            "materia": {
                "id": materia.id,
                "nombre": materia.nombre,
                "nivel_dificultad": materia.nivel_dificultad,
            },
            "total_prerrequisitos": len(prereqs),
            "prerrequisitos": [
                {
                    "id": p["id"],
                    "nombre": p["nombre"],
                    "nivel_dificultad": p.get("nivel_dificultad"),
                    "profundidad": p["profundidad"],
                }
                for p in prereqs
            ],
        }

    # ── Consulta 6 — Ruta óptima de aprendizaje ────────────

    def get_ruta_optima(self, id_estudiante: str, id_materia_objetivo: str) -> dict:
        """
        Determina la mejor secuencia pedagógica para que el estudiante
        llegue a la materia objetivo, considerando lo que ya completó.
        """
        materia = self._materia_repo.get_materia(id_materia_objetivo)
        if not materia:
            raise ValueError(f"Materia {id_materia_objetivo} no encontrada.")

        ruta = self._materia_repo.get_optimal_learning_path(
            id_estudiante, id_materia_objetivo
        )

        return {
            "id_estudiante": id_estudiante,
            "objetivo": {
                "id": materia.id,
                "nombre": materia.nombre,
            },
            "total_pasos": len(ruta),
            "ruta_sugerida": [
                {
                    "orden": idx + 1,
                    "id": m["id"],
                    "nombre": m["nombre"],
                    "nivel_dificultad": m.get("nivel_dificultad"),
                    "tiempo_estimado_horas": m.get("tiempo_estimado"),
                    "distancia_al_objetivo": m["distancia_al_objetivo"],
                }
                for idx, m in enumerate(ruta)
            ],
        }

    # ── Consulta 7 — Caminos alternativos ──────────────────

    def get_caminos_alternativos(self, id_materia: str) -> dict:
        """
        Encuentra rutas educativas alternativas ante dificultades de aprendizaje.
        Útil cuando el estudiante tiene bajo rendimiento en la materia actual.
        """
        materia = self._materia_repo.get_materia(id_materia)
        if not materia:
            raise ValueError(f"Materia {id_materia} no encontrada.")

        alternativas = self._materia_repo.get_alternative_paths(id_materia)

        return {
            "materia_conflictiva": {
                "id": materia.id,
                "nombre": materia.nombre,
                "nivel_dificultad": materia.nivel_dificultad,
            },
            "total_alternativas": len(alternativas),
            "caminos_alternativos": [
                {
                    "id": a["id"],
                    "nombre": a["nombre"],
                    "nivel_dificultad": a.get("nivel_dificultad"),
                    "costo_adicional": a.get("costo_adicional"),
                    "estilo_favorecido": a.get("estilo_favorecido"),
                }
                for a in alternativas
            ],
            "recomendacion": (
                "Se encontraron caminos alternativos. "
                "Considerar cambiar de ruta según el estilo de aprendizaje del estudiante."
                if alternativas else
                "No hay caminos alternativos registrados para esta materia."
            ),
        }
