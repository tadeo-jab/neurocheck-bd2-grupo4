from datetime import datetime
from pydantic import BaseModel


class Requires(BaseModel):
    weight: float
    notes: str = ""
    level: str


class CorrelatesWith(BaseModel):
    strength: float


class AlternativeTo(BaseModel):
    additional_cost: float
    favored_style: str


class Deepens(BaseModel):
    complexity_factor: float


class BelongsTo(BaseModel):
    weight_in_subject: float = 1.0


class Evaluates(BaseModel):
    coverage: float
    approval_threshold: float = 0.7


class Explains(BaseModel):
    coverage: float


class Studies(BaseModel):
    total_time_minutes: int
    last_studied_at: datetime = datetime.now()
    times_studied: int
    mastery_level: float


class Completes(BaseModel):
    score_obtained: float
    time_taken_seconds: int
    completed_at: datetime = datetime.now()
    attempts: int
    approved: bool
