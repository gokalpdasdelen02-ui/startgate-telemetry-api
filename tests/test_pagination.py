from copy import deepcopy


def test_get_events_with_skip_and_limit_returns_requested_page(
    client,
    auth_headers,
    valid_info_event,
):

    events_to_create = []

    for event_number in range(1, 4):
        event_payload = deepcopy(valid_info_event)
        event_payload["session_id"] = f"pagination_test_session_{event_number}"
        event_payload["event_data"]["message"] = f"Pagination test event {event_number}"
        events_to_create.append(event_payload)

    for event_payload in events_to_create:
        create_response = client.post(
            "/events/",
            json=event_payload,
            headers=auth_headers,
        )

        assert create_response.status_code == 201, create_response.json()

    response = client.get(
        "/events/?skip=1&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["status"] == "success"
    assert response_body["total"] == 3
    assert response_body["count"] == 2
    assert response_body["skip"] == 1
    assert response_body["limit"] == 2
    assert len(response_body["data"]) == 2

    returned_session_ids = [event["session_id"] for event in response_body["data"]]

    assert returned_session_ids == [
        "pagination_test_session_2",
        "pagination_test_session_1",
    ]


def test_get_events_with_negative_skip_returns_422(
    client,
    auth_headers,
):
    response = client.get(
        "/events/?skip=-1&limit=10",
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "greater_than_equal" and error["loc"][-1] == "skip"
        for error in errors
    )


def test_get_events_with_zero_limit_returns_422(
    client,
    auth_headers,
):

    response = client.get(
        "/events/?skip=0&limit=0",
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "greater_than_equal" and error["loc"][-1] == "limit"
        for error in errors
    )


def test_get_events_with_limit_above_maximum_returns_422(
    client,
    auth_headers,
):
    response = client.get(
        "/events/?skip=0&limit=101",
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "less_than_equal" and error["loc"][-1] == "limit"
        for error in errors
    )


def test_get_user_events_with_skip_and_limit_returns_requested_page(
    client,
    auth_headers,
    valid_info_event,
):
    first_target_event = deepcopy(valid_info_event)
    first_target_event["user_id"] = "pagination-user-001"
    first_target_event["session_id"] = "target-session-1"
    first_target_event["event_data"]["message"] = "Target event one"

    second_target_event = deepcopy(valid_info_event)
    second_target_event["user_id"] = "pagination-user-001"
    second_target_event["session_id"] = "target-session-2"
    second_target_event["event_data"]["message"] = "Target event two"

    other_user_event = deepcopy(valid_info_event)
    other_user_event["user_id"] = "pagination-user-002"
    other_user_event["session_id"] = "other-session-1"
    other_user_event["event_data"]["message"] = "Other user event"

    third_target_event = deepcopy(valid_info_event)
    third_target_event["user_id"] = "pagination-user-001"
    third_target_event["session_id"] = "target-session-3"
    third_target_event["event_data"]["message"] = "Target event three"

    events_to_create = [
        first_target_event,
        second_target_event,
        other_user_event,
        third_target_event,
    ]

    for event_payload in events_to_create:
        create_response = client.post(
            "/events/",
            json=event_payload,
            headers=auth_headers,
        )

        assert create_response.status_code == 201, create_response.json()

    response = client.get(
        "/events/user/pagination-user-001?skip=1&limit=1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["status"] == "success"
    assert response_body["user_id"] == "pagination-user-001"
    assert response_body["total"] == 3
    assert response_body["count"] == 1
    assert response_body["skip"] == 1
    assert response_body["limit"] == 1
    assert len(response_body["data"]) == 1

    returned_event = response_body["data"][0]

    assert returned_event["user_id"] == "pagination-user-001"
    assert returned_event["session_id"] == "target-session-2"


def test_get_events_with_skip_beyond_total_returns_empty_page(
    client,
    auth_headers,
    valid_info_event,
):
    for event_number in range(1, 4):
        event_payload = deepcopy(valid_info_event)
        event_payload["session_id"] = f"skip-beyond-total-session-{event_number}"
        event_payload["event_data"][
            "message"
        ] = f"Skip beyond total event {event_number}"

        create_response = client.post(
            "/events/",
            json=event_payload,
            headers=auth_headers,
        )

        assert create_response.status_code == 201, create_response.json()

    response = client.get(
        "/events/?skip=10&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["status"] == "success"
    assert response_body["total"] == 3
    assert response_body["count"] == 0
    assert response_body["skip"] == 10
    assert response_body["limit"] == 2
    assert response_body["data"] == []
