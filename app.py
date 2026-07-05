from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.scorepeek.models import ScoreSubmission
from src.scorepeek.service import ScorePeekService

st.set_page_config(page_title="ScorePeek", page_icon="📊", layout="wide")

st.title("📊 ScorePeek: Anonymous Course Score Board")
st.caption("Verify course access, submit your score anonymously, and see the live median, percentile, and score distribution.")

if "service" not in st.session_state:
    st.session_state.service = ScorePeekService()
if "verified_course" not in st.session_state:
    st.session_state.verified_course = None

service: ScorePeekService = st.session_state.service
courses = service.list_courses()
course_labels = {f"{item['course_id']} · {item['title']}": item["course_id"] for item in courses}

with st.sidebar:
    st.header("Course verification")
    if course_labels:
        selected_label = st.selectbox("Course", list(course_labels.keys()))
        course_id = course_labels[selected_label]
    else:
        course_id = st.text_input("Course ID")
    access_key = st.text_input("Course access key", type="password", help="Demo key for the selected course. Replace with SSO/LMS verification in production.")
    if st.button("Verify course", type="primary"):
        result = service.verify_course(course_id, access_key)
        if result.verified:
            st.session_state.verified_course = result.course
            st.success("Course verified.")
        else:
            st.session_state.verified_course = None
            st.error(result.message)

    st.divider()
    st.header("Anonymous identity")
    student_private_key = st.text_input(
        "Private update key",
        type="password",
        help="Use the same private key to update your own score. The raw value is never stored.",
    )

course = st.session_state.verified_course

if not course:
    st.info("Verify your course access first. Demo courses and keys are listed in README.md.")
    st.stop()

left, right = st.columns([0.9, 1.1])

with left:
    st.subheader("Submit or update my score")
    assessment = st.text_input("Assessment", value="midterm")
    max_score = st.number_input("Max score", min_value=1.0, value=float(course.max_score), step=1.0)
    score = st.number_input("My score", min_value=0.0, max_value=float(max_score), value=min(80.0, float(max_score)), step=0.5)

    if st.button("Submit anonymously", type="primary"):
        if not student_private_key:
            st.error("Enter a private update key first.")
        else:
            submission = ScoreSubmission(
                course_id=course.course_id,
                assessment=assessment,
                score=score,
                max_score=max_score,
                student_private_key=student_private_key,
            )
            result = service.submit_score(submission)
            st.success("Your score was submitted or updated anonymously.")
            st.json(result["summary"])

    with st.expander("Privacy model"):
        st.markdown(
            """
- No name or student number is stored directly.
- Your private update key is converted into a salted hash and used only to update your own score.
- In production, the demo access key should be replaced with official SSO/LMS enrollment verification.
            """.strip()
        )

with right:
    st.subheader("Live class distribution")
    report = service.report(course.course_id, assessment, student_private_key or None)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Submissions", report.count)
    m2.metric("Mean", "-" if report.mean is None else f"{report.mean:.2f}")
    m3.metric("Median", "-" if report.median is None else f"{report.median:.2f}")
    m4.metric("My rank", "-" if report.my_estimated_rank is None else f"{report.my_estimated_rank}/{report.count}")

    st.caption(report.message)
    histogram_df = pd.DataFrame([item.model_dump() for item in report.histogram])
    if not histogram_df.empty:
        st.bar_chart(histogram_df, x="label", y="count")

    if report.my_percentile is not None:
        st.success(f"Your score is at approximately the {report.my_percentile:.2f} percentile among submitted anonymous scores.")

    st.download_button(
        "Download report JSON",
        data=json.dumps(report.model_dump(), ensure_ascii=False, indent=2),
        file_name="scorepeek_report.json",
        mime="application/json",
    )
