from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from src.admin_ai.pipeline import AdminAIAgent
from src.admin_ai.profile import StudentProfile

app = FastAPI(title="서강 원스톱 학사·행정 AI 에이전트", version="0.1.0")
agent = AdminAIAgent()


class AskRequest(BaseModel):
    question: str
    profile: StudentProfile


@app.get("/")
def health() -> dict:
    return {"status": "ok", "service": "sogang-one-stop-admin-ai"}


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    return agent.ask(req.question, req.profile)
