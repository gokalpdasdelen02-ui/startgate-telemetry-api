from copy import deepcopy


def test_get_daily_event_statistics(
    client,
    auth_headers,
    valid_info_event,
):
    first_event = deepcopy(valid_info_event)
    first_event["session_id"] = "daily-stats-session-001"

    second_event = deepcopy(valid_info_event)
    second_event["session_id"] = "daily-stats-session-002"

    first_response = client.post(
        "/events/",
        json=first_event,
        headers=auth_headers,
    )

    second_response = client.post(
        "/events/",
        json=second_event,
        headers=auth_headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get(
        "/stats/daily-events",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["status"] == "success"
    assert len(response_body["data"]) == 1
    assert response_body["data"][0]["event_count"] == 2


def test_get_active_user_statistics(
    client,
    auth_headers,
    valid_info_event,
):
    first_user_event = deepcopy(valid_info_event)
    first_user_event["user_id"] = "active-user-001"
    first_user_event["session_id"] = "active-session-001"

    first_user_second_event = deepcopy(valid_info_event)
    first_user_second_event["user_id"] = "active-user-001"
    first_user_second_event["session_id"] = "active-session-002"

    second_user_event = deepcopy(valid_info_event)
    second_user_event["user_id"] = "active-user-002"
    second_user_event["session_id"] = "active-session-003"

    events_to_create = [
        first_user_event,
        first_user_second_event,
        second_user_event,
    ]

    for event_payload in events_to_create:
        create_response = client.post(
            "/events/",
            json=event_payload,
            headers=auth_headers,
        )

        assert create_response.status_code == 201

    response = client.get(
        "/stats/active-users",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["status"] == "success"
    assert response_body["active_users"] == 2
