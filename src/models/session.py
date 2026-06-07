from datetime import datetime
from pydantic import BaseModel


class Session(BaseModel):
    session_id: str
    student_id: str
    started_at: datetime = datetime.now()
    ended_at: datetime | None = None
    events: list[dict] = []


class StudentConfig(BaseModel):
    student_id: str
    preferences: dict = {}
    last_active: datetime = datetime.now()
