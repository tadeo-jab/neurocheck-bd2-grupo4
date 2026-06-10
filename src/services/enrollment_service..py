"""Enrollment service — student engagement with concepts."""

from neo4j import Driver
from src.models.node_models import Student, Concept
from src.models.relationship_models import Studies
from src.repositories.neo4j.nodes.student_repository import StudentNodeRepo
from src.repositories.neo4j.nodes.concept_repository import ConceptNodeRepo
from src.repositories.neo4j.relationships.learns_repository import StudiesRepo


class EnrollmentService:
    def __init__(self, driver: Driver):
        self.students = StudentNodeRepo(driver)
        self.concepts = ConceptNodeRepo(driver)
        self.studies = StudiesRepo(driver)

    def create_student(self, student: Student) -> dict:
        return self.students.create(student)

    def create_concept(self, concept: Concept) -> dict:
        return self.concepts.create(concept)

    def study_concept(self, student_uid: str, concept_uid: str, rel: Studies):
        self.studies.create(student_uid, concept_uid, rel)

    def get_student_concepts(self, student_uid: str) -> list[dict]:
        return self.studies.find_by_student(student_uid)

    def unenroll(self, student_uid: str, concept_uid: str):
        self.studies.delete(student_uid, concept_uid)
