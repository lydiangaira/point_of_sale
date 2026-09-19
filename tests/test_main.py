# tests/test_main.py

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_unknown_route_returns_404(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404


def test_openapi_docs_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()