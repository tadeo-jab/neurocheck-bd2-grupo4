import uuid
from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.model.collection_models import Actividad, CaminoAprendizaje, Estudiante, Intento, Recurso
from src.repository.mongo.curriculum_repository import CurriculumRepository
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.intento_repository import IntentoRepository
from src.repository.mongo.sesion_repository import SesionRepository
from src.repository.neo4j.estudiante_repository import EstudianteRepository
from src.repository.neo4j.materia_repository import MateriaRepository
from src.repository.neo4j.materia_estudiante_repository import MateriaEstudianteRepository


class StudyService:
    def __init__(self, neo4j: Neo4jService, mongo: MongoService):
        self._estudiante_repo = EstudianteRepository(neo4j)
        self._materia_repo = MateriaRepository(neo4j)
        self._materia_estudiante_repo = MateriaEstudianteRepository(neo4j)
        self._estudiante_mdb_repo = EstudianteMDBRepository(mongo)
        self._curriculum_repo = CurriculumRepository(mongo)
        self._intento_repo = IntentoRepository(mongo)
        self._sesion_repo = SesionRepository(mongo)

        self.limite_intentos = 5
        self.warning_threshold = 4

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

    def get_resource(self, id_recurso: str) -> Recurso:
        recurso = self._curriculum_repo.get_resource(id_recurso)
        if not recurso:
            raise ValueError(f"Recurso {id_recurso} no encontrado.")
        return recurso

    # ── Intento ───────────────────────────────────────────

    def start_attempt(self, token: str, id_materia: str,
                      id_contenido: str, tipo_contenido: str,
                      duracion_total: int = 0) -> dict:

        sesion_doc = self._sesion_repo.find_by_token(token)
        if not sesion_doc:
            raise ValueError("Sesión inválida o expirada.")

        user_id = sesion_doc["estudiante"]["uid"]
        sesion_id = sesion_doc["uid"]
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

        return {"intento_id": intento_id, "duracion_total": duracion_total}

    def pause_attempt(self, intento_id: str) -> float:
        doc = self._intento_repo.pause_attempt(intento_id)
        if not doc:
            raise ValueError(f"Intento {intento_id} no encontrado.")
        return float(doc["duracion_segundos"])

    def resume_attempt(self, intento_id: str) -> float:
        doc = self._intento_repo.resume_attempt(intento_id)
        if not doc:
            raise ValueError(f"Intento {intento_id} no encontrado o no está pausado.")
        return float(doc["duracion_segundos"])

    def close_attempt(self, intento_id: str, *, aprobado: bool,
                      terminado: bool,
                      auto_percepcion: int | None = None,
                      aciertos: int | None = None,
                      errores: int | None = None,
                      puntaje: float | None = None) -> dict:
        doc = self._intento_repo.find_by_id(intento_id)
        if not doc:
            raise ValueError(f"Intento {intento_id} no encontrado.")

        # Si está pausado, acumular el tiempo activo final antes de cerrar
        duracion = doc.get("duracion_segundos", 0)
        pausas = doc.get("pausas", 0)
        duracion_pausa = doc.get("duracion_pausa_segundos", 0)

        if doc.get("pausa_inicio") is None:
            # No está pausado: acumular el tramo activo actual
            ahora = datetime.now(timezone.utc)
            ultima = doc.get("ultima_reanudacion", doc["inicio"])
            if isinstance(ultima, str):
                ultima = datetime.fromisoformat(ultima)
            if ultima.tzinfo is None:
                ultima = ultima.replace(tzinfo=timezone.utc)
            duracion += int((ahora - ultima).total_seconds())

        intento = Intento(
            uid=doc["uid"],
            estudiante=Estudiante(**doc["estudiante"]),
            id_sesion=doc["id_sesion"],
            id_materia=doc["id_materia"],
            id_contenido=doc["id_contenido"],
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
        self._sesion_repo.add_attempt_session(intento.id_sesion, intento)

        precuela = None
        warning = False
        if (not terminado or not aprobado) and self.warning_verdict(user_id=doc["estudiante"]["uid"]):
            warning = True
            precuela = self._materia_repo.get_prequel_if_exists(doc["id_materia"])

        print(f"[close_attempt] intento={intento_id} materia={doc['id_materia']} "
              f"terminado={terminado} aprobado={aprobado} "
              f"warning={warning} precuela={precuela.id if precuela else None}")

        return {"warning": warning, "precuela": precuela}

    def warning_verdict(self, user_id: str) -> bool:
        attempts = self._intento_repo.get_last_attempts(user_id, self.limite_intentos)
        malos = sum(1 for a in attempts if not a.get("aprobado") or not a.get("terminado"))
        return malos >= self.warning_threshold
