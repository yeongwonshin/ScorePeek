from __future__ import annotations

from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    """Minimal student profile used for personalized academic/admin decisions."""

    grade: int = Field(default=1, ge=1, le=8, description="학년")
    major: str = Field(default="미지정", description="전공")
    completed_credits: int = Field(default=0, ge=0, description="총 이수학점")
    major_required_credits: int = Field(default=0, ge=0, description="전공필수 이수학점")
    major_elective_credits: int = Field(default=0, ge=0, description="전공선택 이수학점")
    general_education_credits: int = Field(default=0, ge=0, description="교양 이수학점")
    leave_count: int = Field(default=0, ge=0, description="휴학 이력 횟수")
    scholarship_status: str = Field(default="none", description="장학 상태")

    def to_korean_lines(self) -> list[str]:
        return [
            f"학년: {self.grade}",
            f"전공: {self.major}",
            f"총 이수학점: {self.completed_credits}",
            f"전공필수 이수학점: {self.major_required_credits}",
            f"전공선택 이수학점: {self.major_elective_credits}",
            f"교양 이수학점: {self.general_education_credits}",
            f"휴학 이력: {self.leave_count}",
            f"장학 상태: {self.scholarship_status}",
        ]
