"""Session service — orchestrates MongoDB session, student & event repos."""

from pymongo.database import Database
from src.repositories.mongo.sessions import StudySessionRepository
from src.repositories.mongo.student_configs import StudentRepository
from src.repositories.mongo.interaction_events import InteractionEventRepository


class SessionService:
    def __init__(self, db: Database):
        self.sessions = StudySessionRepository(db)
        self.students = StudentRepository(db)
        self.events = InteractionEventRepository(db)

    def create_student(
        self,
        student_id: str,
        name: str,
        objectives: list[str] | None = None,
        preferences: dict | None = None,
    ) -> str:
        return self.students.create({
            "id": student_id,
            "name": name,
            "objectives": objectives or [],
            "preferences": preferences or {},
            "metrics": {"fatigue": 0.0, "attention": 1.0},
            "progress": {"topics_completed": 0, "current_level": "principiante"},
        })

    def start_session(
        self,
        session_id: str,
        student_id: str,
        date: str,
        activity: str,
        topic: str,
        duration_minutes: int,
        attempts: int,
        accuracy_percentage: float,
    ) -> str:
        return self.sessions.create({
            "session_id": session_id,
            "student_id": student_id,
            "date": date,
            "activity": activity,
            "topic": topic,
            "duration_minutes": duration_minutes,
            "attempts": attempts,
            "accuracy_percentage": accuracy_percentage,
        })

    def log_event(
        self,
        event_id: str,
        student_id: str,
        session_id: str,
        event_type: str,
        topic: str,
        activity: str,
        difficulty: str,
        duration_minutes: int,
        status: str,
        attempts: int = 0,
        correct: int = 0,
        errors: int = 0,
        accuracy_percentage: float = 0.0,
    ) -> str:
        return self.events.create({
            "event_id": event_id,
            "student_id": student_id,
            "session_id": session_id,
            "event_type": event_type,
            "topic": topic,
            "activity": activity,
            "difficulty": difficulty,
            "duration_minutes": duration_minutes,
            "status": status,
            "attempts": attempts,
            "correct": correct,
            "errors": errors,
            "accuracy_percentage": accuracy_percentage,
        })
