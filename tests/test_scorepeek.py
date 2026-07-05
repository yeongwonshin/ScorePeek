from pathlib import Path

from src.scorepeek.models import ScoreSubmission
from src.scorepeek.service import ScorePeekService


def make_service(tmp_path: Path) -> ScorePeekService:
    return ScorePeekService("data/courses.json", tmp_path / "scores.sqlite")


def test_course_verification_succeeds_and_fails(tmp_path):
    service = make_service(tmp_path)
    ok = service.verify_course("CSE101-2026S", "demo-cse101")
    bad = service.verify_course("CSE101-2026S", "wrong-key")
    assert ok.verified is True
    assert bad.verified is False


def test_submit_scores_returns_median_and_rank(tmp_path):
    service = make_service(tmp_path)
    for idx, score in enumerate([50, 70, 80, 90]):
        service.submit_score(
            ScoreSubmission(
                course_id="CSE101-2026S",
                assessment="midterm",
                score=score,
                max_score=100,
                student_private_key=f"student-{idx}",
            )
        )

    result = service.submit_score(
        ScoreSubmission(
            course_id="CSE101-2026S",
            assessment="midterm",
            score=85,
            max_score=100,
            student_private_key="myself-key",
        )
    )
    summary = result["summary"]
    assert summary["count"] == 5
    assert summary["median"] == 80
    assert summary["my_estimated_rank"] == 2
    assert summary["my_percentile"] == 80.0


def test_same_private_key_updates_instead_of_duplicate(tmp_path):
    service = make_service(tmp_path)
    payload = dict(
        course_id="CSE101-2026S",
        assessment="final",
        max_score=100,
        student_private_key="same-user",
    )
    service.submit_score(ScoreSubmission(score=60, **payload))
    service.submit_score(ScoreSubmission(score=95, **payload))
    report = service.report("CSE101-2026S", "final", "same-user")
    assert report.count == 1
    assert report.my_score == 95
    assert report.median == 95


def test_histogram_counts_all_scores(tmp_path):
    service = make_service(tmp_path)
    for idx, score in enumerate([5, 15, 15, 99]):
        service.submit_score(
            ScoreSubmission(
                course_id="CSE101-2026S",
                assessment="quiz1",
                score=score,
                max_score=100,
                student_private_key=f"hist-{idx}",
            )
        )
    report = service.report("CSE101-2026S", "quiz1")
    assert sum(item.count for item in report.histogram) == 4
