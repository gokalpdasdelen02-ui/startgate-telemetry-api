from copy import deepcopy


def test_create_event_with_extra_top_level_field_returns_422(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)
    event_payload["unxpected_field"] = "unexpected-value"

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "extra_forbidden" and error["loc"][-1] == "unxpected_field"
        for error in errors
    )


def test_create_event_with_extra_event_data_field_returns_422(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)
    event_payload["event_data"]["unexpected_event_field"] = "unexpected-value"

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "extra_forbidden"
        and error["loc"][-1] == "unexpected_event_field"
        for error in errors
    )


def test_create_event_with_blank_message_return_422(
    client,
    auth_headers,
    valid_info_event,
):

    event_payload = deepcopy(valid_info_event)
    event_payload["event_data"]["message"] = "  "

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["loc"][-1] == "message"
        and "Metin alanları boş bırakılamaz" in error["msg"]
        for error in errors
    )


def test_create_event__trims_message_whitespace(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)
    event_payload["event_data"]["message"] = "   Test event message   "

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 201

    response_body = response.json()
    created_event = response_body["data"]

    assert created_event["event_data"]["message"] == "Test event message"

    list_response = client.get(
        "/events/",
        headers=auth_headers,
    )

    assert list_response.status_code == 200

    stored_events = list_response.json()["data"][0]

    assert stored_events["event_data"]["message"] == "Test event message"


def test_create_event_without_required_user_id_returns_422(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)
    del event_payload["user_id"]

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "missing" and error["loc"][-1] == "user_id" for error in errors
    )


def test_create_event_with_zero_session_num_returns_422(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)
    event_payload["session_num"] = 0

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "greater_than" and error["loc"][-1] == "session_num"
        for error in errors
    )


def test_create_event_with_negative_client_ts_returns_422(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)
    event_payload["client_ts"] = -1

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "greater_than_equal" and error["loc"][-1] == "client_ts"
        for error in errors
    )


def test_create_event_with_mismatched_category_and_event_data_returns_422(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)
    event_payload["category"] = "business"

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "value_error"
        and "'business' kategorisi" in error["msg"]
        and "BusinessData" in error["msg"]
        for error in errors
    )


def test_create_business_event_with_lowercase_currency_returns_422(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)

    event_payload["category"] = "business"
    event_payload["event_data"] = {
        "currency": "try",
        "amount": 3500,
        "cart_type": "shop",
    }

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "value_error" and error["loc"][-1] == "currency"
        for error in errors
    )


def test_create_business_event_with_zero_amount_returns_422(
    client,
    auth_headers,
    valid_info_event,
):
    event_payload = deepcopy(valid_info_event)

    event_payload["category"] = "business"
    event_payload["event_data"] = {
        "currency": "USD",
        "amount": 0,
        "cart_type": "shop",
    }

    response = client.post(
        "/events/",
        json=event_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "greater_than" and error["loc"][-1] == "amount"
        for error in errors
    )
