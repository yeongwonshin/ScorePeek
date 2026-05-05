from __future__ import annotations

import json

import streamlit as st

from src.admin_ai.pipeline import AdminAIAgent
from src.admin_ai.profile import StudentProfile

st.set_page_config(page_title="서강 원스톱 학사·행정 AI", page_icon="🎓", layout="wide")

st.title("🎓 서강 원스톱 학사·행정 AI 에이전트")
st.caption("공지·규정·학사일정 문서를 근거로 개인 상황별 학사·행정 답변과 후속 액션을 생성하는 MVP")

with st.sidebar:
    st.header("학생 프로필")
    grade = st.number_input("학년", min_value=1, max_value=8, value=4)
    major = st.text_input("전공", value="컴퓨터공학")
    completed_credits = st.number_input("총 이수학점", min_value=0, value=118)
    major_required_credits = st.number_input("전공필수 이수학점", min_value=0, value=30)
    major_elective_credits = st.number_input("전공선택 이수학점", min_value=0, value=24)
    general_education_credits = st.number_input("교양 이수학점", min_value=0, value=28)
    leave_count = st.number_input("휴학 이력", min_value=0, value=1)
    scholarship_status = st.text_input("장학 상태", value="none")

question = st.text_area(
    "질문을 입력하세요",
    value="컴공 4학년인데 졸업까지 뭐가 남았어?",
    height=100,
)

if "agent" not in st.session_state:
    st.session_state.agent = AdminAIAgent()

if st.button("AI 에이전트 실행", type="primary"):
    profile = StudentProfile(
        grade=grade,
        major=major,
        completed_credits=completed_credits,
        major_required_credits=major_required_credits,
        major_elective_credits=major_elective_credits,
        general_education_credits=general_education_credits,
        leave_count=leave_count,
        scholarship_status=scholarship_status,
    )
    result = st.session_state.agent.ask(question, profile)

    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("답변")
        st.markdown(result["answer"].replace("\n", "  \n"))

        st.subheader("해야 할 일 체크리스트")
        for item in result["checklist"]:
            st.checkbox(item, value=False)

        st.subheader("문의 이메일 초안")
        st.code(result["email_draft"], language="text")

    with right:
        st.subheader("근거 문서")
        for ev in result["evidence"]:
            with st.expander(f"{ev['source']} | chunk {ev['chunk_id']} | score {ev['score']}"):
                st.write(ev["preview"])

        st.subheader("일정 등록용 JSON")
        st.json(result["calendar_items"])

        st.subheader("원본 응답 JSON")
        st.download_button(
            "결과 JSON 다운로드",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name="admin_ai_result.json",
            mime="application/json",
        )
else:
    st.info("왼쪽 프로필과 질문을 조정한 뒤 AI 에이전트 실행 버튼을 누르세요.")
