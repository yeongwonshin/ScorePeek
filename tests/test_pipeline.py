from src.admin_ai.pipeline import AdminAIAgent
from src.admin_ai.profile import StudentProfile


def test_graduation_question_returns_checklist():
    agent = AdminAIAgent("data/sample_documents", "data/policies/rules.json")
    profile = StudentProfile(
        grade=4,
        major="컴퓨터공학",
        completed_credits=118,
        major_required_credits=30,
        major_elective_credits=24,
        general_education_credits=28,
        leave_count=1,
        scholarship_status="none",
    )
    result = agent.ask("컴공 4학년인데 졸업까지 뭐가 남았어?", profile)
    assert "졸업요건" in result["answer"]
    assert result["checklist"]
    assert result["email_draft"].startswith("제목:")
    assert result["evidence"]


def test_leave_question_returns_documents():
    agent = AdminAIAgent("data/sample_documents", "data/policies/rules.json")
    profile = StudentProfile(grade=2, major="경영학", leave_count=3)
    result = agent.ask("이번 학기 휴학 가능해?", profile)
    assert any("휴학" in item for item in result["checklist"])
    assert result["calendar_items"]
