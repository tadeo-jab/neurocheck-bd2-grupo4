from fastapi import Depends, Request

from src.config import settings
from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.service.auth_service import AuthService
from src.service.curriculum_service import CurriculumService
from src.service.mates_service import MatesService
from src.service.study_service import StudyService


# ── Bases de datos ──────────────────────────────────────

def get_mongo(request: Request) -> MongoService:
    return request.app.state.mongo

def get_neo4j(request: Request) -> Neo4jService:
    return request.app.state.neo4j

def get_redis_url() -> str:
    return settings.redis_url

# ── Servicios ───────────────────────────────────────────

def get_auth_service(
    neo4j: Neo4jService = Depends(get_neo4j),
    mongo: MongoService = Depends(get_mongo),
    redis_url: str = Depends(get_redis_url),
) -> AuthService:
    return AuthService(neo4j, mongo, redis_url)

def get_curriculum_service(
    neo4j: Neo4jService = Depends(get_neo4j),
) -> CurriculumService:
    return CurriculumService(neo4j)

def get_mates_service(
    neo4j: Neo4jService = Depends(get_neo4j),
) -> MatesService:
    return MatesService(neo4j)

def get_study_service(
    neo4j: Neo4jService = Depends(get_neo4j),
    mongo: MongoService = Depends(get_mongo),
    redis_url: str = Depends(get_redis_url),
) -> StudyService:
    return StudyService(neo4j, mongo, redis_url)
