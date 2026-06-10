"""Learning service — orchestrates Neo4j node & relationship repos."""

from neo4j import Driver
from src.repositories.neo4j.nodes.student_repository import StudentNodeRepo
from src.repositories.neo4j.nodes.concept_repository import ConceptNodeRepo
from src.repositories.neo4j.relationships.learns_repository import StudiesRepo
from src.repositories.neo4j.relationships.prerequisite_of_repository import RequiresRepo
from src.repositories.neo4j.relationships.completes_repository import CompletesRepo


class LearningService:
    def __init__(self, driver: Driver):
        self.students = StudentNodeRepo(driver)
        self.concepts = ConceptNodeRepo(driver)
        self.studies = StudiesRepo(driver)
        self.requires = RequiresRepo(driver)
        self.completes = CompletesRepo(driver)

    def enroll_in_concept(
        self,
        student_uid: str,
        concept_uid: str,
        total_time_minutes: int,
        times_studied: int,
        mastery_level: float,
    ):
        self.studies.create(student_uid, concept_uid, total_time_minutes, times_studied, mastery_level)
