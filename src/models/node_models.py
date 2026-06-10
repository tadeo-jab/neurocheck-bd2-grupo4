from datetime import datetime
from pydantic import BaseModel


class Student(BaseModel):
    uid: str
    name: str
    mastery_level: float
    preferred_style: str
    current_session_id: str | None = None
    created_at: datetime = datetime.now()


class Concept(BaseModel):
    uid: str
    name: str
    description: str = ""
    difficulty_level: float
    estimated_time_minutes: int
    usage_frequency: int


class Activity(BaseModel):
    uid: str
    name: str
    description: str = ""
    type: str
    difficulty: float
    estimated_time_minutes: int
    cognitive_load: float
    max_score: float


class Resource(BaseModel):
    uid: str
    type: str
    duration: int
    cognitive_load: float
    url: str = ""
    optimal_learning_style: list[str] = []


class Subject(BaseModel):
    uid: str
    name: str
    difficulty_level: float
