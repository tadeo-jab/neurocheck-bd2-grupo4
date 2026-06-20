from fastapi import Depends, Request

from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.service.admin_service import AdminService
from src.service.auth_service import AuthService
from src.service.curriculum_service import CurriculumService
from src.service.mates_service import MatesService
from src.service.study_service import StudyService


# ── Bases de datos ──────────────────────────────────────

def get_mongo(request: Request) -> MongoService:
    return request.app.state.mongo

def get_neo4j(request: Request) -> Neo4jService:
    return request.app.state.neo4j

# ── Servicios ───────────────────────────────────────────

def get_auth_service(
    neo4j: Neo4jService = Depends(get_neo4j),
    mongo: MongoService = Depends(get_mongo),
) -> AuthService:
    return AuthService(neo4j, mongo)

def get_curriculum_service(
    neo4j: Neo4jService = Depends(get_neo4j),
    mongo: MongoService = Depends(get_mongo),
) -> CurriculumService:
    return CurriculumService(neo4j, mongo)

def get_mates_service(
    neo4j: Neo4jService = Depends(get_neo4j),
    mongo: MongoService = Depends(get_mongo),
) -> MatesService:
    return MatesService(neo4j, mongo)

def get_study_service(
    neo4j: Neo4jService = Depends(get_neo4j),
    mongo: MongoService = Depends(get_mongo),
) -> StudyService:
    return StudyService(neo4j, mongo)

def get_admin_service(
    mongo: MongoService = Depends(get_mongo),
) -> AdminService:
    return AdminService(mongo)
