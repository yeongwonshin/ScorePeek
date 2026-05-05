# 서강 원스톱 학사·행정 AI 에이전트

> 공지·학칙·학사일정·장학/졸업/휴복학/수강신청 규정을 근거로 학생의 개인 상황에 맞는 학사·행정 답변, 해야 할 일 체크리스트, 일정 등록용 JSON, 문의 이메일 초안을 생성하는 MVP 프로젝트입니다.

## 1. 프로젝트 소개

이 프로젝트는 단순한 “학교 규정 챗봇”이 아니라, 학생의 학년·전공·이수학점·휴학 이력·장학 상태 같은 정보를 함께 받아 **개인 상황 기반 학사·행정 의사결정 보조**를 수행하는 AI 에이전트입니다.

예를 들어 학생이 다음과 같이 질문할 수 있습니다.

- “컴공 4학년인데 졸업까지 뭐가 남았어?”
- “이번 학기 휴학 가능해?”
- “장학금 신청하려면 뭘 해야 해?”
- “수강정정 기간을 놓치면 어떻게 돼?”

시스템은 내부 샘플 문서를 검색하고, 규칙 엔진으로 개인 상황을 판정한 뒤 다음 결과를 제공합니다.

1. 근거 문서 기반 답변
2. 학생 프로필 기반 위험/부족 요건 판정
3. 해야 할 일 체크리스트
4. 일정 등록용 JSON
5. 행정부서 문의 이메일 초안
6. 근거 문서 출처

> 현재 포함된 문서는 **데모용 가상 샘플 데이터**입니다. 실제 공모전 제출/운영 시에는 서강대학교의 공식 공지, 학칙, 학사일정, 장학 규정, 졸업요건 문서로 교체해야 합니다.

## 2. 핵심 차별점

기존 FAQ 챗봇은 질문과 유사한 문서를 찾아 요약하는 수준에 머무릅니다. 본 프로젝트는 다음 구조를 통해 “개인화된 행정 판단”까지 수행합니다.

```text
공지/규정/학사일정 문서
        ↓
문서 파서 및 인덱싱
        ↓
TF-IDF 기반 로컬 RAG 검색
        ↓
학생 프로필 입력
        ↓
규칙 엔진 기반 학사·행정 판정
        ↓
답변 + 체크리스트 + 일정 + 이메일 초안 생성
```

## 3. 프로젝트 구조

```text
sogang-one-stop-admin-ai/
├── app.py                         # Streamlit 웹 데모
├── api.py                         # FastAPI API 서버
├── requirements.txt               # 실행 의존성
├── .env.example                   # 환경변수 예시
├── README.md                      # 실행 및 소개 문서
├── data/
│   ├── sample_documents/          # 데모용 학사/행정 문서
│   └── policies/rules.json        # 규칙 엔진 설정
├── examples/
│   └── demo_profile.json          # 예시 학생 프로필
├── src/admin_ai/
│   ├── document_loader.py         # txt/md/pdf/hwpx 문서 로더
│   ├── retriever.py               # 로컬 RAG 검색기
│   ├── rule_engine.py             # 개인 상황 기반 규칙 판정
│   ├── response_builder.py        # 답변/체크리스트/이메일 생성
│   ├── calendar.py                # 일정 JSON 생성
│   ├── profile.py                 # 학생 프로필 모델
│   └── pipeline.py                # 전체 파이프라인 통합
└── tests/
    └── test_pipeline.py           # 핵심 동작 테스트
```

## 4. 설치 방법

Python 3.10 이상을 권장합니다.

```bash
cd sogang-one-stop-admin-ai
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## 5. Streamlit 웹앱 실행

```bash
streamlit run app.py
```

브라우저가 열리면 다음 값을 입력해 테스트할 수 있습니다.

```text
질문: 컴공 4학년인데 졸업까지 뭐가 남았어?
학년: 4
전공: 컴퓨터공학
총 이수학점: 118
전공필수 이수학점: 30
전공선택 이수학점: 24
교양 이수학점: 28
휴학 이력: 1
장학 상태: none
```

## 6. FastAPI 서버 실행

```bash
uvicorn api:app --reload
```

요청 예시:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "컴공 4학년인데 졸업까지 뭐가 남았어?",
    "profile": {
      "grade": 4,
      "major": "컴퓨터공학",
      "completed_credits": 118,
      "major_required_credits": 30,
      "major_elective_credits": 24,
      "general_education_credits": 28,
      "leave_count": 1,
      "scholarship_status": "none"
    }
  }'
```

API 문서는 서버 실행 후 아래에서 확인할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

## 7. CLI 방식 빠른 테스트

```bash
python -m src.admin_ai.pipeline \
  --question "이번 학기 휴학 가능해?" \
  --profile examples/demo_profile.json
```

## 8. OpenAI API 사용 선택 사항

기본 동작은 외부 API 없이 로컬 TF-IDF 검색과 규칙 엔진으로 작동합니다. OpenAI API를 연결하면 답변 문장을 더 자연스럽게 생성하도록 확장할 수 있습니다.

```bash
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력
```

현재 MVP에서는 API 키가 없어도 실행됩니다.

## 9. 실제 서강대 데이터로 교체하는 방법

`data/sample_documents/` 폴더에 공식 문서를 넣으면 됩니다.

지원 형식:

- `.txt`
- `.md`
- `.pdf`
- `.hwpx` 일부 지원: HWPX는 zip/XML 구조에서 텍스트를 추출합니다. 문서 구조에 따라 추가 보정이 필요할 수 있습니다.

예시:

```bash
cp ~/Downloads/official_academic_calendar.pdf data/sample_documents/
cp ~/Downloads/graduation_rules.hwpx data/sample_documents/
```

그 후 앱이나 API를 다시 실행하면 자동으로 인덱싱합니다.

## 10. 공모전 제안서에 쓸 수 있는 요약문

본 프로젝트는 서강대학교 구성원이 학사·행정·규정·공지 관련 문제를 개인 상황에 맞게 해결할 수 있도록 지원하는 생성형 AI 기반 원스톱 행정 에이전트이다. 기존 규정 검색이나 FAQ 챗봇은 문서 검색 중심이지만, 본 시스템은 학생의 학년, 전공, 이수학점, 휴학 이력, 장학 상태 등을 함께 반영하여 졸업 가능성, 휴학 가능성, 장학 신청 준비도, 수강정정 대응 방안 등을 개인화해 판정한다. 또한 답변에 그치지 않고 해야 할 일 체크리스트, 일정 등록용 JSON, 제출서류 초안, 행정부서 문의 이메일까지 생성하여 학내 행정 접근성을 높인다.

## 11. 구현 범위

### 세부업무 #1: 학내 문서 수집 및 검색 인덱스 구축

공지, 학칙, 학사일정, 장학, 졸업, 휴복학, 수강신청 문서를 수집하고 문서 파서를 통해 텍스트를 추출합니다. 추출된 문서는 청크 단위로 분할되어 로컬 검색 인덱스에 저장됩니다.

### 세부업무 #2: 개인 상황 기반 규칙 엔진 구현

학생 프로필을 기반으로 졸업요건 부족분, 휴학 관련 위험 여부, 장학 신청 준비 항목, 수강정정 대응 항목을 계산합니다.

### 세부업무 #3: AI 응답 및 행정 액션 생성

검색된 문서와 규칙 엔진 결과를 결합하여 답변, 체크리스트, 일정 JSON, 이메일 초안을 생성합니다.

## 12. 기술 스택

- Python 3.10+
- Streamlit
- FastAPI
- scikit-learn TF-IDF 검색
- Pydantic
- pypdf
- python-dotenv
- OpenAI API 선택 연동 가능

## 13. 테스트

```bash
pytest -q
```

## 14. 향후 고도화 방향

1. 학교 포털/공지사항 크롤러 정식 연동
2. 학과별 졸업요건 JSON 자동 구축
3. Google Calendar 또는 Outlook 일정 등록 연동
4. 전자서식 자동 작성 기능
5. 학사팀/장학팀/국제팀별 라우팅 기능
6. 답변 근거의 문서 페이지 번호 표시
7. 사용자 로그 기반 자주 묻는 질문 분석 대시보드

## 15. 주의 사항

이 프로젝트는 공모전 MVP와 데모를 위한 코드입니다. 실제 운영 시에는 다음이 필요합니다.

- 공식 문서 최신성 검증
- 부서별 승인된 답변 정책
- 개인정보 처리 기준 준수
- 답변 면책 문구 및 담당부서 최종 확인 절차
- 민감한 학적 정보 저장 최소화
