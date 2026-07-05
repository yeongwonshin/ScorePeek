from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CourseConfig(BaseModel):
    """Course configuration used for demo enrollment verification."""

    course_id: str = Field(..., description="Stable course identifier, e.g. CSE101-2026S")
    title: str
    instructor: str = "TBD"
    semester: str = "TBD"
    access_key_hash: str = Field(..., description="SHA-256 hash of the demo course access key")
    max_score: float = Field(default=100, gt=0)
    min_anonymous_count: int = Field(default=1, ge=1)


class VerifyRequest(BaseModel):
    course_id: str
    access_key: str = Field(..., min_length=1)


class VerifyResponse(BaseModel):
    verified: bool
    course: CourseConfig | None = None
    message: str


class ScoreSubmission(BaseModel):
    course_id: str
    assessment: str = Field(default="midterm", min_length=1, max_length=80)
    score: float = Field(..., ge=0)
    max_score: float = Field(default=100, gt=0)
    student_private_key: str = Field(
        ...,
        min_length=4,
        description="Private value used only for salted hashing and score updates. Raw value is never stored.",
    )

    @field_validator("assessment")
    @classmethod
    def normalize_assessment(cls, value: str) -> str:
        return " ".join(value.strip().lower().split())

    @field_validator("score")
    @classmethod
    def score_must_be_reasonable(cls, value: float) -> float:
        if value > 10000:
            raise ValueError("score is too large")
        return value

    def normalized_score(self) -> float:
        return round((self.score / self.max_score) * 100, 4)


class ScoreRecord(BaseModel):
    course_id: str
    assessment: str
    participant_hash: str
    score: float
    max_score: float
    normalized_score: float
    created_at: datetime
    updated_at: datetime


class HistogramBin(BaseModel):
    label: str
    lower: float
    upper: float
    count: int


class ScoreSummary(BaseModel):
    course_id: str
    assessment: str
    count: int
    mean: float | None = None
    median: float | None = None
    stdev: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    my_score: float | None = None
    my_percentile: float | None = None
    my_estimated_rank: int | None = None
    privacy_status: Literal["ok", "insufficient_samples"] = "ok"
    message: str
    histogram: list[HistogramBin] = Field(default_factory=list)
