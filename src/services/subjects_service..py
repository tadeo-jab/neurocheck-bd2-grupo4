"""Subject service — subject structure and membership."""

from neo4j import Driver
from src.models.node_models import Subject
from src.models.relationship_models import BelongsTo, Evaluates
from src.repositories.neo4j.nodes.subject_repository import SubjectNodeRepo
from src.repositories.neo4j.relationships.belongs_to_repository import BelongsToRepo
from src.repositories.neo4j.relationships.evaluates_repository import EvaluatesRepo


class SubjectService:
    def __init__(self, driver: Driver):
        self.subjects = SubjectNodeRepo(driver)
        self.belongs_to = BelongsToRepo(driver)
        self.evaluates = EvaluatesRepo(driver)

    def create_subject(self, subject: Subject) -> dict:
        return self.subjects.create(subject)

    def assign_concept(self, concept_uid: str, subject_uid: str, rel: BelongsTo):
        self.belongs_to.create(concept_uid, subject_uid, rel)

    def assign_activity(self, activity_uid: str, subject_uid: str, rel: Evaluates):
        self.evaluates.create(activity_uid, subject_uid, rel)

    def get_concepts(self, subject_uid: str) -> list[dict]:
        return self.belongs_to.find_by_subject(subject_uid)

    def get_activities(self, subject_uid: str) -> list[dict]:
        return self.evaluates.find_by_subject(subject_uid)

    def remove_concept(self, concept_uid: str, subject_uid: str):
        self.belongs_to.delete(concept_uid, subject_uid)

    def remove_activity(self, activity_uid: str, subject_uid: str):
        self.evaluates.delete(activity_uid, subject_uid)
