"""Tests for EndUser Pydantic model and EndUsers resource."""

import pytest

from pyplanhat._exceptions import (
    APIError,
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    ServerError,
)
from pyplanhat._sync.resources.endusers import EndUser


def test_enduser_minimal_creation():
    """Test creating an end user with minimal fields."""
    enduser = EndUser(company_id="comp-123", email="user@example.com")

    assert enduser.company_id == "comp-123"
    assert enduser.email == "user@example.com"
    assert enduser.id is None
    assert enduser.external_id is None
    assert enduser.source_id is None
    assert enduser.custom == {}


def test_enduser_with_all_fields():
    """Test creating an end user with all fields populated."""
    enduser_data = {
        "companyId": "comp-123",
        "_id": "user-123",
        "email": "john@example.com",
        "externalId": "ext-456",
        "sourceId": "src-789",
        "firstName": "John",
        "lastName": "Doe",
        "name": "John Doe",
        "position": "CFO",
        "phone": "+1-555-0123",
        "featured": True,
        "primary": True,
        "archived": False,
        "tags": ["vip", "decision-maker"],
        "otherEmails": ["john.doe@example.com", "jdoe@example.com"],
        "lastActive": "2023-12-01T12:00:00Z",
        "beats": 100,
        "beatsTotal": 1500,
        "beatTrend": "up",
        "convs14": 5,
        "convsTotal": 50,
        "experience": "positive",
        "lastTouch": "2023-12-01T10:00:00Z",
        "lastTouchType": "email",
        "lastTouchByType": {"email": "2023-12-01", "call": "2023-11-30"},
        "nps": 9,
        "npsComment": "Great product!",
        "npsDate": "2023-11-15",
        "npsSent": "2023-11-10",
        "npsUnsubscribed": False,
        "lastActivities": [{"type": "email", "date": "2023-11-30"}],
        "relatedEndusers": ["user-456", "user-789"],
        "custom": {"department": "Finance", "seniority": "executive"},
    }

    enduser = EndUser(**enduser_data)

    assert enduser.company_id == "comp-123"
    assert enduser.id == "user-123"
    assert enduser.email == "john@example.com"
    assert enduser.external_id == "ext-456"
    assert enduser.source_id == "src-789"
    assert enduser.first_name == "John"
    assert enduser.last_name == "Doe"
    assert enduser.name == "John Doe"
    assert enduser.position == "CFO"
    assert enduser.phone == "+1-555-0123"
    assert enduser.featured is True
    assert enduser.primary is True
    assert enduser.archived is False
    assert enduser.tags == ["vip", "decision-maker"]
    assert enduser.other_emails == ["john.doe@example.com", "jdoe@example.com"]
    assert enduser.last_active == "2023-12-01T12:00:00Z"
    assert enduser.beats == 100
    assert enduser.beats_total == 1500
    assert enduser.beat_trend == "up"
    assert enduser.convs14 == 5
    assert enduser.convs_total == 50
    assert enduser.experience == "positive"
    assert enduser.last_touch == "2023-12-01T10:00:00Z"
    assert enduser.last_touch_type == "email"
    assert enduser.last_touch_by_type == {"email": "2023-12-01", "call": "2023-11-30"}
    assert enduser.nps == 9
    assert enduser.nps_comment == "Great product!"
    assert enduser.nps_date == "2023-11-15"
    assert enduser.nps_sent == "2023-11-10"
    assert enduser.nps_unsubscribed is False
    assert enduser.last_activities == [{"type": "email", "date": "2023-11-30"}]
    assert enduser.related_endusers == ["user-456", "user-789"]
    assert enduser.custom == {"department": "Finance", "seniority": "executive"}


def test_enduser_serialization_with_alias():
    """Test that model serializes correctly with aliases."""
    enduser = EndUser(
        company_id="comp-123",
        email="user@example.com",
        _id="user-123",
        external_id="ext-456",
        source_id="src-789",
        first_name="Jane",
        last_name="Smith",
        other_emails=["jane@example.com"],
        custom={"key": "value"},
    )

    data = enduser.model_dump(exclude_none=True, by_alias=True)

    assert data["companyId"] == "comp-123"
    assert data["email"] == "user@example.com"
    assert data["_id"] == "user-123"
    assert data["externalId"] == "ext-456"
    assert data["sourceId"] == "src-789"
    assert data["firstName"] == "Jane"
    assert data["lastName"] == "Smith"
    assert data["otherEmails"] == ["jane@example.com"]
    assert data["custom"] == {"key": "value"}

    # Ensure excluded None fields are not present
    assert "position" not in data
    assert "phone" not in data


def test_enduser_deserialization_from_api_response():
    """Test parsing EndUser from API response JSON."""
    api_response = {
        "_id": "user-123",
        "companyId": "comp-456",
        "email": "api-user@example.com",
        "firstName": "API",
        "lastName": "User",
        "position": "CTO",
        "primary": True,
        "tags": ["technical"],
        "nps": 10,
        "custom": {"tier": "Premium"},
    }

    enduser = EndUser(**api_response)

    assert enduser.id == "user-123"
    assert enduser.company_id == "comp-456"
    assert enduser.email == "api-user@example.com"
    assert enduser.first_name == "API"
    assert enduser.last_name == "User"
    assert enduser.position == "CTO"
    assert enduser.primary is True
    assert enduser.tags == ["technical"]
    assert enduser.nps == 10
    assert enduser.custom == {"tier": "Premium"}


def test_enduser_custom_fields_default_factory():
    """Test that custom fields use default factory correctly."""
    enduser1 = EndUser(company_id="comp-1", email="user1@example.com")
    enduser2 = EndUser(company_id="comp-2", email="user2@example.com")

    # Both should have empty dict for custom fields
    assert enduser1.custom == {}
    assert enduser2.custom == {}

    # They should be independent (not same object)
    assert enduser1.custom is not enduser2.custom


def test_enduser_field_population_by_name():
    """Test that fields can be populated by both name and alias."""
    # Using field names (snake_case)
    enduser1 = EndUser(
        company_id="comp-1",
        email="user1@example.com",
        external_id="ext-1",
        source_id="src-1",
        first_name="First1",
        last_name="Last1",
        other_emails=["other1@example.com"],
    )

    # Using aliases (camelCase)
    enduser2 = EndUser(
        companyId="comp-2",
        email="user2@example.com",
        externalId="ext-2",
        sourceId="src-2",
        firstName="First2",
        lastName="Last2",
        otherEmails=["other2@example.com"],
    )

    assert enduser1.company_id == "comp-1"
    assert enduser1.external_id == "ext-1"
    assert enduser1.source_id == "src-1"
    assert enduser1.first_name == "First1"
    assert enduser1.last_name == "Last1"
    assert enduser1.other_emails == ["other1@example.com"]

    assert enduser2.company_id == "comp-2"
    assert enduser2.external_id == "ext-2"
    assert enduser2.source_id == "src-2"
    assert enduser2.first_name == "First2"
    assert enduser2.last_name == "Last2"
    assert enduser2.other_emails == ["other2@example.com"]


# CRUD Tests for EndUsers Resource


def test_list_endusers_success(async_client, httpx_mock):
    """Test listing all end users successfully."""
    mock_response = [
        {
            "_id": "user-1",
            "companyId": "comp-123",
            "email": "user1@example.com",
            "firstName": "User",
            "lastName": "One",
            "primary": True,
        },
        {
            "_id": "user-2",
            "companyId": "comp-123",
            "email": "user2@example.com",
            "firstName": "User",
            "lastName": "Two",
            "primary": False,
        },
    ]

    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/endusers",
        json=mock_response,
    )

    endusers = async_client.endusers.list()

    assert len(endusers) == 2
    assert endusers[0].id == "user-1"
    assert endusers[0].email == "user1@example.com"
    assert endusers[0].first_name == "User"
    assert endusers[0].last_name == "One"
    assert endusers[0].primary is True

    assert endusers[1].id == "user-2"
    assert endusers[1].email == "user2@example.com"
    assert endusers[1].primary is False


def test_list_endusers_by_company(async_client, httpx_mock):
    """Test listing end users filtered by company."""
    mock_response = [
        {
            "_id": "user-1",
            "companyId": "comp-123",
            "email": "user1@example.com",
            "firstName": "User",
            "lastName": "One",
        },
    ]

    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies/comp-123/endusers",
        json=mock_response,
    )

    endusers = async_client.endusers.list(company_id="comp-123")

    assert len(endusers) == 1
    assert endusers[0].id == "user-1"
    assert endusers[0].company_id == "comp-123"


def test_list_endusers_empty(async_client, httpx_mock):
    """Test listing end users when no end users exist."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/endusers",
        json=[],
    )

    endusers = async_client.endusers.list()

    assert endusers == []


def test_get_enduser_success(async_client, httpx_mock):
    """Test getting a specific end user successfully."""
    mock_response = {
        "_id": "user-123",
        "companyId": "comp-456",
        "email": "user@example.com",
        "firstName": "Test",
        "lastName": "User",
        "position": "CEO",
        "custom": {"role": "executive"},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/endusers/user-123",
        json=mock_response,
    )

    enduser = async_client.endusers.get("user-123")

    assert enduser.id == "user-123"
    assert enduser.company_id == "comp-456"
    assert enduser.email == "user@example.com"
    assert enduser.first_name == "Test"
    assert enduser.last_name == "User"
    assert enduser.position == "CEO"
    assert enduser.custom == {"role": "executive"}


def test_get_enduser_not_found(async_client, httpx_mock):
    """Test getting a non-existent end user raises error."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/endusers/nonexistent",
        status_code=404,
        text="EndUser not found",
    )

    with pytest.raises(InvalidRequestError) as exc_info:
        async_client.endusers.get("nonexistent")

    assert exc_info.value.status_code == 404
    assert "EndUser not found" in exc_info.value.response_body


def test_create_enduser_success(async_client, httpx_mock):
    """Test creating a new end user successfully."""
    new_enduser = EndUser(
        company_id="comp-123",
        email="newuser@example.com",
        first_name="New",
        last_name="User",
        position="Manager",
        custom={"department": "Sales"},
    )

    mock_response = {
        "_id": "user-new",
        "companyId": "comp-123",
        "email": "newuser@example.com",
        "firstName": "New",
        "lastName": "User",
        "position": "Manager",
        "custom": {"department": "Sales"},
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.planhat.com/endusers",
        status_code=201,
        json=mock_response,
    )

    created_enduser = async_client.endusers.create(new_enduser)

    assert created_enduser.id == "user-new"
    assert created_enduser.company_id == "comp-123"
    assert created_enduser.email == "newuser@example.com"
    assert created_enduser.first_name == "New"
    assert created_enduser.last_name == "User"
    assert created_enduser.position == "Manager"
    assert created_enduser.custom == {"department": "Sales"}


def test_create_enduser_validation_error(async_client, httpx_mock):
    """Test creating an end user with invalid data raises error."""
    httpx_mock.add_response(
        method="POST",
        url="https://api.planhat.com/endusers",
        status_code=400,
        text="Invalid request: missing required field",
    )

    enduser = EndUser(company_id="comp-123", email="test@example.com")

    with pytest.raises(APIError) as exc_info:
        async_client.endusers.create(enduser)

    assert exc_info.value.status_code == 400
    assert "Invalid request" in str(exc_info.value)


def test_update_enduser_success(async_client, httpx_mock):
    """Test updating an existing end user successfully."""
    updated_enduser = EndUser(
        company_id="comp-123",
        email="updated@example.com",
        first_name="Updated",
        last_name="Name",
        position="Director",
    )

    mock_response = {
        "_id": "user-123",
        "companyId": "comp-123",
        "email": "updated@example.com",
        "firstName": "Updated",
        "lastName": "Name",
        "position": "Director",
    }

    httpx_mock.add_response(
        method="PUT",
        url="https://api.planhat.com/endusers/user-123",
        json=mock_response,
    )

    result = async_client.endusers.update("user-123", updated_enduser)

    assert result.id == "user-123"
    assert result.email == "updated@example.com"
    assert result.first_name == "Updated"
    assert result.last_name == "Name"
    assert result.position == "Director"


def test_update_enduser_not_found(async_client, httpx_mock):
    """Test updating a non-existent end user raises error."""
    httpx_mock.add_response(
        method="PUT",
        url="https://api.planhat.com/endusers/nonexistent",
        status_code=404,
        text="EndUser not found",
    )

    enduser = EndUser(company_id="comp-123", email="test@example.com")

    with pytest.raises(InvalidRequestError) as exc_info:
        async_client.endusers.update("nonexistent", enduser)

    assert exc_info.value.status_code == 404
    assert "EndUser not found" in exc_info.value.response_body


def test_delete_enduser_success(async_client, httpx_mock):
    """Test deleting an end user successfully."""
    httpx_mock.add_response(
        method="DELETE",
        url="https://api.planhat.com/endusers/user-123",
        status_code=204,
    )

    # Should not raise any exception
    async_client.endusers.delete("user-123")


def test_delete_enduser_not_found(async_client, httpx_mock):
    """Test deleting a non-existent end user raises error."""
    httpx_mock.add_response(
        method="DELETE",
        url="https://api.planhat.com/endusers/nonexistent",
        status_code=404,
        text="EndUser not found",
    )

    with pytest.raises(InvalidRequestError) as exc_info:
        async_client.endusers.delete("nonexistent")

    assert exc_info.value.status_code == 404
    assert "EndUser not found" in exc_info.value.response_body


def test_enduser_authentication_error(async_client, httpx_mock):
    """Test authentication error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/endusers",
        status_code=401,
        text="Invalid API key",
    )

    with pytest.raises(AuthenticationError) as exc_info:
        async_client.endusers.list()

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.response_body


def test_enduser_rate_limit_error(async_client, httpx_mock):
    """Test rate limit error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/endusers",
        status_code=429,
        text="Rate limit exceeded",
    )

    with pytest.raises(RateLimitError) as exc_info:
        async_client.endusers.list()

    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value)


def test_enduser_server_error(async_client, httpx_mock):
    """Test server error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/endusers",
        status_code=500,
        text="Internal server error",
    )

    with pytest.raises(ServerError) as exc_info:
        async_client.endusers.list()

    assert exc_info.value.status_code == 500
    assert "Internal server error" in str(exc_info.value)
