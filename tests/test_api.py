from fastapi.testclient import TestClient
from backend.main import app
client=TestClient(app)
def test_health():
    r=client.get("/health")
    assert r.status_code==200 and r.json()["status"]=="ok"
def test_questions_demo(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY",raising=False)
    r=client.post("/api/questions",json={"role":"AI Product Manager","mode":"mixed","count":3})
    assert r.status_code==200 and r.json()["demo"] is True and len(r.json()["questions"])==3
def test_evaluation_demo(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY",raising=False)
    r=client.post("/api/evaluate",json={"role":"Forward Deployed Engineer","question":"Design RAG","answer":"I would ingest, chunk, embed and retrieve documents, then evaluate groundedness and latency."})
    assert r.status_code==200 and 1<=r.json()["overall_score"]<=10
def test_summary():
    r=client.post("/api/summary",json={"role":"AI Product Manager","evaluations":[{"overall_score":8,"improvements":["Quantify impact"]},{"overall_score":6,"improvements":["Explain trade-offs"]}]})
    assert r.status_code==200 and r.json()["average_score"]==7
