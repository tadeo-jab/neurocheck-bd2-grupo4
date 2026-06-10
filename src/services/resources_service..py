"""Resource service — learning resources and concept coverage."""

from neo4j import Driver
from src.models.node_models import Resource
from src.models.relationship_models import Explains
from src.repositories.neo4j.nodes.resource_repository import ResourceNodeRepo
from src.repositories.neo4j.relationships.uses_repository import ExplainsRepo


class ResourceService:
    def __init__(self, driver: Driver):
        self.resources = ResourceNodeRepo(driver)
        self.explains = ExplainsRepo(driver)

    def create_resource(self, resource: Resource) -> dict:
        return self.resources.create(resource)

    def link_to_concept(self, resource_uid: str, concept_uid: str, rel: Explains):
        self.explains.create(resource_uid, concept_uid, rel)

    def get_concepts_explained_by(self, resource_uid: str) -> list[dict]:
        return self.explains.find_by_resource(resource_uid)

    def unlink_from_concept(self, resource_uid: str, concept_uid: str):
        self.explains.delete(resource_uid, concept_uid)
