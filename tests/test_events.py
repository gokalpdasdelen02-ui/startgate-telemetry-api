from copy import deepcopy


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
            "X-API-Key": "wrong-test-api-key",
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
            "X-API-Key": "wrong-test-api-key",
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
            "X-API-Key": "wrong-test-api-key",
        },
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}


def test_get_user_events_returns_only_requested_users_events(
    client, auth_headers, valid_info_event
):

    first_user_event_1 = deepcopy(valid_info_event)
    first_user_event_1["session_id"] = "first-user-session-001"
    first_user_event_1["event_data"]["message"] = "First user event one"

    first_user_event_2 = deepcopy(valid_info_event)
    first_user_event_2["session_id"] = "first-user-session-002"
    first_user_event_2["event_data"]["message"] = "First user event two"

    second_user_event = deepcopy(valid_info_event)
    second_user_event["user_id"] = "test-user-002"
    second_user_event["session_id"] = "second-user-session-001"
    second_user_event["event_data"]["message"] = "Second user event"

    events_to_create = [
        first_user_event_1,
        first_user_event_2,
        second_user_event,
    ]

    for event_payload in events_to_create:
        create_response = client.post(
            "/events/",
            json=event_payload,
            headers=auth_headers,
        )

        assert create_response.status_code == 201, create_response.json()

    response = client.get(
        "/events/user/test-user-001",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["status"] == "success"
    assert response_body["user_id"] == "test-user-001"
    assert response_body["total"] == 2
    assert response_body["count"] == 2
    assert len(response_body["data"]) == 2

    returned_events = response_body["data"]

    assert all(event["user_id"] == "test-user-001" for event in returned_events)

    returned_session_ids = {event["session_id"] for event in returned_events}

    assert returned_session_ids == {
        "first-user-session-001",
        "first-user-session-002",
    }


def test_get_events_for_unknown_user_returns_empty_list(
    client,
    auth_headers,
):
    response = client.get(
        "/events/user/unknown-user",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["status"] == "success"
    assert response_body["user_id"] == "unknown-user"
    assert response_body["total"] == 0
    assert response_body["count"] == 0
    assert response_body["skip"] == 0
    assert response_body["limit"] == 10
    assert response_body["data"] == []


def test_create_batch_events_returns_201(
    client,
    auth_headers,
    valid_info_event,
):
    first_event = deepcopy(valid_info_event)
    first_event["session_id"] = "batch-session-001"
    first_event["event_data"]["message"] = "First batch event"

    second_event = deepcopy(valid_info_event)
    second_event["user_id"] = "batch-user-002"
    second_event["session_id"] = "batch-session-002"
    second_event["event_data"]["message"] = "Second batch event"

    response = client.post(
        "/events/batch",
        json={
            "events": [
                first_event,
                second_event,
            ]
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["status"] == "success"
    assert response_body["created_count"] == 2
    assert len(response_body["data"]) == 2


def test_create_batch_with_empty_list_returns_422(client, auth_headers):
    response = client.post(
        "/events/batch",
        json={"events": []},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_get_events_filters_by_category(
    client,
    auth_headers,
    valid_info_event,
):
    info_event = deepcopy(valid_info_event)
    info_event["session_id"] = "category-info-session"

    business_event = deepcopy(valid_info_event)
    business_event["category"] = "business"
    business_event["user_id"] = "business-user"
    business_event["session_id"] = "category-business-session"
    business_event["event_data"] = {
        "currency": "TRY",
        "amount": 100,
        "cart_type": "shop",
    }

    info_response = client.post(
        "/events/",
        json=info_event,
        headers=auth_headers,
    )

    business_response = client.post(
        "/events/",
        json=business_event,
        headers=auth_headers,
    )

    assert info_response.status_code == 201
    assert business_response.status_code == 201

    response = client.get(
        "/events/",
        params={
            "category": "business",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["total"] == 1
    assert response_body["count"] == 1
    assert len(response_body["data"]) == 1
    assert response_body["data"][0]["category"] == "business"


def test_get_events_with_reversed_date_range_returns_422(
    client,
    auth_headers,
):
    response = client.get(
        "/events/",
        params={
            "date_from": "2026-08-10T00:00:00Z",
            "date_to": "2026-08-01T00:00:00Z",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "date_from date_to değerinden sonra olamaz.",
    }


def test_get_events_filters_by_date_range(
    client,
    auth_headers,
    valid_info_event,
):
    old_event = deepcopy(valid_info_event)
    old_event["timestamp"] = "2026-08-01T10:00:00Z"
    old_event["session_id"] = "date-filter-old-session"
    old_event["event_data"]["message"] = "Old event"

    matching_event = deepcopy(valid_info_event)
    matching_event["timestamp"] = "2026-08-05T10:00:00Z"
    matching_event["session_id"] = "date-filter-matching-session"
    matching_event["event_data"]["message"] = "Matching event"

    new_event = deepcopy(valid_info_event)
    new_event["timestamp"] = "2026-08-10T10:00:00Z"
    new_event["session_id"] = "date-filter-new-session"
    new_event["event_data"]["message"] = "New event"

    events_to_create = [
        old_event,
        matching_event,
        new_event,
    ]

    for event_payload in events_to_create:
        create_response = client.post(
            "/events/",
            json=event_payload,
            headers=auth_headers,
        )

        assert create_response.status_code == 201, create_response.json()

    response = client.get(
        "/events/",
        params={
            "date_from": "2026-08-04T00:00:00Z",
            "date_to": "2026-08-06T23:59:59Z",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["total"] == 1
    assert response_body["count"] == 1
    assert len(response_body["data"]) == 1

    returned_event = response_body["data"][0]

    assert returned_event["session_id"] == "date-filter-matching-session"
    assert returned_event["event_data"]["message"] == "Matching event"


def test_batch_with_invalid_event_does_not_create_any_records(
    client,
    auth_headers,
    valid_info_event,
):
    valid_event = deepcopy(valid_info_event)
    valid_event["session_id"] = "atomic-batch-valid-session"
    valid_event["event_data"]["message"] = "Valid event in invalid batch"

    invalid_event = deepcopy(valid_info_event)
    invalid_event["session_id"] = "atomic-batch-invalid-session"
    invalid_event["session_num"] = 0
    invalid_event["event_data"]["message"] = "Invalid event in batch"

    batch_response = client.post(
        "/events/batch",
        json={
            "events": [
                valid_event,
                invalid_event,
            ]
        },
        headers=auth_headers,
    )

    assert batch_response.status_code == 422

    list_response = client.get(
        "/events/",
        headers=auth_headers,
    )

    assert list_response.status_code == 200

    response_body = list_response.json()

    assert response_body["total"] == 0
    assert response_body["count"] == 0
    assert response_body["data"] == []
