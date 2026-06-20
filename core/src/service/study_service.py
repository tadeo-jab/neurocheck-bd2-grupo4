import uuid
from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.model.collection_models import Actividad, CaminoAprendizaje, Estudiante, Intento, Recurso
from src.repository.mongo.curriculum_repository import CurriculumRepository
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.evento_repository import EventoRepository
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
        self._evento_repo = EventoRepository(mongo)

        self.limite_intentos = 5
        self.warning_threshold = 4

    # ── Currículum ────────────────────────────────────────

    def get_subject_course(self, id_estudiante: str, id_materia: str) -> tuple[CaminoAprendizaje, dict[int, bool]]:
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

        progress: dict[int, bool] = {}
        for i, item in enumerate(camino.secuencia):
            if item["tipo"] == "recurso":
                progress[i] = self._materia_estudiante_repo.is_terminado(id_estudiante, item["id"])
            else:
                progress[i] = self._materia_estudiante_repo.is_aprobado(id_estudiante, item["id"])

        return camino, progress

    def get_resource(self, id_recurso: str) -> Recurso:
        recurso = self._curriculum_repo.get_resource(id_recurso)
        if not recurso:
            raise ValueError(f"Recurso {id_recurso} no encontrado.")
        return recurso

    def get_activity(self, id_actividad: str) -> Actividad:
        actividad = self._curriculum_repo.get_activity(id_actividad)
        if not actividad:
            raise ValueError(f"Actividad {id_actividad} no encontrada.")
        return actividad

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

        sesion = self._sesion_repo.find_by_uid(sesion_id)
        if sesion:
            self._evento_repo.create_event(
                tipo_evento="start_attempt",
                usuario=estudiante,
                sesion=sesion,
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

    def close_attempt(self, intento_id: str, *, terminado: bool,
                      auto_percepcion: int | None = None,
                      respuestas: dict[str, int] | None = None) -> dict:
        doc = self._intento_repo.find_by_id(intento_id)
        if not doc:
            raise ValueError(f"Intento {intento_id} no encontrado.")

        # Determinar aprobado, aciertos, errores, puntaje según tipo
        aprobado = False
        aciertos: int | None = None
        errores: int | None = None
        puntaje: float | None = None

        if doc["tipo_contenido"] == "recurso":
            aprobado = terminado
        elif respuestas:
            actividad = self._curriculum_repo.get_activity(doc["id_contenido"])
            if actividad:
                aciertos = 0
                puntaje = 0.0
                for p in actividad.preguntas:
                    if respuestas.get(p.uid) == p.respuesta_correcta:
                        aciertos += 1
                        puntaje += p.puntaje
                errores = len(actividad.preguntas) - aciertos
                aprobado = puntaje >= actividad.puntaje_maximo * 0.6

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

        user_id = doc["estudiante"]["uid"]
        id_contenido = doc["id_contenido"]

        if doc["tipo_contenido"] == "recurso":
            self._materia_estudiante_repo.set_studied(user_id, id_contenido, terminado)
        else:
            self._materia_estudiante_repo.set_completed(user_id, id_contenido, aprobado, puntaje or 0)

        # Si aprobó, revisar si completó todos los contenidos de la materia
        curso_aprobado = False
        if aprobado:
            try:
                _, progress = self.get_subject_course(user_id, doc["id_materia"])
                if all(progress.values()):
                    self._materia_estudiante_repo.set_enrollment_completed(user_id, doc["id_materia"])
                    curso_aprobado = True
            except ValueError:
                pass  # no debería pasar, pero no queremos romper el cierre

        precuela = None
        warning = False
        if (not terminado or not aprobado) and self.warning_verdict(user_id=doc["estudiante"]["uid"]):
            warning = True
            precuela = self._materia_repo.get_prequel_if_exists(doc["id_materia"])

        print(f"[close_attempt] intento={intento_id} materia={doc['id_materia']} "
              f"terminado={terminado} aprobado={aprobado} "
              f"warning={warning} precuela={precuela.id if precuela else None}")

        usuario = self._estudiante_mdb_repo.find_by_id(user_id)
        sesion = self._sesion_repo.find_by_uid(doc["id_sesion"])
        if usuario and sesion:
            self._evento_repo.create_event(
                tipo_evento="close_attempt",
                usuario=usuario,
                sesion=sesion,
            )

        return {"warning": warning, "precuela": precuela, "aprobado": aprobado, "puntaje": puntaje,
                "curso_aprobado": curso_aprobado}

    def warning_verdict(self, user_id: str) -> bool:
        attempts = self._intento_repo.get_last_attempts(user_id, self.limite_intentos)
        malos = sum(1 for a in attempts if not a.get("aprobado") or not a.get("terminado"))
        return malos >= self.warning_threshold
