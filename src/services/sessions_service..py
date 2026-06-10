"""Session service — orchestrates MongoDB session, student & event repos."""

from pymongo.database import Database
from src.models.collection_models import Student, StudySession, InteractionEvent
from src.repositories.mongo.sessions import StudySessionRepository
from src.repositories.mongo.student_configs import StudentRepository
from src.repositories.mongo.interaction_events import InteractionEventRepository


class SessionService:
    def __init__(self, db: Database):
        self.sessions = StudySessionRepository(db)
        self.students = StudentRepository(db)
        self.events = InteractionEventRepository(db)

    def create_student(self, student: Student) -> str:
        return self.students.create(student)

    def start_session(self, session: StudySession) -> str:
        return self.sessions.create(session)

    def log_event(self, event: InteractionEvent) -> str:
        return self.events.create(event)
