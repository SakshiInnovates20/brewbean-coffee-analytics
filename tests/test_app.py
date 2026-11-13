import pytest
from app import create_app

@pytest.fixture
def client():
    """
    Flask test client fixture.
    """
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """
    Tests that the home page (GET /) loads successfully with HTTP 200.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"BREWBEAN COFFEE" in response.data
    assert b"Multi-Branch Sales" in response.data

def test_health_endpoint(client):
    """
    Tests that the health check endpoint (GET /health) returns valid JSON with status ok.
    """
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data.get("status") == "ok"
    assert "database" in data
    assert "connected" in data["database"]
