"""Learning service — orchestrates Neo4j node & relationship repos."""

from neo4j import Driver
from src.repositories.neo4j.nodes.students import StudentNodeRepo
from src.repositories.neo4j.nodes.concepts import ConceptNodeRepo
from src.repositories.neo4j.relationships.learns import LearnsRepo
from src.repositories.neo4j.relationships.prerequisite_of import PrerequisiteOfRepo
from src.repositories.neo4j.relationships.completes import CompletesRepo


class LearningService:
    def __init__(self, driver: Driver):
        self.students = StudentNodeRepo(driver)
        self.concepts = ConceptNodeRepo(driver)
        self.learns = LearnsRepo(driver)
        self.prerequisites = PrerequisiteOfRepo(driver)
        self.completes = CompletesRepo(driver)

    def enroll_in_concept(self, student_uid: str, concept_uid: str, confidence: float = 0.0):
        self.learns.create(student_uid, concept_uid, confidence)
