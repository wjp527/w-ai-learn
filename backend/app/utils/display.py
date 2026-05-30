from datetime import datetime, timedelta, timezone


def format_duration_seconds(seconds: int) -> str:
    minutes = seconds // 60
    remain = seconds % 60
    if minutes <= 0:
        return f"{remain}秒"
    return f"{minutes}分{remain}秒"


def format_total_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0h"
    hours = seconds / 3600
    if hours >= 1:
        rounded = round(hours, 1)
        if rounded.is_integer():
            return f"{int(rounded)}h"
        return f"{rounded}h"
    minutes = max(1, seconds // 60)
    return f"{minutes}m"


def truncate_title(source_text: str, max_len: int = 20) -> str:
    cleaned = source_text.strip()
    if len(cleaned) <= max_len:
        return cleaned or "未命名题目集"
    return cleaned[:max_len] + "…"


def infer_subject_icon(title: str) -> str:
    stripped = title.strip()
    if not stripped:
        return "学"
    return stripped[0]


def format_relative_datetime(value: datetime, *, now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    local_value = value.astimezone(timezone(timedelta(hours=8)))
    local_now = current.astimezone(timezone(timedelta(hours=8)))

    if local_value.date() == local_now.date():
        return f"今天 {local_value.strftime('%H:%M')}"

    yesterday = local_now.date() - timedelta(days=1)
    if local_value.date() == yesterday:
        return f"昨天 {local_value.strftime('%H:%M')}"

    if local_value.year == local_now.year:
        return f"{local_value.month}月{local_value.day}日 {local_value.strftime('%H:%M')}"

    return local_value.strftime("%Y年%m月%d日 %H:%M")


def format_full_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    local_value = value.astimezone(timezone(timedelta(hours=8)))
    return local_value.strftime("%Y年%m月%d日 %H:%M")


def format_created_date(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    local_value = value.astimezone(timezone(timedelta(hours=8)))
    return f"{local_value.month}月{local_value.day}日生成"


def infer_type_label(questions: list[dict]) -> str:
    has_single = any(item.get("type") == "single_choice" for item in questions)
    has_tf = any(item.get("type") == "true_false" for item in questions)
    if has_single and has_tf:
        return "单选/判断"
    if has_single:
        return "单选"
    if has_tf:
        return "判断"
    return "综合"
