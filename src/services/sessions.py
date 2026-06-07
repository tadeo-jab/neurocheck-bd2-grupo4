"""Session service — orchestrates MongoDB session & config repos."""

from pymongo.database import Database
from src.repositories.mongo.sessions import SessionRepository
from src.repositories.mongo.student_configs import StudentConfigRepository


class SessionService:
    def __init__(self, db: Database):
        self.sessions = SessionRepository(db)
        self.configs = StudentConfigRepository(db)

    def start_session(self, session_id: str, student_id: str) -> str:
        return self.sessions.create({
            "session_id": session_id,
            "student_id": student_id,
            "started_at": None,  # MongoDB handles this via $currentDate in real implementation
            "events": [],
        })

    def log_event(self, session_id: str, event: dict):
        self.sessions.update(session_id, {"events": event})
