from typing import Protocol

from app.schemas.session import KnowledgePoint, Question, StudyReport


class GenerationService(Protocol):
    async def extract_and_generate(
        self,
        source_text: str,
        question_count: int,
        *,
        retry_hint: str | None = None,
    ) -> tuple[list[KnowledgePoint], list[Question]]:
        ...

    async def generate_report(
        self,
        source_text: str,
        knowledge_points: list[KnowledgePoint],
        questions: list[Question],
        answer_records: list,
    ) -> StudyReport:
        ...

    async def generate_title(self, source_text: str) -> str:
        ...
