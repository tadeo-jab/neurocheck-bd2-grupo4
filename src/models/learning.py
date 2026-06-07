from datetime import datetime
from pydantic import BaseModel


class Student(BaseModel):
    uid: str
    name: str
    created_at: datetime = datetime.now()


class Concept(BaseModel):
    uid: str
    name: str
    description: str = ""


class Activity(BaseModel):
    uid: str
    name: str
    type: str


class Resource(BaseModel):
    uid: str
    title: str
    url: str


class Subject(BaseModel):
    uid: str
    name: str
    code: str


# ── Relationship models (edge properties) ──

class Learns(BaseModel):
    confidence: float = 0.0
    since: datetime = datetime.now()


class Completes(BaseModel):
    score: float = 0.0
    completed_at: datetime = datetime.now()


class PrerequisiteOf(BaseModel):
    required: bool = True


class Uses(BaseModel):
    weight: float = 1.0


class BelongsTo(BaseModel):
    primary: bool = False
