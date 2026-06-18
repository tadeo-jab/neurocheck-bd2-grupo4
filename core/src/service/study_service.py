import uuid
from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.model.collection_models import Actividad, CaminoAprendizaje, Estudiante, Intento, Recurso
from src.repository.mongo.curriculum_repository import CurriculumRepository
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.intento_repository import IntentoRepository
from src.repository.neo4j.estudiante_repository import EstudianteRepository
from src.repository.neo4j.materia_repository import MateriaRepository
from src.repository.neo4j.materia_estudiante_repository import MateriaEstudianteRepository
from src.repository.redis.intento_cache import IntentoCacheRepository
from src.repository.redis.session_cache import SessionCacheRepository


class StudyService:
    def __init__(self, neo4j: Neo4jService, mongo: MongoService, redis_url: str):
        self._estudiante_repo = EstudianteRepository(neo4j)
        self._materia_repo = MateriaRepository(neo4j)
        self._materia_estudiante_repo = MateriaEstudianteRepository(neo4j)
        self._estudiante_mdb_repo = EstudianteMDBRepository(mongo)
        self._curriculum_repo = CurriculumRepository(mongo)
        self._intento_repo = IntentoRepository(mongo)
        self._cache_sesion = SessionCacheRepository(redis_url)
        self._cache_intento = IntentoCacheRepository(redis_url)

    # ── Currículum ────────────────────────────────────────

    def get_subject_course(self, id_estudiante: str, id_materia: str) -> CaminoAprendizaje:
        if not self._estudiante_repo.exists_by_id(id_estudiante):
            raise ValueError(f"Estudiante {id_estudiante} no encontrado")
        if not self._materia_repo.exists_by_id(id_materia):
            raise ValueError(f"Materia {id_materia} no encontrada")

        estilo = self._materia_estudiante_repo.get_enrollment_style(id_estudiante, id_materia)
        if estilo is None:
            raise ValueError(f"Estudiante {id_estudiante} no está anotado en {id_materia}")

        camino = self._curriculum_repo.get_course_by_style(id_materia, estilo)
        if camino is None:
            raise ValueError(f"No hay camino '{estilo}' para la materia {id_materia}")

        return camino

    # ── Intento ───────────────────────────────────────────

    def start_attempt(self, token: str, id_materia: str,
                      id_contenido: str, tipo_contenido: str,
                      duracion_total: int = 0) -> dict:
        sesion = self._cache_sesion.validar_sesion(token)
        if not sesion:
            raise ValueError("Sesión inválida o expirada.")

        user_id = sesion["user_id"]
        sesion_id = sesion["sesion_id"]
        estudiante = self._estudiante_mdb_repo.find_by_id(user_id)
        if not estudiante:
            raise ValueError(f"Estudiante {user_id} no encontrado.")

        intento_id = uuid.uuid4().hex

        self._intento_repo.create_attempt(
            id=intento_id,
            estudiante=estudiante,
            id_sesion=sesion_id,
            id_materia=id_materia,
            id_contenido=id_contenido,
            tipo_contenido=tipo_contenido,
            inicio=datetime.now(timezone.utc),
        )

        if duracion_total > 0:
            self._cache_intento.iniciar_cronometro(
                intento_id, id_contenido, user_id, duracion_total
            )

        if tipo_contenido == "recurso":
            contenido = self._curriculum_repo.get_resource(id_contenido)
        else:
            contenido = self._curriculum_repo.get_activity(id_contenido)

        if not contenido:
            raise ValueError(f"Contenido {id_contenido} no encontrado.")

        return {"intento_id": intento_id, "contenido": contenido}

    def pause_attempt(self, intento_id: str) -> float:
        doc = self._intento_repo.find_by_id(intento_id)
        if not doc:
            raise ValueError(f"Intento {intento_id} no encontrado.")
        return self._cache_intento.pausar_cronometro(
            doc["id_contenido"], doc["estudiante"]["id"]
        )

    def resume_attempt(self, intento_id: str) -> float:
        doc = self._intento_repo.find_by_id(intento_id)
        if not doc:
            raise ValueError(f"Intento {intento_id} no encontrado.")
        return self._cache_intento.reanudar_cronometro(
            doc["id_contenido"], doc["estudiante"]["id"]
        )

    def close_attempt(self, intento_id: str, *, terminado: bool = True,
                      auto_percepcion: int | None = None,
                      aciertos: int | None = None,
                      errores: int | None = None,
                      puntaje: float | None = None,
                      aprobado: bool | None = None) -> None:
        doc = self._intento_repo.find_by_id(intento_id)
        if not doc:
            raise ValueError(f"Intento {intento_id} no encontrado.")

        actividad_id = doc["id_contenido"]
        user_id = doc["estudiante"]["id"]
        datos = self._cache_intento.obtener_datos(actividad_id, user_id)

        if datos:
            duracion = int(float(datos["transcurrido"]))
            pausas = int(datos.get("pausas", 0))
            duracion_pausa = int(float(datos.get("tiempo_pausado", 0)))
        else:
            duracion = doc.get("duracion_segundos", 0)
            pausas = doc.get("pausas", 0)
            duracion_pausa = doc.get("duracion_pausa_segundos", 0)

        intento = Intento(
            id=doc["_id"],
            estudiante=Estudiante(**doc["estudiante"]),
            id_sesion=doc["id_sesion"],
            id_materia=doc["id_materia"],
            id_contenido=actividad_id,
            tipo_contenido=doc["tipo_contenido"],
            inicio=doc["inicio"],
            fin=datetime.now(timezone.utc),
            duracion_segundos=duracion,
            pausas=pausas,
            duracion_pausa_segundos=duracion_pausa,
            terminado=terminado,
            auto_percepcion=auto_percepcion,
            aciertos=aciertos,
            errores=errores,
            puntaje=puntaje,
            aprobado=aprobado,
        )

        self._intento_repo.close_attempt(intento)
        self._cache_intento.detener_cronometro(actividad_id, user_id)
