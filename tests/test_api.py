from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_questions_demo_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/api/questions",
        json={"role": "AI Product Manager", "mode": "mixed", "count": 3},
    )
    assert response.status_code == 200
    assert response.json()["demo"] is True
    assert len(response.json()["questions"]) == 3


def test_question_count_is_validated():
    response = client.post(
        "/api/questions",
        json={"role": "AI Product Manager", "count": 11},
    )
    assert response.status_code == 422


def test_evaluation_demo_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/api/evaluate",
        json={
            "role": "Forward Deployed Engineer",
            "question": "Design RAG",
            "answer": (
                "I would ingest, chunk, embed and retrieve documents, "
                "then evaluate groundedness and latency."
            ),
        },
    )
    assert response.status_code == 200
    assert 1 <= response.json()["overall_score"] <= 10
    assert response.json()["demo"] is True


def test_evaluation_rejects_empty_answer():
    response = client.post(
        "/api/evaluate",
        json={"role": "AI PM", "question": "Prioritize a roadmap", "answer": ""},
    )
    assert response.status_code == 422


def test_summary_uses_answered_questions_only():
    response = client.post(
        "/api/summary",
        json={
            "role": "AI Product Manager",
            "evaluations": [
                {"overall_score": 8, "improvements": ["Quantify impact"]},
                {"overall_score": 2, "skipped": True, "improvements": ["Ignore this"]},
                {"overall_score": 6, "improvements": ["Explain trade-offs"]},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["average_score"] == 7
    assert response.json()["questions_answered"] == 2
    assert response.json()["questions_skipped"] == 1
    assert "Ignore this" not in response.json()["top_focus_areas"]


def test_summary_rejects_all_skipped_questions():
    response = client.post(
        "/api/summary",
        json={
            "role": "AI Product Manager",
            "evaluations": [{"overall_score": 8, "skipped": True}],
        },
    )
    assert response.status_code == 400


def test_analyze_rejects_short_job_description():
    response = client.post(
        "/api/analyze",
        data={"job_description": "Too short", "role": "AI Product Manager"},
        files={"resume": ("resume.txt", b"A sufficiently long resume text for parsing.", "text/plain")},
    )
    assert response.status_code == 400
    assert "80 characters" in response.json()["detail"]


def test_analyze_accepts_text_resume_in_demo_mode(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    resume = (
        "AI validation engineer with experience in Python, FastAPI, RAG, "
        "LLM evaluation, observability and enterprise AI systems."
    )
    job_description = (
        "We need an AI Product Manager with Python, RAG, LLM evaluation, "
        "observability, product strategy and stakeholder management skills. "
        "The role owns discovery, prioritization and delivery of AI products."
    )
    response = client.post(
        "/api/analyze",
        data={"job_description": job_description, "role": "AI Product Manager"},
        files={"resume": ("resume.txt", resume.encode(), "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["demo"] is True
    assert response.json()["resume_text"] == resume
    assert "rag" in response.json()["matched_skills"]


def test_analyze_rejects_unsupported_resume_format():
    response = client.post(
        "/api/analyze",
        data={
            "job_description": (
                "This is a sufficiently detailed job description with more than "
                "eighty characters for the validation endpoint."
            )
        },
        files={"resume": ("resume.csv", b"candidate,data", "text/csv")},
    )
    assert response.status_code == 415
