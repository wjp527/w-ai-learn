import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel

from app.schemas.session import QuestionType

_OPTION_LABEL_RE = re.compile(r"^[A-Da-d][\.、\)\:]?\s*")
_INLINE_OPTION_SPLIT_RE = re.compile(r"(?=[A-Da-d][\.、\)\:])")

T = TypeVar("T", bound=BaseModel)


def extract_json_object(text: str) -> dict[str, Any]:
    content = text.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            raise
        return json.loads(match.group())


def normalize_knowledge_payload(data: dict[str, Any]) -> dict[str, Any]:
    points = data.get("knowledgePoints") or data.get("knowledge_points") or []
    normalized_points: list[dict[str, Any]] = []

    for index, item in enumerate(points):
        if not isinstance(item, dict):
            continue
        normalized_points.append(
            {
                "id": str(item.get("id", index + 1)),
                "title": str(item.get("title", "")).strip(),
                "description": str(item.get("description", "")).strip(),
                "sourceEvidence": str(
                    item.get("sourceEvidence") or item.get("source_evidence") or ""
                ).strip(),
            }
        )

    return {
        "knowledgePoints": normalized_points,
        "summary": str(data.get("summary", "")).strip(),
    }


def strip_option_label(text: str) -> str:
    stripped = text.strip()
    match = _OPTION_LABEL_RE.match(stripped)
    if match and stripped[match.end() :].strip():
        return stripped[match.end() :].strip()
    return stripped


def _split_option_string(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []

    if any(separator in stripped for separator in ("\n", "|", "；", ";", "，", ",")):
        parts = re.split(r"[\n|；;,，]+", stripped)
        return [strip_option_label(part) for part in parts if part.strip()]

    inline_parts = [part for part in _INLINE_OPTION_SPLIT_RE.split(stripped) if part.strip()]
    if len(inline_parts) > 1:
        return [strip_option_label(part) for part in inline_parts]

    return [strip_option_label(stripped)]


def normalize_options(raw: Any) -> list[str]:
    options: list[str] = []

    if isinstance(raw, dict):
        keys = list(raw.keys())
        if keys and all(str(key).strip().upper() in {"A", "B", "C", "D", "E"} for key in keys):
            keys = sorted(keys, key=lambda key: str(key).strip().upper())
        for key in keys:
            value = str(raw[key]).strip()
            if value:
                options.append(strip_option_label(value))
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                text = str(item.get("text") or item.get("content") or item.get("value") or "").strip()
                if not text:
                    text = str(item.get("label") or "").strip()
            else:
                text = str(item).strip()
            if text:
                options.append(strip_option_label(text))
    elif isinstance(raw, str) and raw.strip():
        options = _split_option_string(raw)

    seen: set[str] = set()
    deduped: list[str] = []
    for option in options:
        if option and option not in seen:
            seen.add(option)
            deduped.append(option)
    return deduped


def normalize_question_type(value: Any) -> str:
    raw = str(value or "").strip().lower()
    mapping = {
        "single_choice": QuestionType.SINGLE_CHOICE.value,
        "single choice": QuestionType.SINGLE_CHOICE.value,
        "single": QuestionType.SINGLE_CHOICE.value,
        "单选": QuestionType.SINGLE_CHOICE.value,
        "单选题": QuestionType.SINGLE_CHOICE.value,
        "true_false": QuestionType.TRUE_FALSE.value,
        "true false": QuestionType.TRUE_FALSE.value,
        "boolean": QuestionType.TRUE_FALSE.value,
        "判断": QuestionType.TRUE_FALSE.value,
        "判断题": QuestionType.TRUE_FALSE.value,
    }
    return mapping.get(raw, QuestionType.SINGLE_CHOICE.value)


def normalize_questions_payload(data: dict[str, Any]) -> dict[str, Any]:
    questions = data.get("questions") or []
    normalized: list[dict[str, Any]] = []

    for index, item in enumerate(questions):
        if not isinstance(item, dict):
            continue

        q_type = normalize_question_type(item.get("type"))
        options = normalize_options(item.get("options"))

        if q_type == QuestionType.TRUE_FALSE.value:
            options = ["对", "错"]

        correct = strip_option_label(
            str(item.get("correctAnswer") or item.get("correct_answer") or "").strip()
        )
        if q_type == QuestionType.TRUE_FALSE.value and correct in {"true", "True", "正确"}:
            correct = "对"
        if q_type == QuestionType.TRUE_FALSE.value and correct in {"false", "False", "错误"}:
            correct = "错"

        normalized.append(
            {
                "id": str(item.get("id", index + 1)),
                "type": q_type,
                "stem": str(item.get("stem", "")).strip(),
                "options": options,
                "correctAnswer": correct,
                "explanation": str(item.get("explanation", "")).strip(),
                "sourceEvidence": str(
                    item.get("sourceEvidence") or item.get("source_evidence") or ""
                ).strip(),
            }
        )

    return {"questions": normalized}


def normalize_report_payload(data: dict[str, Any]) -> dict[str, Any]:
    weak_points = data.get("weakPoints") or data.get("weak_points") or []
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    return {
        "weakPoints": [str(item).strip() for item in weak_points if str(item).strip()],
        "summary": str(data.get("summary", "")).strip(),
    }


def parse_model(model: type[T], data: dict[str, Any]) -> T:
    return model.model_validate(data)
