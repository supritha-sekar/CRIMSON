import pytest
from fastapi.testclient import TestClient
import os
import sys

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.seed import seed_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    seed_db()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] is True
    assert data["mode"] == "demo"

def test_login_success(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@crimson.intel", "password": "crimson2026"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@crimson.intel"
    assert data["user"]["role"] == "Administrator"

def test_get_cases(client):
    response = client.get("/api/cases")
    assert response.status_code == 200
    cases = response.json()
    assert isinstance(cases, list)
    assert len(cases) > 0

def test_get_subjects(client):
    response = client.get("/api/subjects")
    assert response.status_code == 200
    subjects = response.json()
    assert isinstance(subjects, list)
    assert len(subjects) > 0

def test_run_analysis(client):
    response = client.post(
        "/api/analysis/run",
        json={
            "query_text": "Analyze C2 traffic to IP 185.220.101.45 by subject Viktor Reznov",
            "context_text": "Ransomware payout sent to crypto wallet 0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["is_demo"] is True
    assert len(data["entities"]) > 0

def test_network_graph(client):
    response = client.get("/api/network/graph")
    assert response.status_code == 200
    graph = response.json()
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) > 0

def test_global_search(client):
    response = client.get("/api/search/global?q=Shadow")
    assert response.status_code == 200
    results = response.json()
    assert "cases" in results
    assert results["total"] > 0
