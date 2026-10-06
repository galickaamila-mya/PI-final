import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

import api.main as main


@pytest.fixture
def client(monkeypatch):
    mock_qa = MagicMock()
    mock_qa.answer_question.return_value = {"answer": "100 million", "confidence": 0.9}
    mock_qa.extract_financial_metrics.return_value = {"revenue": "100 million"}

    monkeypatch.setattr(main, "qa_model", mock_qa)
    monkeypatch.setattr(main, "literacy_model", main.FinancialLiteracyModel())

    with TestClient(main.app) as c:
        yield c


def test_health_and_docs(client):
    assert client.get("/health").status_code == 200

    openapi_paths = client.get("/openapi.json").json()["paths"]
    assert "/api/v1/financial-qa" in openapi_paths


def test_qa_endpoint(client):
    payload = {
        "question": "What was revenue?",
        "context": "Revenue was 100 million."
    }
    resp = client.post("/api/v1/financial-qa", json=payload)
    assert resp.status_code == 200
    assert resp.json()["answer"] == "100 million"


def test_literacy_endpoint(client):
    payload = {
        "user_profile": {
            "age": 27,
            "income": 55300,
            "savings": 12000,
            "expenses": 41250,
            "debt": 0,
            "has_emergency_fund": False,
            "has_budget": True,
            "has_insurance": True
        },
        "question": "Как начать копить?",
    }
    resp = client.post("/api/v1/financial-literacy", json=payload)
    assert resp.status_code == 200
    assert "literacy_score" in resp.json()


def test_extract_metrics(client):
    ctx = "Revenue was 100 million."
    resp = client.post("/api/v1/financial-qa/extract-metrics", params={"context": ctx})
    assert resp.status_code == 200
    assert "metrics" in resp.json()
