import secrets
import uuid
from datetime import datetime, timezone

import bcrypt

from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.sesion_repository import SesionRepository
from src.repository.neo4j.estudiante_repository import EstudianteRepository
from src.model.collection_models import Estudiante, Sesion


class AuthService:
    def __init__(self, neo4j: Neo4jService, mongo: MongoService):
        self._estudiante_repo = EstudianteRepository(neo4j)
        self._estudiante_mdb_repo = EstudianteMDBRepository(mongo)
        self._sesion_repo = SesionRepository(mongo)

    # ── Login ──────────────────────────────────────────────

    def login(self, email: str, password: str, ip: str = "") -> dict:
        estudiante = self._estudiante_mdb_repo.find_by_email(email)
        print(f"[auth_service] find_by_email({email!r}) → encontrado={estudiante is not None}")
        if not estudiante or not bcrypt.checkpw(
            password.encode(), estudiante.password_hash.encode()
        ):
            print(f"[auth_service] bcrypt check failed, raising 'Credenciales inválidas'")
            raise ValueError("Credenciales inválidas.")

        token = secrets.token_hex(32)
        sesion_id = uuid.uuid4().hex

        self._sesion_repo.create_session(Sesion(
            uid=sesion_id,
            estudiante=estudiante,
            fecha_ini=datetime.now(timezone.utc),
            fatiga_estimada=0.0,
            token=token,
        ))

        return {
            "token": token,
            "sesion_id": sesion_id,
            "user": {
                "id": estudiante.uid,
                "nombre": estudiante.nombre,
                "email": estudiante.email,
                "estilo_preferido": estudiante.estilo_preferido,
            },
        }

    # ── Registro ───────────────────────────────────────────

    def register(self, email: str, password: str, nombre: str,
                 estilo_preferido: str) -> dict:
        if self._estudiante_mdb_repo.find_by_email(email):
            raise ValueError("El email ya está registrado.")

        estudiante_id = uuid.uuid4().hex
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        estudiante = Estudiante(
            uid=estudiante_id,
            nombre=nombre,
            email=email,
            password_hash=password_hash,
            estilo_preferido=estilo_preferido,
        )
        self._estudiante_mdb_repo.insert(estudiante)
        self._estudiante_repo.crear(estudiante_id, nombre, estilo_preferido)

        return self.login(email, password)

    # ── Sesión ─────────────────────────────────────────────

    def validar_sesion(self, token: str | None) -> dict:
        if not token:
            raise ValueError("Token requerido.")
        doc = self._sesion_repo.find_by_token(token)
        if not doc:
            raise ValueError("Sesión expirada o inválida.")
        return doc

    def logout(self, token: str) -> None:
        doc = self._sesion_repo.find_by_token(token)
        if not doc:
            return
        self._sesion_repo.end_session(doc["uid"])
