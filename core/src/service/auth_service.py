import secrets
import uuid
from datetime import datetime, timezone

import bcrypt

from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.sesion_repository import SesionRepository
from src.repository.neo4j.estudiante_repository import EstudianteRepository
from src.repository.redis.sesion_cache import SessionCacheRepository
from src.model.collection_models import Estudiante, Sesion


class AuthService:
    def __init__(self, neo4j: Neo4jService, mongo: MongoService, redis_url: str):
        self._estudiante_repo = EstudianteRepository(neo4j)
        self._estudiante_mdb_repo = EstudianteMDBRepository(mongo)
        self._sesion_repo = SesionRepository(mongo)
        self._cache = SessionCacheRepository(redis_url)

    # ── Login ──────────────────────────────────────────────

    def login(self, email: str, password: str, ip: str = "") -> dict:
        if self._cache.intentos_restantes(email) == 0:
            raise ValueError("Demasiados intentos. Intente más tarde.")

        estudiante = self._estudiante_mdb_repo.find_by_email(email)
        if not estudiante or not bcrypt.checkpw(
            password.encode(), estudiante.password_hash.encode()
        ):
            self._cache.incrementar_intento(email)
            raise ValueError("Credenciales inválidas.")

        self._cache._redis.delete(f"sesiones:intentos:{email}")

        token = secrets.token_hex(32)
        sesion_id = uuid.uuid4().hex

        self._sesion_repo.create_session(Sesion(
            id=sesion_id,
            estudiante=estudiante,
            fecha_ini=datetime.now(timezone.utc),
            fatiga_estimada=0.0,
        ))

        self._cache.crear_sesion(token, {
            "user_id": estudiante.id,
            "sesion_id": sesion_id,
            "email": estudiante.email,
            "rol": "estudiante",
            "nombre": estudiante.nombre,
            "creado": datetime.now(timezone.utc).isoformat(),
            "ip": ip,
        })
        self._cache.vincular_usuario(estudiante.id, token)

        return {
            "token": token,
            "user": {
                "id": estudiante.id,
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
            id=estudiante_id,
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
        datos = self._cache.validar_sesion(token)
        if not datos:
            raise ValueError("Sesión expirada o inválida.")
        return datos

    def logout(self, token: str) -> None:
        datos = self._cache.validar_sesion(token)
        if not datos:
            return
        self._sesion_repo.end_session(datos["sesion_id"])
        self._cache.cerrar_sesion(token, datos["user_id"])
