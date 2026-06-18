
class MatesService:
    def __init__(self, curriculum_repo: CurriculumRepository, materia_estudiante_repo: MateriaEstudianteRepository):
        pass

    def get_student_mates(self, id_estudiante: str) -> list[dict]:
        pass

    def suggested_mates(self, id_estudiante: str) -> list[dict]:
        pass

    def send_mate_request(self, student_id_a: str, student_id_b: str) -> None:
        pass


    