from __future__ import annotations

import os
from textwrap import shorten

from .calendar import build_calendar_items
from .profile import StudentProfile
from .rule_engine import RuleFinding


def _merge_actions(findings: list[RuleFinding]) -> list[str]:
    actions: list[str] = []
    for finding in findings:
        for action in finding.actions:
            if action not in actions:
                actions.append(action)
    return actions


def build_email_draft(question: str, profile: StudentProfile, findings: list[RuleFinding]) -> str:
    finding_titles = ", ".join(f.title for f in findings)
    actions = _merge_actions(findings)
    action_text = "\n".join(f"- {action}" for action in actions[:8])
    return f"""제목: 학사·행정 문의드립니다 - {shorten(question, width=40, placeholder='...')}

안녕하세요. 담당자님,

아래 학사·행정 사항에 대해 확인을 요청드립니다.

[문의 내용]
{question}

[학생 정보]
{chr(10).join(profile.to_korean_lines())}

[AI 에이전트가 확인한 주요 점검 항목]
{finding_titles}

[확인이 필요한 사항]
{action_text}

본 내용은 AI 기반 사전 점검 결과이므로, 공식 기준에 따른 최종 확인을 부탁드립니다.
감사합니다.
""".strip()


def build_answer(question: str, profile: StudentProfile, retrieved: list[dict], findings: list[RuleFinding]) -> dict:
    actions = _merge_actions(findings)
    evidence_lines = []
    for item in retrieved[:4]:
        evidence_lines.append(
            {
                "source": item["source"],
                "chunk_id": item["chunk_id"],
                "score": item["score"],
                "preview": shorten(item["text"], width=220, placeholder="..."),
            }
        )

    summary_parts = [f"질문: {question}", ""]
    summary_parts.append("개인 프로필 기준 점검 결과:")
    for finding in findings:
        summary_parts.append(f"- [{finding.severity}] {finding.title}: {finding.detail}")

    summary_parts.append("")
    summary_parts.append("권장 후속 조치:")
    for idx, action in enumerate(actions, start=1):
        summary_parts.append(f"{idx}. {action}")

    summary_parts.append("")
    summary_parts.append("주의: 현재 포함된 문서는 데모용 샘플이므로 실제 제출·신청 전 공식 공지와 담당 부서 확인이 필요합니다.")

    return {
        "answer": "\n".join(summary_parts),
        "findings": [finding.__dict__ for finding in findings],
        "checklist": actions,
        "calendar_items": build_calendar_items(question, actions),
        "email_draft": build_email_draft(question, profile, findings),
        "evidence": evidence_lines,
    }


def maybe_rewrite_with_openai(answer_payload: dict, question: str) -> dict:
    """Optional LLM rewrite.

    The MVP does not require OpenAI. If OPENAI_API_KEY is present, this function
    can be extended to rewrite the deterministic answer in a more natural style.
    For reliability in the contest demo, deterministic output is kept by default.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return answer_payload
    return answer_payload
