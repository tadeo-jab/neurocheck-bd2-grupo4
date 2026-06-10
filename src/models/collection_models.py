from datetime import datetime
from pydantic import BaseModel


class StudentPreferences(BaseModel):
    format: str = "video"
    schedule: str = "mañana"


class StudentMetrics(BaseModel):
    fatigue: float = 0.0
    attention: float = 1.0


class StudentProgress(BaseModel):
    topics_completed: int = 0
    current_level: str = "principiante"


class Student(BaseModel):
    id: str
    name: str
    objectives: list[str] = []
    preferences: StudentPreferences = StudentPreferences()
    metrics: StudentMetrics = StudentMetrics()
    progress: StudentProgress = StudentProgress()


class StudySession(BaseModel):
    session_id: str
    student_id: str
    date: str
    activity: str
    topic: str
    duration_minutes: int
    attempts: int
    accuracy_percentage: float


class InteractionEvent(BaseModel):
    event_id: str
    student_id: str
    session_id: str
    event_type: str
    topic: str
    activity: str
    difficulty: str
    timestamp: datetime = datetime.now()
    duration_minutes: int
    status: str
    attempts: int = 0
    correct: int = 0
    errors: int = 0
    accuracy_percentage: float = 0.0
