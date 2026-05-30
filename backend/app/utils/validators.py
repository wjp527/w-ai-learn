import re

from app.config import settings


def clean_source_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def validate_source_text(text: str) -> str | None:
    cleaned = clean_source_text(text)
    length = len(cleaned)
    if length < settings.min_source_text_length:
        return f"文本过短，至少需要 {settings.min_source_text_length} 字"
    if length > settings.max_source_text_length:
        return f"文本过长，最多支持 {settings.max_source_text_length} 字"
    return None


def validate_question_count(count: int) -> str | None:
    if count < settings.min_question_count or count > settings.max_question_count:
        return f"题目数量需在 {settings.min_question_count}~{settings.max_question_count} 之间"
    return None
