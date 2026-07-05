from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.scorepeek.models import ScoreSubmission, VerifyRequest
from src.scorepeek.service import ScorePeekService

app = FastAPI(title="ScorePeek Anonymous Score Board", version="0.1.0")
service = ScorePeekService()


class ReportRequest(BaseModel):
    course_id: str
    assessment: str = "midterm"
    student_private_key: str | None = None


@app.get("/")
def health() -> dict:
    return {
        "status": "ok",
        "service": "scorepeek-anonymous-score-board",
        "description": "Anonymous course score distribution and percentile monitor",
    }


@app.get("/courses")
def list_courses() -> list[dict]:
    return service.list_courses()


@app.post("/verify")
def verify(req: VerifyRequest) -> dict:
    result = service.verify_course(req.course_id, req.access_key)
    return result.model_dump(exclude={"course": {"access_key_hash"}})


@app.post("/scores")
def submit_score(submission: ScoreSubmission) -> dict:
    try:
        return service.submit_score(submission)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/stats")
def stats(req: ReportRequest) -> dict:
    try:
        return service.report(req.course_id, req.assessment, req.student_private_key).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
