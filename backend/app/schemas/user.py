from datetime import datetime

from pydantic import BaseModel, Field


class UserStatsResponse(BaseModel):
    total_sessions: int = Field(alias="totalSessions")
    average_accuracy: int = Field(alias="averageAccuracy")
    total_duration_seconds: int = Field(alias="totalDurationSeconds")
    total_duration_display: str = Field(alias="totalDurationDisplay")

    model_config = {"populate_by_name": True}


class StudyRecordListItem(BaseModel):
    id: str
    title: str
    subject_icon: str = Field(alias="subjectIcon")
    finished_at: datetime = Field(alias="finishedAt")
    finished_at_display: str = Field(alias="finishedAtDisplay")
    duration_seconds: int = Field(alias="durationSeconds")
    duration_display: str = Field(alias="durationDisplay")
    accuracy: float
    correct_count: int = Field(alias="correctCount")
    total_questions: int = Field(alias="totalQuestions")

    model_config = {"populate_by_name": True}


class PaginatedStudyRecordsResponse(BaseModel):
    items: list[StudyRecordListItem]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    model_config = {"populate_by_name": True}


class WrongQuestionDetail(BaseModel):
    question_id: str = Field(alias="questionId")
    stem: str
    selected_answer: str = Field(alias="selectedAnswer")
    correct_answer: str = Field(alias="correctAnswer")

    model_config = {"populate_by_name": True}


class StudyRecordDetailResponse(BaseModel):
    id: str
    title: str
    accuracy: float
    correct_count: int = Field(alias="correctCount")
    total_questions: int = Field(alias="totalQuestions")
    duration_seconds: int = Field(alias="durationSeconds")
    duration_display: str = Field(alias="durationDisplay")
    finished_at: datetime = Field(alias="finishedAt")
    finished_at_display: str = Field(alias="finishedAtDisplay")
    wrong_questions: list[WrongQuestionDetail] = Field(alias="wrongQuestions")
    summary: str
    question_set_id: str = Field(alias="questionSetId")

    model_config = {"populate_by_name": True}


class QuestionPreview(BaseModel):
    id: str
    type: str
    stem: str
    options: list[str]

    model_config = {"populate_by_name": True}


class QuestionSetListItem(BaseModel):
    id: str
    title: str
    question_count: int = Field(alias="questionCount")
    type_label: str = Field(alias="typeLabel")
    created_at: datetime = Field(alias="createdAt")
    created_at_display: str = Field(alias="createdAtDisplay")
    practice_status: str = Field(alias="practiceStatus")
    last_accuracy: float | None = Field(default=None, alias="lastAccuracy")
    badge: str

    model_config = {"populate_by_name": True}


class PaginatedQuestionSetsResponse(BaseModel):
    items: list[QuestionSetListItem]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    model_config = {"populate_by_name": True}


class QuestionSetDetailResponse(BaseModel):
    id: str
    title: str
    questions: list[QuestionPreview]

    model_config = {"populate_by_name": True}


class PracticeResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    status: str

    model_config = {"populate_by_name": True}


class ResumeResponse(BaseModel):
    has_resume: bool = Field(alias="hasResume")
    type: str = "none"
    session_id: str | None = Field(default=None, alias="sessionId")
    title: str | None = None
    answered_count: int | None = Field(default=None, alias="answeredCount")
    total_questions: int | None = Field(default=None, alias="totalQuestions")
    accuracy: float | None = None
    updated_at_display: str | None = Field(default=None, alias="updatedAtDisplay")

    model_config = {"populate_by_name": True}
