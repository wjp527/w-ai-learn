from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    TRUE_FALSE = "true_false"


class KnowledgePoint(BaseModel):
    id: str
    title: str
    description: str
    source_evidence: str = Field(alias="sourceEvidence")

    model_config = {"populate_by_name": True}


class Question(BaseModel):
    id: str
    type: QuestionType
    stem: str
    options: list[str]
    correct_answer: str = Field(alias="correctAnswer")
    explanation: str
    source_evidence: str = Field(alias="sourceEvidence")

    model_config = {"populate_by_name": True}


class AnswerRecord(BaseModel):
    question_id: str = Field(alias="questionId")
    selected_answer: str = Field(alias="selectedAnswer")
    is_correct: bool = Field(alias="isCorrect")
    answered_at: datetime = Field(alias="answeredAt")

    model_config = {"populate_by_name": True}


class WrongQuestionSummary(BaseModel):
    question_id: str = Field(alias="questionId")
    stem: str
    selected_answer: str = Field(alias="selectedAnswer")
    correct_answer: str = Field(alias="correctAnswer")

    model_config = {"populate_by_name": True}


class StudyReport(BaseModel):
    accuracy: float
    total_questions: int = Field(alias="totalQuestions")
    correct_count: int = Field(alias="correctCount")
    wrong_questions: list[WrongQuestionSummary] = Field(alias="wrongQuestions")
    weak_points: list[str] = Field(alias="weakPoints")
    summary: str
    duration_seconds: int = Field(alias="durationSeconds")

    model_config = {"populate_by_name": True}


class CreateSessionRequest(BaseModel):
    source_text: str = Field(alias="sourceText")
    question_count: int = Field(alias="questionCount", default=8)

    model_config = {"populate_by_name": True}


class CreateSessionResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    status: SessionStatus

    model_config = {"populate_by_name": True}


class SessionDetailResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    status: SessionStatus
    knowledge_points: list[KnowledgePoint] = Field(default_factory=list, alias="knowledgePoints")
    questions: list[Question] = Field(default_factory=list)
    error_message: str | None = Field(default=None, alias="errorMessage")

    model_config = {"populate_by_name": True}


class SubmitAnswerRequest(BaseModel):
    question_id: str = Field(alias="questionId")
    selected_answer: str = Field(alias="selectedAnswer")

    model_config = {"populate_by_name": True}


class SubmitAnswerResponse(BaseModel):
    is_correct: bool = Field(alias="isCorrect")
    correct_answer: str = Field(alias="correctAnswer")
    explanation: str
    source_evidence: str = Field(alias="sourceEvidence")

    model_config = {"populate_by_name": True}


class ReportResponse(StudyReport):
    pass
