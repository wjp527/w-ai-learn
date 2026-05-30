from app.llm.json_utils import normalize_knowledge_payload, normalize_options, normalize_questions_payload


def test_normalize_knowledge_coerces_numeric_id():
    data = {
        "knowledgePoints": [
            {
                "id": 1,
                "title": "赤壁之战时间",
                "description": "发生于208年",
                "sourceEvidence": "赤壁之战发生于208年",
            }
        ],
        "summary": "总结",
    }
    normalized = normalize_knowledge_payload(data)
    assert normalized["knowledgePoints"][0]["id"] == "1"


def test_normalize_questions_true_false_options():
    data = {
        "questions": [
            {
                "id": 2,
                "type": "判断题",
                "stem": "三国鼎立初步形成",
                "options": ["是", "否"],
                "correctAnswer": "true",
                "explanation": "原文有描述",
                "sourceEvidence": "三国鼎立",
            }
        ]
    }
    normalized = normalize_questions_payload(data)
    question = normalized["questions"][0]
    assert question["type"] == "true_false"
    assert question["options"] == ["对", "错"]
    assert question["correctAnswer"] == "对"


def test_normalize_options_from_dict():
    assert normalize_options({"A": "208年", "B": "220年", "C": "200年", "D": "189年"}) == [
        "208年",
        "220年",
        "200年",
        "189年",
    ]


def test_normalize_options_strips_labels():
    assert normalize_options(["A. 208年", "B. 220年", "C. 200年", "D. 189年"]) == [
        "208年",
        "220年",
        "200年",
        "189年",
    ]
    assert normalize_options(["A", "B", "C", "D"]) == ["A", "B", "C", "D"]


def test_normalize_questions_single_choice_dict_options():
    data = {
        "questions": [
            {
                "id": 1,
                "type": "single_choice",
                "stem": "赤壁之战发生于哪一年？",
                "options": {"A": "208年", "B": "220年", "C": "200年", "D": "189年"},
                "correctAnswer": "A",
                "explanation": "原文记载208年。",
                "sourceEvidence": "赤壁之战发生于208年",
            }
        ]
    }
    normalized = normalize_questions_payload(data)
    question = normalized["questions"][0]
    assert question["options"] == ["208年", "220年", "200年", "189年"]
    assert question["correctAnswer"] == "A"


def test_normalize_options_from_multiline_string():
    raw = "A. 208年\nB. 220年\nC. 200年\nD. 189年"
    assert normalize_options(raw) == ["208年", "220年", "200年", "189年"]


def test_normalize_options_from_inline_string():
    raw = "A. 208年 B. 220年 C. 200年 D. 189年"
    assert normalize_options(raw) == ["208年", "220年", "200年", "189年"]
