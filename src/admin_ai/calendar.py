from __future__ import annotations

from datetime import date, timedelta


def build_calendar_items(question: str, actions: list[str]) -> list[dict]:
    """Create simple calendar-like JSON items.

    In production, replace this with official academic calendar dates and Google/Outlook APIs.
    """
    today = date.today()
    items: list[dict] = []
    for idx, action in enumerate(actions[:5]):
        due = today + timedelta(days=idx + 1)
        items.append(
            {
                "title": action,
                "date": due.isoformat(),
                "description": f"질문 '{question}'에 대한 후속 조치",
                "source": "demo-generated",
            }
        )
    return items
