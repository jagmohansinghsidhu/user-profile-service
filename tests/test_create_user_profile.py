import pytest
from fastapi import status
from sqlmodel import select

from api.models import UserProfile
from api.db import SessionLocal


@pytest.fixture
def valid_payload():
    return {
        "name": "Jagmohan Singh Sidhu",
        "email": "jagmohan@mysite.com",
        "age": 34
    }


@pytest.mark.parametrize("payload, expected_age", [
    ({"name": "Alice", "email": "alice@company.com", "age": 25}, 25),
    ({"name": "Bob",   "email": "bob@home.io"}, None),
])
def test_create_user_profile_success(client, payload, expected_age):
    response = client.post("/users", json=payload)

    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["age"] == expected_age


@pytest.mark.parametrize("field, invalid_value, expected_msg_snippet", [
    ("name", "", "String should have at least 1 character"),
    ("email", "email@invalid", "value is not a valid email address"),
    ("age", 0, "Input should be greater than 0"),
    ("age", 130, "Input should be less than 130"),
])
def test_create_user_profile_validation_errors(
    client, valid_payload, field, invalid_value, expected_msg_snippet
):
    bad_payload = valid_payload.copy()
    bad_payload[field] = invalid_value

    response = client.post("/users", json=bad_payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]

    found = False
    for err in errors:
        if field in err["loc"] and expected_msg_snippet.lower() in err["msg"].lower():
            found = True
            break

    assert found, f"Expected validation error for {field} not found"


def test_create_user_profile_duplicate_email(client, valid_payload):
    client.post("/users", json=valid_payload)

    duplicate = valid_payload.copy()
    duplicate["name"] = "John Doe"

    response = client.post("/users", json=duplicate)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error = response.json()["detail"]
    assert error == f'User Profile with email: {valid_payload["email"]} already exists'


@pytest.mark.parametrize("age_values", [None, 1, 129])
def test_create_user_profile_age_optional_and_bounds(client, valid_payload, age_values):
    payload = valid_payload.copy()
    payload["age"] = age_values

    response = client.post("/users", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["age"] == age_values


def test_create_user_profile_actually_persisted(client, valid_payload):
    response = client.post("/users", json=valid_payload)
    assert response.status_code == 201

    created_id = response.json()["id"]

    session = SessionLocal()
    stmt = select(UserProfile).where(UserProfile.id == created_id)
    result = session.exec(stmt).first()

    assert result is not None
    assert result.email == valid_payload["email"]
    assert result.name == valid_payload["name"]
