from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo = MongoService(settings.mongo_uri)
    neo4j = Neo4jService(
        settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password
    )
    mongo.connect()
    neo4j.connect()

    app.state.mongo = mongo
    app.state.neo4j = neo4j

    yield

    mongo.disconnect()
    neo4j.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(
        title="NeuroCheck API",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from src.api.admin_router import router as admin_router
    from src.api.analytics_router import router as analytics_router
    from src.api.auth_router import router as auth_router
    from src.api.curriculum_router import router as curriculum_router
    from src.api.graph_router import router as graph_router
    from src.api.mates_router import router as mates_router
    from src.api.study_router import router as study_router

    app.include_router(admin_router, prefix="/api")
    app.include_router(analytics_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(curriculum_router, prefix="/api")
    app.include_router(graph_router, prefix="/api")
    app.include_router(mates_router, prefix="/api")
    app.include_router(study_router, prefix="/api")

    return app
