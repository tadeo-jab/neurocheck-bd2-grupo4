"""
AnalyticsService — implementa los 4 patrones de consulta MongoDB declarados en Etapa 1.

Consulta 1: Perfil completo del estudiante
Consulta 2: Historial de sesiones de estudio
Consulta 3: Detectar posibles dificultades de aprendizaje
Consulta 4: Obtener eventos recientes de un estudiante
"""

from datetime import datetime

from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.sesion_repository import SesionRepository
from src.repository.mongo.intento_repository import IntentoRepository
from src.repository.mongo.evento_repository import EventoRepository
from src.repository.neo4j.materia_estudiante_repository import MateriaEstudianteRepository


class AnalyticsService:

    def __init__(self, mongo: MongoService, neo4j: Neo4jService):
        self._estudiante_repo = EstudianteMDBRepository(mongo)
        self._sesion_repo = SesionRepository(mongo)
        self._intento_repo = IntentoRepository(mongo)
        self._evento_repo = EventoRepository(mongo)
        self._mat_est_repo = MateriaEstudianteRepository(neo4j)

    # ── Consulta 1 — Perfil completo ───────────────────────

    def get_perfil_completo(self, id_estudiante: str) -> dict:
        """
        Combina datos de MongoDB (auth, métricas de sesiones)
        con datos de Neo4j (matrículas, estado por materia).
        """
        estudiante = self._estudiante_repo.find_by_id(id_estudiante)
        if not estudiante:
            raise ValueError(f"Estudiante {id_estudiante} no encontrado.")

        sesiones = self._sesion_repo.get_student_sessions(id_estudiante, limite=100)
        total_sesiones = len(sesiones)
        duracion_promedio = 0.0
        fatiga_promedio = 0.0
        if sesiones:
            sesiones_con_duracion = [
                s for s in sesiones if s.fecha_fin is not None
            ]
            if sesiones_con_duracion:
                duracion_promedio = sum(
                    (s.fecha_fin - s.fecha_ini).total_seconds() / 60
                    for s in sesiones_con_duracion
                ) / len(sesiones_con_duracion)
            fatiga_promedio = sum(s.fatiga_estimada for s in sesiones) / total_sesiones

        intentos = self._intento_repo.get_all_attempts(id_estudiante)
        total_intentos = len(intentos)
        aprobados = sum(1 for i in intentos if i.get("aprobado"))
        pct_aciertos = round(aprobados / total_intentos * 100, 1) if total_intentos else 0

        estados_materias = self._mat_est_repo.get_student_nodes_status(id_estudiante)
        completadas = sum(1 for e in estados_materias if e.get("estado") in ("aprobada", "completada"))
        en_curso = sum(1 for e in estados_materias if e.get("estado") == "cursando")

        return {
            "id": estudiante.uid,
            "nombre": estudiante.nombre,
            "email": estudiante.email,
            "estilo_preferido": estudiante.estilo_preferido,
            "metricas": {
                "total_sesiones": total_sesiones,
                "duracion_promedio_minutos": round(duracion_promedio, 1),
                "fatiga_promedio": round(fatiga_promedio, 2),
                "total_intentos": total_intentos,
                "intentos_aprobados": aprobados,
                "porcentaje_aciertos": pct_aciertos,
            },
            "progreso": {
                "materias_completadas": completadas,
                "materias_en_curso": en_curso,
                "nivel_actual": _calcular_nivel(pct_aciertos),
            },
        }

    # ── Consulta 2 — Historial de sesiones ─────────────────

    def get_historial_sesiones(self, id_estudiante: str,
                               fecha_desde: datetime | None = None,
                               fecha_hasta: datetime | None = None,
                               limite: int = 50) -> dict:
        """
        Devuelve sesiones ordenadas cronológicamente con métricas por sesión.
        """
        sesiones = self._sesion_repo.get_student_sessions(id_estudiante, limite=limite)

        if fecha_desde:
            sesiones = [s for s in sesiones if s.fecha_ini >= fecha_desde]
        if fecha_hasta:
            sesiones = [s for s in sesiones if s.fecha_ini <= fecha_hasta]

        sesiones_serializadas = []
        for s in sesiones:
            duracion_min = None
            if s.fecha_fin:
                duracion_min = round((s.fecha_fin - s.fecha_ini).total_seconds() / 60, 1)
            sesiones_serializadas.append({
                "id_sesion": s.uid,
                "fecha_ini": s.fecha_ini.isoformat(),
                "fecha_fin": s.fecha_fin.isoformat() if s.fecha_fin else None,
                "duracion_minutos": duracion_min,
                "cantidad_intentos": len(s.intentos_estudio),
                "fatiga_estimada": s.fatiga_estimada,
            })

        return {
            "id_estudiante": id_estudiante,
            "total_sesiones": len(sesiones_serializadas),
            "sesiones": sesiones_serializadas,
        }

    # ── Consulta 3 — Detectar dificultades ─────────────────

    def detectar_dificultades(self, id_estudiante: str,
                              tema: str | None = None) -> dict:
        """
        Analiza señales de dificultad: bajo porcentaje de aciertos,
        muchos intentos, abandonos, frecuencia decreciente de acceso.
        """
        intentos = self._intento_repo.get_all_attempts(id_estudiante)
        if tema:
            intentos = [i for i in intentos if i.get("id_materia") == tema]

        total = len(intentos)
        if total == 0:
            return {
                "id_estudiante": id_estudiante,
                "tema": tema,
                "alerta": False,
                "motivos": [],
                "detalle": "Sin intentos registrados.",
            }

        aprobados = sum(1 for i in intentos if i.get("aprobado"))
        abandonados = sum(1 for i in intentos if not i.get("terminado"))
        pct_aciertos = round(aprobados / total * 100, 1)
        pct_abandono = round(abandonados / total * 100, 1)

        duraciones = [
            i.get("duracion_segundos", 0) for i in intentos
            if i.get("duracion_segundos", 0) > 0
        ]
        tiempo_promedio = round(sum(duraciones) / len(duraciones), 1) if duraciones else 0

        eventos = self._evento_repo.get_events_for_difficulty(id_estudiante, tema)
        total_eventos = len(eventos)

        motivos = []
        if pct_aciertos < 50:
            motivos.append(f"Bajo porcentaje de aciertos: {pct_aciertos}%")
        if pct_abandono > 30:
            motivos.append(f"Alta tasa de abandono: {pct_abandono}%")
        if total >= 4 and aprobados == 0:
            motivos.append(f"Sin aprobaciones en {total} intentos consecutivos")
        if tiempo_promedio > 1800:
            motivos.append(f"Tiempo promedio de resolución alto: {tiempo_promedio}s")

        return {
            "id_estudiante": id_estudiante,
            "tema": tema,
            "alerta": len(motivos) > 0,
            "motivos": motivos,
            "detalle": {
                "total_intentos": total,
                "aprobados": aprobados,
                "abandonados": abandonados,
                "porcentaje_aciertos": pct_aciertos,
                "porcentaje_abandono": pct_abandono,
                "tiempo_promedio_segundos": tiempo_promedio,
                "total_eventos_interaccion": total_eventos,
            },
        }

    # ── Consulta 4 — Eventos recientes ─────────────────────

    def get_eventos_recientes(self, id_estudiante: str, limite: int = 20) -> dict:
        """
        Devuelve las últimas interacciones educativas registradas para el estudiante.
        """
        eventos = self._evento_repo.get_recent_events(id_estudiante, limit=limite)

        for e in eventos:
            if isinstance(e.get("timestamp"), datetime):
                e["timestamp"] = e["timestamp"].isoformat()

        return {
            "id_estudiante": id_estudiante,
            "total": len(eventos),
            "eventos": eventos,
        }


# ── Helpers ────────────────────────────────────────────────

def _calcular_nivel(pct_aciertos: float) -> str:
    if pct_aciertos >= 80:
        return "avanzado"
    if pct_aciertos >= 50:
        return "intermedio"
    return "básico"
