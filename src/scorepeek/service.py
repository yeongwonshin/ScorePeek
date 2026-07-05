from __future__ import annotations

from pathlib import Path

from .auth import CourseRegistry, hash_participant
from .models import ScoreSubmission, ScoreSummary, VerifyResponse
from .stats import compute_summary
from .storage import ScoreStore


class ScorePeekService:
    """Application service for anonymous score submissions and score distributions."""

    def __init__(
        self,
        courses_path: str | Path = "data/courses.json",
        db_path: str | Path | None = None,
    ):
        self.registry = CourseRegistry(courses_path)
        self.store = ScoreStore(db_path)

    def list_courses(self) -> list[dict]:
        return [course.model_dump(exclude={"access_key_hash"}) for course in self.registry.list_courses()]

    def verify_course(self, course_id: str, access_key: str) -> VerifyResponse:
        course = self.registry.verify(course_id, access_key)
        if not course:
            return VerifyResponse(verified=False, course=None, message="Course verification failed.")
        return VerifyResponse(verified=True, course=course, message="Course verification succeeded.")

    def submit_score(self, submission: ScoreSubmission) -> dict:
        course = self.registry.get(submission.course_id)
        if not course:
            raise ValueError("Unknown course_id")
        participant_hash = hash_participant(submission.course_id, submission.student_private_key)
        record = self.store.upsert_score(submission, participant_hash)
        records = self.store.list_scores(submission.course_id, submission.assessment)
        summary = compute_summary(
            submission.course_id,
            submission.assessment,
            records,
            my_score=record.normalized_score,
            min_anonymous_count=course.min_anonymous_count,
        )
        return {"record": record.model_dump(exclude={"participant_hash"}), "summary": summary.model_dump()}

    def report(self, course_id: str, assessment: str, student_private_key: str | None = None) -> ScoreSummary:
        course = self.registry.get(course_id)
        if not course:
            raise ValueError("Unknown course_id")
        assessment = " ".join(assessment.strip().lower().split())
        my_score = None
        if student_private_key:
            participant_hash = hash_participant(course_id, student_private_key)
            try:
                my_score = self.store.get_score(course_id, assessment, participant_hash).normalized_score
            except KeyError:
                my_score = None
        records = self.store.list_scores(course_id, assessment)
        return compute_summary(course_id, assessment, records, my_score, course.min_anonymous_count)
