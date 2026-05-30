import pytest

from app.schemas.session import Question, QuestionType


def build_single_choice() -> Question:
    return Question(
        id="q1",
        type=QuestionType.SINGLE_CHOICE,
        stem="赤壁之战发生于哪一年？",
        options=["208年", "220年", "200年", "189年"],
        correctAnswer="208年",
        explanation="原文记载208年。",
        sourceEvidence="赤壁之战发生于208年",
    )


def build_true_false() -> Question:
    return Question(
        id="q2",
        type=QuestionType.TRUE_FALSE,
        stem="赤壁之战后三国鼎立局面初步形成。",
        options=["对", "错"],
        correctAnswer="对",
        explanation="原文有明确描述。",
        sourceEvidence="三国鼎立的局面初步形成",
    )


def test_validate_questions_rejects_wrong_count():
    from app.utils.question_validator import validate_questions

    assert validate_questions([build_single_choice()], 2) == "题目数量应为 2 道，实际为 1 道"


def test_validate_questions_rejects_invalid_true_false_options():
    from app.utils.question_validator import validate_questions

    question = build_true_false()
    question.options = ["是", "否"]
    assert validate_questions([question], 1) == "判断题选项必须为「对」和「错」"


def test_validate_questions_accepts_valid_set():
    from app.utils.question_validator import validate_questions

    assert validate_questions([build_single_choice(), build_true_false()], 2) is None


def test_repair_questions_pads_three_single_choice_options():
    from app.utils.question_validator import repair_questions, validate_questions

    question = build_single_choice()
    question.options = ["208年", "220年", "200年"]
    repaired = repair_questions([question])
    assert validate_questions(repaired, 1) is None
    assert len(repaired[0].options) == 4


def test_repair_questions_trims_extra_single_choice_options():
    from app.utils.question_validator import repair_questions, validate_questions

    question = build_single_choice()
    question.options = ["208年", "220年", "200年", "189年", "180年"]
    repaired = repair_questions([question])
    assert validate_questions(repaired, 1) is None
    assert len(repaired[0].options) == 4
    assert repaired[0].correct_answer in repaired[0].options


def test_repair_questions_converts_two_options_to_true_false():
    from app.utils.question_validator import repair_questions, validate_questions

    question = build_single_choice()
    question.options = ["是", "否"]
    question.correct_answer = "是"
    repaired = repair_questions([question])
    assert repaired[0].type == QuestionType.TRUE_FALSE
    assert validate_questions(repaired, 1) is None


def test_repair_questions_pads_one_option_single_choice():
    from app.utils.question_validator import repair_questions, validate_questions

    question = build_single_choice()
    question.options = ["208年"]
    question.correct_answer = "208年"
    repaired = repair_questions([question])
    assert repaired[0].type == QuestionType.SINGLE_CHOICE
    assert validate_questions(repaired, 1) is None
    assert len(repaired[0].options) == 4


def test_repair_questions_converts_empty_options_to_true_false():
    from app.utils.question_validator import repair_questions, validate_questions

    question = build_single_choice()
    question.options = []
    repaired = repair_questions([question])
    assert repaired[0].type == QuestionType.TRUE_FALSE
    assert validate_questions(repaired, 1) is None


def test_repair_questions_aligns_letter_correct_answer():
    from app.utils.question_validator import repair_questions, validate_questions

    question = build_single_choice()
    question.correct_answer = "B"
    repaired = repair_questions([question])
    assert validate_questions(repaired, 1) is None
    assert repaired[0].correct_answer == "220年"
