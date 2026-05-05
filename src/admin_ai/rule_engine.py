from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .profile import StudentProfile


@dataclass
class RuleFinding:
    category: str
    severity: str
    title: str
    detail: str
    actions: list[str]


class RuleEngine:
    def __init__(self, rules_path: str | Path):
        self.rules_path = Path(rules_path)
        self.rules = json.loads(self.rules_path.read_text(encoding="utf-8"))

    def evaluate(self, question: str, profile: StudentProfile) -> list[RuleFinding]:
        q = question.lower()
        findings: list[RuleFinding] = []

        if any(keyword in question for keyword in ["졸업", "이수", "학점", "수강 추천"]):
            findings.append(self._graduation(profile))

        if any(keyword in question for keyword in ["휴학", "복학"]):
            findings.append(self._leave_of_absence(profile))

        if any(keyword in question for keyword in ["장학", "장학금"]):
            findings.append(self._scholarship(profile))

        if any(keyword in question for keyword in ["수강정정", "정정", "수강신청", "증원"]):
            findings.append(self._course_correction(profile))

        if not findings:
            findings.append(
                RuleFinding(
                    category="general",
                    severity="info",
                    title="일반 학사·행정 문의",
                    detail="질문과 관련된 문서를 먼저 확인하고, 필요한 경우 담당 부서 문의 초안을 생성합니다.",
                    actions=["관련 공지 확인", "문의 대상 부서 확인", "필요 서류 여부 확인"],
                )
            )
        return findings

    def _graduation(self, profile: StudentProfile) -> RuleFinding:
        grad_rules = self.rules["graduation"]
        major_rules = grad_rules["major_overrides"].get(profile.major, {})
        required_total = major_rules.get("total_credits", grad_rules["default_total_credits"])
        required_major_req = major_rules.get("major_required_credits", grad_rules["default_major_required_credits"])
        required_major_ele = major_rules.get("major_elective_credits", grad_rules["default_major_elective_credits"])
        required_ge = major_rules.get("general_education_credits", grad_rules["default_general_education_credits"])

        gaps = {
            "총 이수학점": max(0, required_total - profile.completed_credits),
            "전공필수": max(0, required_major_req - profile.major_required_credits),
            "전공선택": max(0, required_major_ele - profile.major_elective_credits),
            "교양": max(0, required_ge - profile.general_education_credits),
        }
        missing = {k: v for k, v in gaps.items() if v > 0}
        if missing:
            detail = "졸업요건 데모 기준에서 부족한 항목: " + ", ".join(f"{k} {v}학점" for k, v in missing.items())
            severity = "warning"
            actions = [f"{k} 영역 {v}학점 이상 보완" for k, v in missing.items()]
            actions += ["졸업논문/졸업시험/외국어 요건 별도 확인", "학과사무실 또는 학사지원팀 최종 확인"]
        else:
            detail = "입력된 학점 기준으로는 데모 졸업학점 요건을 충족합니다. 단, 필수 과목·논문·시험·외국어 요건은 별도 확인해야 합니다."
            severity = "success"
            actions = ["필수 과목 이수 여부 확인", "졸업논문/졸업시험 요건 확인", "졸업사정 결과 최종 확인"]
        return RuleFinding("graduation", severity, "졸업요건 점검", detail, actions)

    def _leave_of_absence(self, profile: StudentProfile) -> RuleFinding:
        leave_rules = self.rules["leave_of_absence"]
        actions = ["학사일정의 휴학 신청 기간 확인"] + leave_rules["required_documents"]
        if profile.leave_count >= leave_rules["requires_advisor_check_after_count"]:
            severity = "warning"
            detail = f"휴학 이력이 {profile.leave_count}회이므로 학과 또는 담당 부서 확인이 필요할 수 있습니다."
            actions.append("휴학 가능 횟수 및 지도교수 상담 필요 여부 확인")
        else:
            severity = "info"
            detail = "휴학 신청은 지정 기간과 사유별 제출서류 확인이 핵심입니다."
        return RuleFinding("leave_of_absence", severity, "휴학 가능성 점검", detail, actions)

    def _scholarship(self, profile: StudentProfile) -> RuleFinding:
        scholarship = self.rules["scholarship"]
        actions = ["최신 장학 공지의 신청 기간 확인"] + scholarship["required_documents"]
        if profile.scholarship_status and profile.scholarship_status != "none":
            detail = f"현재 장학 상태가 '{profile.scholarship_status}'로 입력되었습니다. 중복 수혜 가능 여부를 확인해야 합니다."
            severity = "warning"
            actions.append("중복 수혜 제한 여부 확인")
        else:
            detail = "장학 신청을 위해 공지별 자격 기준과 제출서류를 확인해야 합니다. " + scholarship["recommended_gpa_note"]
            severity = "info"
        return RuleFinding("scholarship", severity, "장학 신청 준비도 점검", detail, actions)

    def _course_correction(self, profile: StudentProfile) -> RuleFinding:
        course = self.rules["course_correction"]
        return RuleFinding(
            "course_correction",
            "info",
            "수강정정 대응 점검",
            course["after_deadline_note"],
            course["actions"],
        )
