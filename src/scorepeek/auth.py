from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from .models import CourseConfig

DEFAULT_COURSES_PATH = Path("data/courses.json")
DEFAULT_SALT = "scorepeek-local-demo-salt"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_access_key(access_key: str) -> str:
    return sha256_text(access_key.strip())


def hash_participant(course_id: str, student_private_key: str, salt: str | None = None) -> str:
    """Create a stable anonymous participant hash for de-duplication.

    The raw student identifier or private key is never stored. In production,
    replace this demo input with SSO/LMS verification and store only the salted hash.
    """

    salt = salt or os.getenv("SCOREBOARD_SECRET_SALT", DEFAULT_SALT)
    normalized = f"{salt}:{course_id.strip().lower()}:{student_private_key.strip().lower()}"
    return sha256_text(normalized)


class CourseRegistry:
    def __init__(self, courses_path: str | Path = DEFAULT_COURSES_PATH):
        self.courses_path = Path(courses_path)
        self.courses = self._load()

    def _load(self) -> dict[str, CourseConfig]:
        if not self.courses_path.exists():
            return {}
        raw = json.loads(self.courses_path.read_text(encoding="utf-8"))
        courses = [CourseConfig(**item) for item in raw.get("courses", [])]
        return {course.course_id: course for course in courses}

    def list_courses(self) -> list[CourseConfig]:
        return list(self.courses.values())

    def get(self, course_id: str) -> CourseConfig | None:
        return self.courses.get(course_id)

    def verify(self, course_id: str, access_key: str) -> CourseConfig | None:
        course = self.get(course_id)
        if not course:
            return None
        if hash_access_key(access_key) != course.access_key_hash:
            return None
        return course
