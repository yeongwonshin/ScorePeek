from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .document_loader import load_documents_from_dir
from .profile import StudentProfile
from .response_builder import build_answer, maybe_rewrite_with_openai
from .retriever import LocalRetriever
from .rule_engine import RuleEngine


class AdminAIAgent:
    def __init__(
        self,
        document_dir: str | Path = "data/sample_documents",
        rules_path: str | Path = "data/policies/rules.json",
    ):
        self.document_dir = Path(document_dir)
        self.rules_path = Path(rules_path)
        self.chunks = load_documents_from_dir(self.document_dir)
        self.retriever = LocalRetriever(self.chunks)
        self.rule_engine = RuleEngine(self.rules_path)

    def ask(self, question: str, profile: StudentProfile | dict[str, Any]) -> dict:
        if isinstance(profile, dict):
            profile = StudentProfile(**profile)
        retrieved = self.retriever.search(question, top_k=5)
        findings = self.rule_engine.evaluate(question, profile)
        payload = build_answer(question, profile, retrieved, findings)
        return maybe_rewrite_with_openai(payload, question)


def _load_profile(path: str | Path) -> StudentProfile:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return StudentProfile(**data)


def main() -> None:
    parser = argparse.ArgumentParser(description="서강 원스톱 학사·행정 AI 에이전트 CLI")
    parser.add_argument("--question", required=True, help="질문")
    parser.add_argument("--profile", default="examples/demo_profile.json", help="학생 프로필 JSON 경로")
    parser.add_argument("--document-dir", default="data/sample_documents", help="문서 폴더")
    parser.add_argument("--rules", default="data/policies/rules.json", help="규칙 JSON 경로")
    args = parser.parse_args()

    agent = AdminAIAgent(args.document_dir, args.rules)
    profile = _load_profile(args.profile)
    result = agent.ask(args.question, profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
