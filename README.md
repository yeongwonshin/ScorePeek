# ScorePeek: Anonymous Course Score Board

ScorePeek is a dynamic anonymous score-sharing application for university courses. Students verify that they belong to a specific course, submit their score anonymously, and immediately see the live median, score distribution, percentile, and estimated rank based on already submitted scores.

> Goal: When a class only reveals the average score, ScorePeek helps students understand the real distribution by pooling anonymous submissions from classmates.

## Project Purpose

Many university courses disclose only limited statistics such as the average score. Students often cannot see the median, spread, or approximate percentile because the full grade distribution is not shared as a spreadsheet or dashboard.

This project solves that problem by creating a course-specific anonymous score board. Once a student verifies course access, they can submit or update their own score. The system aggregates all submitted scores for the same course and assessment, then calculates distribution statistics in real time.

The project is designed for:

- Students who want to understand where their score stands in the class
- Course communities that want an anonymous and transparent score distribution
- Portfolio demonstrations of Streamlit, FastAPI, SQLite, Pydantic, and statistics pipelines
- Future integration with official SSO/LMS enrollment verification

## Key Features

- Course access verification using a demo course key
- Anonymous score submission and update
- No raw student ID or name storage
- Median, mean, standard deviation, min, max calculation
- Approximate percentile and estimated rank for the current student
- Score distribution histogram
- SQLite persistence
- Streamlit web UI
- FastAPI endpoints
- Testable service layer

## Privacy and Abuse Prevention Model

This MVP does not store names, student numbers, or raw identifiers. The user enters a private update key, and the application stores only a salted hash of that value. The hash is used to update the same student's previous score instead of creating duplicate submissions.

For a real deployment, the demo course key should be replaced with one of the following:

- University SSO login
- LMS enrollment API verification
- Course-specific invitation links
- Email domain plus course roster verification

Recommended production safeguards:

- Minimum submission count before showing distribution
- Rate limiting
- Duplicate and outlier monitoring
- Course owner moderation
- Clear disclaimer that the distribution is based on voluntary anonymous submissions

## Architecture

```text
+----------------------+        +--------------------------+
| Student browser      | -----> | Streamlit UI             |
| - verify course      |        | - score form             |
| - submit score       |        | - live distribution      |
+----------------------+        +------------+-------------+
                                      |
                                      v
+----------------------+        +--------------------------+
| FastAPI API          | -----> | ScorePeek service layer  |
| - /verify            |        | - course verification    |
| - /scores            |        | - anonymous hash         |
| - /stats             |        | - statistics pipeline    |
+----------------------+        +------------+-------------+
                                      |
                                      v
                               +--------------------------+
                               | SQLite score store       |
                               | - course_id              |
                               | - assessment             |
                               | - participant_hash       |
                               | - normalized_score       |
                               +--------------------------+
```

## Directory Structure

```text
scorepeek/
├── app.py                       # Streamlit web application
├── api.py                       # FastAPI server
├── requirements.txt             # Runtime dependencies
├── pyproject.toml               # Pytest configuration
├── .env.example                 # Environment variable examples
├── data/
│   └── courses.json             # Demo course registry and access-key hashes
├── examples/
│   └── demo_submission.json     # Example API payload
├── src/scorepeek/
│   ├── auth.py                  # Course verification and anonymous hashing
│   ├── models.py                # Pydantic request/response models
│   ├── service.py               # Application service layer
│   ├── stats.py                 # Median, percentile, rank, histogram logic
│   └── storage.py               # SQLite persistence
└── tests/
    └── test_scorepeek.py        # Core behavior tests
```

## Quick Start

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### Run the Streamlit App

```bash
streamlit run app.py
```

Demo course:

```text
Course ID: CSE101-2026S
Access key: demo-cse101
```

### Run the FastAPI Server

```bash
uvicorn api:app --reload
```

API docs:

```text
http://127.0.0.1:8000/docs
```

Submit a score:

```bash
curl -X POST "http://127.0.0.1:8000/scores" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "CSE101-2026S",
    "assessment": "midterm",
    "score": 82,
    "max_score": 100,
    "student_private_key": "my-private-update-key"
  }'
```

Get stats:

```bash
curl -X POST "http://127.0.0.1:8000/stats" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "CSE101-2026S",
    "assessment": "midterm",
    "student_private_key": "my-private-update-key"
  }'
```

## Main Output

The application returns a live class distribution summary:

```json
{
  "course_id": "CSE101-2026S",
  "assessment": "midterm",
  "count": 24,
  "mean": 73.42,
  "median": 75.0,
  "stdev": 12.85,
  "minimum": 41.0,
  "maximum": 98.0,
  "my_score": 82.0,
  "my_percentile": 79.17,
  "my_estimated_rank": 5
}
```

## Tests

```bash
pytest -q
```

## What Changed from the Previous Repository Concept

The previous repository was an academic administration AI agent. This version intentionally removes that concept and keeps only the useful application skeleton: Streamlit UI, FastAPI API, Pydantic models, tests, and a service pipeline.

Removed or replaced areas:

- Academic document RAG
- Graduation and scholarship rule engine
- Calendar generation
- Admin email draft generation
- Sample university policy documents

New areas:

- Course verification
- Anonymous score storage
- Score statistics
- Distribution histogram
- Percentile and estimated rank calculation
