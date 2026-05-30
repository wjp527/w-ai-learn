from app.llm.json_utils import strip_option_label
from app.schemas.session import Question, QuestionType

_TRUE_FALSE_POSITIVE = {"对", "是", "正确", "true", "yes", "√", "✓"}
_TRUE_FALSE_NEGATIVE = {"错", "否", "错误", "false", "no", "×", "✗"}
_SINGLE_CHOICE_FILLERS = ("以上都不对", "其他选项", "无法确定", "与此无关")


def validate_questions(questions: list[Question], expected_count: int) -> str | None:
    if len(questions) != expected_count:
        return f"题目数量应为 {expected_count} 道，实际为 {len(questions)} 道"

    for question in questions:
        if not question.stem.strip():
            return "题目题干不能为空"
        if not question.source_evidence.strip():
            return "每道题必须包含原文依据"
        if not question.explanation.strip():
            return "每道题必须包含讲解"

        if question.type == QuestionType.SINGLE_CHOICE:
            if len(question.options) != 4:
                return "单选题必须包含 4 个选项"
            if question.correct_answer not in question.options:
                return "单选题正确答案必须来自选项"
        elif question.type == QuestionType.TRUE_FALSE:
            allowed = {"对", "错"}
            if set(question.options) != allowed:
                return "判断题选项必须为「对」和「错」"
            if question.correct_answer not in allowed:
                return "判断题正确答案必须为「对」或「错」"

    return None


def repair_questions(questions: list[Question]) -> list[Question]:
    repaired = [_repair_question(question) for question in questions]
    return [_force_valid_question(question) for question in repaired]


def _repair_question(question: Question) -> Question:
    options = _dedupe_options([strip_option_label(option) for option in question.options if str(option).strip()])
    correct = _align_correct_answer(question.correct_answer, options)

    if question.type == QuestionType.TRUE_FALSE:
        mapped = _map_to_true_false_value(correct)
        if mapped is None and correct in {"对", "错"}:
            mapped = correct
        return question.model_copy(
            update={
                "options": ["对", "错"],
                "correct_answer": mapped or "对",
            }
        )

    if len(options) == 0:
        return _fallback_to_true_false(question, correct)

    if len(options) > 4:
        options = _trim_to_four_options(options, correct)
        correct = _align_correct_answer(correct, options)
    elif len(options) == 2:
        mapped_correct = _map_to_true_false_value(correct)
        if mapped_correct is None:
            for option in options:
                if option == correct or correct in option or option in correct:
                    mapped_correct = _map_to_true_false_value(option)
                    break
        if mapped_correct is not None:
            return question.model_copy(
                update={
                    "type": QuestionType.TRUE_FALSE,
                    "options": ["对", "错"],
                    "correct_answer": mapped_correct,
                }
            )

    return question.model_copy(update={"options": options, "correct_answer": correct})


def _force_valid_question(question: Question) -> Question:
    if question.type == QuestionType.TRUE_FALSE:
        mapped = _map_to_true_false_value(question.correct_answer)
        if mapped is None and question.correct_answer in {"对", "错"}:
            mapped = question.correct_answer
        return question.model_copy(
            update={
                "options": ["对", "错"],
                "correct_answer": mapped or "对",
            }
        )

    options = _dedupe_options(list(question.options))
    correct = _align_correct_answer(question.correct_answer, options)

    if correct and correct not in options:
        options.insert(0, correct)

    for filler in _SINGLE_CHOICE_FILLERS:
        if len(options) >= 4:
            break
        if filler not in options:
            options.append(filler)

    while len(options) < 4:
        placeholder = f"备选项{len(options) + 1}"
        if placeholder not in options:
            options.append(placeholder)

    if len(options) > 4:
        options = _trim_to_four_options(options, correct)

    correct = _align_correct_answer(correct, options)
    if correct not in options:
        correct = options[0]

    return question.model_copy(update={"options": options[:4], "correct_answer": correct})


def _fallback_to_true_false(question: Question, correct: str) -> Question:
    mapped = _map_to_true_false_value(correct)
    return question.model_copy(
        update={
            "type": QuestionType.TRUE_FALSE,
            "options": ["对", "错"],
            "correct_answer": mapped or "对",
        }
    )


def _dedupe_options(options: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for option in options:
        if option and option not in seen:
            seen.add(option)
            result.append(option)
    return result


def _align_correct_answer(correct: str, options: list[str]) -> str:
    correct = strip_option_label(correct)
    if correct in options:
        return correct

    if correct.isdigit():
        index = int(correct)
        if 0 <= index < len(options):
            return options[index]

    if len(correct) == 1 and correct.upper() in "ABCD":
        index = ord(correct.upper()) - ord("A")
        if 0 <= index < len(options):
            return options[index]

    for option in options:
        if option == correct or option in correct or correct in option:
            return option

    return correct


def _trim_to_four_options(options: list[str], correct: str) -> list[str]:
    if len(options) <= 4:
        return options

    correct = _align_correct_answer(correct, options)
    trimmed: list[str] = []
    if correct in options:
        trimmed.append(correct)
    for option in options:
        if len(trimmed) >= 4:
            break
        if option not in trimmed:
            trimmed.append(option)
    if len(trimmed) < 4:
        trimmed = options[:4]
    return trimmed[:4]


def _map_to_true_false_value(value: str) -> str | None:
    normalized = strip_option_label(value)
    lowered = normalized.lower()
    if normalized in _TRUE_FALSE_POSITIVE or lowered in _TRUE_FALSE_POSITIVE:
        return "对"
    if normalized in _TRUE_FALSE_NEGATIVE or lowered in _TRUE_FALSE_NEGATIVE:
        return "错"
    return None
