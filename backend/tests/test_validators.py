import pytest

from app.utils.validators import clean_source_text, validate_question_count, validate_source_text


def test_clean_source_text_normalizes_whitespace():
    raw = "  赤壁之战   发生于208年 \n\n\n曹操南下"
    cleaned = clean_source_text(raw)
    assert cleaned == "赤壁之战 发生于208年 \n\n曹操南下"


def test_validate_source_text_rejects_too_short():
    assert validate_source_text("太短") == "文本过短，至少需要 5 字"


def test_validate_source_text_rejects_too_long():
    assert validate_source_text("a" * 2001) == "文本过长，最多支持 2000 字"


def test_validate_source_text_accepts_valid_length():
    assert validate_source_text("a" * 5) is None


def test_validate_question_count_rejects_out_of_range():
    assert validate_question_count(4) == "题目数量需在 5~10 之间"
    assert validate_question_count(11) == "题目数量需在 5~10 之间"


def test_validate_question_count_accepts_valid_range():
    assert validate_question_count(8) is None
