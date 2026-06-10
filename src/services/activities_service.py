"""Activity service — activity creation and completion tracking."""

from neo4j import Driver
from src.models.node_models import Activity
from src.models.relationship_models import Completes
from src.repositories.neo4j.nodes.activity_repository import ActivityNodeRepo
from src.repositories.neo4j.relationships.completes_repository import CompletesRepo


class ActivityService:
    def __init__(self, driver: Driver):
        self.activities = ActivityNodeRepo(driver)
        self.completes = CompletesRepo(driver)

    def create_activity(self, activity: Activity) -> dict:
        return self.activities.create(activity)

    def complete(self, student_uid: str, activity_uid: str, rel: Completes):
        self.completes.create(student_uid, activity_uid, rel)

    def get_student_completions(self, student_uid: str) -> list[dict]:
        return self.completes.find_by_student(student_uid)

    def get_by_type(self, type: str) -> list[dict]:
        return self.activities.find_by_type(type)

    def remove_completion(self, student_uid: str, activity_uid: str):
        self.completes.delete(student_uid, activity_uid)
