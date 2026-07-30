def test_create_event_without_api_key_returns_401(client, valid_info_event):
    response = client.post(
        "/events/",
        json=valid_info_event,
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or missing API key.",
    }


def test_create_event_with_wrong_api_key_returns_401(
    client,
    valid_info_event,
):

    response = client.post(
        "/events/",
        json=valid_info_event,
        headers={
            "X-API-KEY": "wrong-test-api-key",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or missing API key.",
    }


def test_create_event_with_valid_api_key_returns_201(
    client, auth_headers, valid_info_event
):
    response = client.post(
        "/events/",
        json=valid_info_event,
        headers=auth_headers,
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["status"] == "success"
    assert isinstance(response_body["message"], str)
    assert response_body["message"]

    created_event = response_body["data"]

    assert created_event["category"] == valid_info_event["category"]
    assert created_event["user_id"] == valid_info_event["user_id"]
    assert created_event["session_id"] == valid_info_event["session_id"]
    assert created_event["event_data"] == valid_info_event["event_data"]

    assert isinstance(created_event["id"], int)
    assert created_event["id"] > 0
    assert "timestamp" in created_event

    list_response = client.get("/events/", headers=auth_headers)

    assert list_response.status_code == 200

    list_body = list_response.json()

    assert list_body["total"] == 1
    assert list_body["count"] == 1
    assert len(list_body["data"]) == 1

    stored_event = list_body["data"][0]

    assert stored_event["id"] == created_event["id"]
    assert stored_event["user_id"] == valid_info_event["user_id"]
    assert stored_event["event_data"] == valid_info_event["event_data"]


def test_event_list_starts_empty(
    client,
    auth_headers,
):
    response = client.get(
        "/events/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["total"] == 0
    assert response_body["count"] == 0
    assert response_body["data"] == []


def test_get_events_without_api_key_returns_401(client):
    response = client.get("/events/")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or missing API key.",
    }


def test_get_events_with_wrong_api_key_returns_401(client):
    response = client.get(
        "/events/",
        headers={
            "X-API-KEY": "wrong-test-api-key",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}


def test_get_user_events_without_api_key_returns_401(client):
    response = client.get(
        "/events/user/test-user-001",
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}


def test_get_user_events_with_wrong_api_key_returns_401(client):
    response = client.get(
        "/events/user/test-user-001",
        headers={
            "X-API-KEY": "wrong-test-api key",
        },
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}
