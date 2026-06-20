"""
demo_queries.py — Ejecuta y muestra las 7 consultas declaradas en Etapa 1.

Uso:
    cd core
    python demo_queries.py

Redirigir a archivo para evidencia PDF:
    python demo_queries.py > evidencia_consultas.txt
"""

import json
import sys
from datetime import datetime

from src.config import settings
from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.repository.mongo.evento_repository import EventoRepository
from src.repository.mongo.intento_repository import IntentoRepository
from src.repository.mongo.sesion_repository import SesionRepository
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.neo4j.materia_repository import MateriaRepository
from src.repository.neo4j.materia_estudiante_repository import MateriaEstudianteRepository
from src.service.analytics_service import AnalyticsService
from src.service.graph_service import GraphService


# ── Utilidades de display ───────────────────────────────────

def _sep(titulo: str) -> None:
    linea = "═" * 70
    print(f"\n{linea}")
    print(f"  {titulo}")
    print(linea)

def _json(obj) -> None:
    def _default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=_default))


# ── Consultas ───────────────────────────────────────────────

def run_all(mongo: MongoService, neo4j: Neo4jService) -> None:
    analytics = AnalyticsService(mongo, neo4j)
    graph     = GraphService(neo4j)

    # ── Consulta 1 ──────────────────────────────────────────
    _sep("CONSULTA 1 — Perfil completo del estudiante (MongoDB + Neo4j)")
    print("Estudiante: est-001 (Juan Pérez)")
    result = analytics.get_perfil_completo("est-001")
    _json(result)

    # ── Consulta 2 ──────────────────────────────────────────
    _sep("CONSULTA 2 — Historial de sesiones de estudio (MongoDB)")
    print("Estudiante: est-001 — últimas 10 sesiones")
    result = analytics.get_historial_sesiones("est-001", limite=10)
    _json(result)

    # ── Consulta 3 ──────────────────────────────────────────
    _sep("CONSULTA 3 — Detectar dificultades de aprendizaje (MongoDB)")
    print("Estudiante: est-001 / Materia: mat-prog")
    result = analytics.detectar_dificultades("est-001", tema="mat-prog")
    _json(result)
    print("\n--- Sin filtro de tema (todos los intentos) ---")
    result = analytics.detectar_dificultades("est-001")
    _json(result)

    # ── Consulta 4 ──────────────────────────────────────────
    _sep("CONSULTA 4 — Eventos recientes del estudiante (MongoDB)")
    print("Estudiante: est-001 — últimos 10 eventos")
    result = analytics.get_eventos_recientes("est-001", limite=10)
    _json(result)

    # ── Consulta 5 ──────────────────────────────────────────
    _sep("CONSULTA 5 — Prerrequisitos recursivos de un tema (Neo4j)")
    print("Materia objetivo: mat-ml (Machine Learning)")
    result = graph.get_prerrequisitos("mat-ml")
    _json(result)

    # ── Consulta 6 ──────────────────────────────────────────
    _sep("CONSULTA 6 — Ruta óptima de aprendizaje (Neo4j)")
    print("Estudiante: est-001 → Objetivo: mat-bdnosql (Bases de Datos NoSQL)")
    result = graph.get_ruta_optima("est-001", "mat-bdnosql")
    _json(result)

    # ── Consulta 7 ──────────────────────────────────────────
    _sep("CONSULTA 7 — Caminos alternativos de aprendizaje (Neo4j)")
    print("Materia con dificultad: mat-bdnosql")
    result = graph.get_caminos_alternativos("mat-bdnosql")
    _json(result)

    _sep("FIN — 7 consultas ejecutadas correctamente")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()


# ── Main ────────────────────────────────────────────────────

def main():
    print("NeuroCheck — Demostración de las 7 consultas de Etapa 1")
    print(f"Timestamp inicio: {datetime.now().isoformat()}")

    mongo = MongoService(settings.mongo_uri)
    neo4j = Neo4jService(
        settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password
    )

    with mongo, neo4j:
        run_all(mongo, neo4j)


if __name__ == "__main__":
    main()
