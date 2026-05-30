from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.llm.json_utils import (
    extract_json_object,
    normalize_knowledge_payload,
    normalize_questions_payload,
    normalize_report_payload,
    parse_model,
)
from app.schemas.session import (
    KnowledgePoint,
    Question,
    StudyReport,
    WrongQuestionSummary,
)
from app.services.generation_protocol import GenerationService


class KnowledgeExtractionResult:
    def __init__(self, knowledge_points: list[KnowledgePoint], summary: str) -> None:
        self.knowledge_points = knowledge_points
        self.summary = summary


def create_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.2,
        max_tokens=4096,
    )


class LangChainGenerationService(GenerationService):
    def __init__(self, llm: ChatOpenAI | None = None) -> None:
        self._llm = llm or create_llm()

    async def _call_json(self, system: str, user: str) -> dict[str, Any]:
        response = await self._llm.ainvoke(
            [
                SystemMessage(content=system),
                HumanMessage(content=user),
            ],
            response_format={"type": "json_object"},
        )
        content = response.content
        if isinstance(content, list):
            content = "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        if not isinstance(content, str) or not content.strip():
            raise ValueError("模型返回了空内容，请稍后重试")
        return extract_json_object(content)

    async def extract_and_generate(
        self, source_text: str, question_count: int, *, retry_hint: str | None = None
    ) -> tuple[list[KnowledgePoint], list[Question]]:
        knowledge_result = await self._extract_knowledge(source_text)
        questions = await self._generate_questions(
            source_text,
            knowledge_result.knowledge_points,
            question_count,
            retry_hint=retry_hint,
        )
        return knowledge_result.knowledge_points, questions

    async def _extract_knowledge(self, source_text: str) -> KnowledgeExtractionResult:
        system = (
            "你是严谨的学习内容分析助手。只能基于用户提供的原文提取知识点，禁止扩写或引入原文没有的信息。"
            "必须输出合法 json 对象，字段为 knowledgePoints 和 summary。"
            "knowledgePoints 是数组，每项包含 id(字符串)、title、description、sourceEvidence。"
            '示例: {"knowledgePoints":[{"id":"kp1","title":"标题","description":"描述","sourceEvidence":"原文片段"}],"summary":"总结"}'
        )
        user = f"原文：\n{source_text}"
        raw = await self._call_json(system, user)
        normalized = normalize_knowledge_payload(raw)

        from pydantic import BaseModel, Field

        class _Result(BaseModel):
            knowledge_points: list[KnowledgePoint] = Field(alias="knowledgePoints")
            summary: str

            model_config = {"populate_by_name": True}

        parsed = parse_model(_Result, normalized)
        return KnowledgeExtractionResult(parsed.knowledge_points, parsed.summary)

    async def _generate_questions(
        self,
        source_text: str,
        knowledge_points: list[KnowledgePoint],
        question_count: int,
        retry_hint: str | None = None,
    ) -> list[Question]:
        knowledge_text = "\n".join(
            f"- {item.title}: {item.description}" for item in knowledge_points
        )
        system = (
            "你是出题助手。只能基于原文和知识点出题。"
            "题型 type 只能是 single_choice 或 true_false。"
            "单选题 type=single_choice，options 必须恰好 4 个字符串，不能多也不能少；"
            '判断题 type=true_false，options 必须恰好是 ["对","错"]；'
            "correctAnswer 必须与 options 中某一项完全一致。"
            "每题必须有 id(字符串)、stem、options、correctAnswer、explanation、sourceEvidence。"
            "必须输出合法 json 对象，字段 questions 为数组。"
            f"请生成恰好 {question_count} 道题，建议单选与判断题混合。"
            '示例: {"questions":[{"id":"q1","type":"single_choice","stem":"题干","options":["A项","B项","C项","D项"],"correctAnswer":"A项","explanation":"讲解","sourceEvidence":"原文片段"}]}'
        )
        user = f"原文：\n{source_text}\n\n知识点：\n{knowledge_text}"
        if retry_hint:
            user += f"\n\n上次生成未通过校验，请严格修正：{retry_hint}"
        raw = await self._call_json(system, user)
        normalized = normalize_questions_payload(raw)

        from pydantic import BaseModel

        class _Result(BaseModel):
            questions: list[Question]

        parsed = parse_model(_Result, normalized)
        return parsed.questions

    async def generate_report(
        self,
        source_text: str,
        knowledge_points: list[KnowledgePoint],
        questions: list[Question],
        answer_records: list,
    ) -> StudyReport:
        total = len(questions)
        correct_count = sum(1 for item in answer_records if item.is_correct)
        accuracy = round((correct_count / total) * 100, 1) if total else 0.0

        wrong_questions: list[WrongQuestionSummary] = []
        for record in answer_records:
            if record.is_correct:
                continue
            question = next(item for item in questions if item.id == record.question_id)
            wrong_questions.append(
                WrongQuestionSummary(
                    question_id=question.id,
                    stem=question.stem,
                    selected_answer=record.selected_answer,
                    correct_answer=question.correct_answer,
                )
            )

        knowledge_text = "\n".join(
            f"- {item.title}: {item.description}" for item in knowledge_points
        )
        answer_text = "\n".join(
            f"- {item.question_id}: {'正确' if item.is_correct else '错误'}"
            for item in answer_records
        )
        system = (
            "你是学习报告助手。根据答题表现生成 weakPoints 和 summary，语气中性。"
            "必须输出合法 json，包含 weakPoints(字符串数组) 和 summary(字符串)。"
        )
        user = (
            f"原文：\n{source_text}\n\n知识点：\n{knowledge_text}\n\n答题记录：\n{answer_text}"
        )
        raw = await self._call_json(system, user)
        normalized = normalize_report_payload(raw)

        from pydantic import BaseModel, Field

        class _Result(BaseModel):
            weak_points: list[str] = Field(alias="weakPoints")
            summary: str

            model_config = {"populate_by_name": True}

        ai_report = parse_model(_Result, normalized)

        return StudyReport(
            accuracy=accuracy,
            total_questions=total,
            correct_count=correct_count,
            wrong_questions=wrong_questions,
            weak_points=ai_report.weak_points,
            summary=ai_report.summary,
            duration_seconds=0,
        )

    async def generate_title(self, source_text: str) -> str:
        system = (
            "你是学习助手。根据用户学习文本生成一个简短中文标题，不超过 20 字，不要引号。"
            "必须输出合法 json，包含 title 字段。"
        )
        user = f"学习文本：\n{source_text[:500]}"
        raw = await self._call_json(system, user)
        title = raw.get("title")
        if not isinstance(title, str):
            raise ValueError("标题生成失败")
        return title.strip()
