from fastapi.testclient import TestClient

import api


client = TestClient(api.app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ask_endpoint_success(monkeypatch):

    def mock_run_agent(question):
        assert question == "How many customers are there?"

        return {
            "success": True,
            "sql": "SELECT COUNT(CustomerId) FROM Customer",
            "columns": ["COUNT(CustomerId)"],
            "rows": [(59,)],
            "answer": "COUNT(CustomerId): 59",
            "attempts": 1,
            "error": None,
        }

    monkeypatch.setattr(api, "run_agent", mock_run_agent)

    response = client.post(
        "/ask",
        json={"question": "How many customers are there?"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["rows"] == [[59]]


def test_ask_endpoint_empty_question():
    response = client.post(
        "/ask",
        json={"question": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."


def test_ask_endpoint_missing_question():
    response = client.post("/ask", json={})

    assert response.status_code == 422
