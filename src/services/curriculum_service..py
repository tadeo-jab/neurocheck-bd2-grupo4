"""Curriculum service — concept hierarchy and relationships."""

from neo4j import Driver
from src.models.relationship_models import Requires, CorrelatesWith, AlternativeTo, Deepens
from src.repositories.neo4j.relationships.prerequisite_of_repository import RequiresRepo
from src.repositories.neo4j.relationships.correlates_with_repository import CorrelatesWithRepo
from src.repositories.neo4j.relationships.alternative_to_repository import AlternativeToRepo
from src.repositories.neo4j.relationships.deepens_repository import DeepensRepo


class CurriculumService:
    def __init__(self, driver: Driver):
        self.requires = RequiresRepo(driver)
        self.correlates = CorrelatesWithRepo(driver)
        self.alternatives = AlternativeToRepo(driver)
        self.deepens = DeepensRepo(driver)

    def add_prerequisite(self, concept_uid: str, prerequisite_uid: str, rel: Requires):
        self.requires.create(concept_uid, prerequisite_uid, rel)

    def add_correlation(self, concept_a_uid: str, concept_b_uid: str, rel: CorrelatesWith):
        self.correlates.create(concept_a_uid, concept_b_uid, rel)

    def add_alternative(self, concept_uid: str, alternative_uid: str, rel: AlternativeTo):
        self.alternatives.create(concept_uid, alternative_uid, rel)

    def add_advanced_version(self, advanced_uid: str, foundational_uid: str, rel: Deepens):
        self.deepens.create(advanced_uid, foundational_uid, rel)

    def get_prerequisites(self, concept_uid: str) -> list[dict]:
        return self.requires.find_prerequisites(concept_uid)

    def get_correlated(self, concept_uid: str) -> list[dict]:
        return self.correlates.find_by_concept(concept_uid)

    def get_alternatives(self, concept_uid: str) -> list[dict]:
        return self.alternatives.find_by_concept(concept_uid)

    def get_advanced_versions(self, concept_uid: str) -> list[dict]:
        return self.deepens.find_by_concept(concept_uid)

    def remove_prerequisite(self, concept_uid: str, prerequisite_uid: str):
        self.requires.delete(concept_uid, prerequisite_uid)

    def remove_correlation(self, concept_a_uid: str, concept_b_uid: str):
        self.correlates.delete(concept_a_uid, concept_b_uid)

    def remove_alternative(self, concept_uid: str, alternative_uid: str):
        self.alternatives.delete(concept_uid, alternative_uid)

    def remove_advanced_version(self, advanced_uid: str, foundational_uid: str):
        self.deepens.delete(advanced_uid, foundational_uid)
