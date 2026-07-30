def test_health_returns_healthy_response(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Service is healthy.",
    }
