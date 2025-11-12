"""Tests for Conversation Pydantic model and Conversations resource."""

import pytest

from pyplanhat._async.resources.conversations import Conversation
from pyplanhat._exceptions import (
    APIError,
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    ServerError,
)


def test_conversation_minimal_creation():
    """Test creating a conversation with minimal fields."""
    conversation = Conversation(company_id="comp-123")

    assert conversation.company_id == "comp-123"
    assert conversation.id is None
    assert conversation.external_id is None
    assert conversation.type is None
    assert conversation.custom == {}


def test_conversation_with_all_fields():
    """Test creating a conversation with all fields populated."""
    conversation_data = {
        "companyId": "comp-123",
        "_id": "conv-123",
        "externalId": "ext-456",
        "type": "email",
        "subject": "Important Discussion",
        "description": "Details about the conversation",
        "snippet": "Quick preview of content",
        "date": "2023-12-01T10:00:00Z",
        "outDate": "2023-12-01T11:00:00Z",
        "createDate": "2023-12-01T09:00:00Z",
        "users": [{"id": "user-1", "name": "John Doe", "isOwner": True}],
        "endusers": ["enduser-1", "enduser-2"],
        "userIds": ["user-1", "user-2"],
        "starred": True,
        "pinned": False,
        "archived": False,
        "isOpen": True,
        "tags": ["important", "follow-up"],
        "activityTags": ["meeting", "discussion"],
        "hasAttachments": True,
        "hasMore": False,
        "emailTemplateIds": ["template-1", "template-2"],
        "timeBucket": [{"hour": 10, "count": 5}],
        "sender": [{"email": "sender@example.com", "name": "Sender Name"}],
        "history": [{"action": "created", "timestamp": "2023-12-01"}],
        "isCustomType": False,
        "assigneeName": "Jane Smith",
        "numberOfParts": 3,
        "numberOfRelevantParts": 2,
        "custom": {"priority": "high", "category": "sales"},
    }

    conversation = Conversation(**conversation_data)

    assert conversation.company_id == "comp-123"
    assert conversation.id == "conv-123"
    assert conversation.external_id == "ext-456"
    assert conversation.type == "email"
    assert conversation.subject == "Important Discussion"
    assert conversation.description == "Details about the conversation"
    assert conversation.snippet == "Quick preview of content"
    assert conversation.date == "2023-12-01T10:00:00Z"
    assert conversation.out_date == "2023-12-01T11:00:00Z"
    assert conversation.create_date == "2023-12-01T09:00:00Z"
    assert conversation.users == [{"id": "user-1", "name": "John Doe", "isOwner": True}]
    assert conversation.endusers == ["enduser-1", "enduser-2"]
    assert conversation.user_ids == ["user-1", "user-2"]
    assert conversation.starred is True
    assert conversation.pinned is False
    assert conversation.archived is False
    assert conversation.is_open is True
    assert conversation.tags == ["important", "follow-up"]
    assert conversation.activity_tags == ["meeting", "discussion"]
    assert conversation.has_attachments is True
    assert conversation.has_more is False
    assert conversation.email_template_ids == ["template-1", "template-2"]
    assert conversation.time_bucket == [{"hour": 10, "count": 5}]
    assert conversation.sender == [{"email": "sender@example.com", "name": "Sender Name"}]
    assert conversation.history == [{"action": "created", "timestamp": "2023-12-01"}]
    assert conversation.is_custom_type is False
    assert conversation.assignee_name == "Jane Smith"
    assert conversation.number_of_parts == 3
    assert conversation.number_of_relevant_parts == 2
    assert conversation.custom == {"priority": "high", "category": "sales"}


def test_conversation_serialization_with_alias():
    """Test that model serializes correctly with aliases."""
    conversation = Conversation(
        company_id="comp-123",
        _id="conv-123",
        external_id="ext-456",
        type="note",
        subject="Test Subject",
        out_date="2023-12-01T12:00:00Z",
        create_date="2023-12-01T11:00:00Z",
        user_ids=["user-1", "user-2"],
        is_open=True,
        activity_tags=["tag1", "tag2"],
        has_attachments=True,
        email_template_ids=["tmpl-1"],
        custom={"key": "value"},
    )

    data = conversation.model_dump(exclude_none=True, by_alias=True)

    assert data["companyId"] == "comp-123"
    assert data["_id"] == "conv-123"
    assert data["externalId"] == "ext-456"
    assert data["type"] == "note"
    assert data["subject"] == "Test Subject"
    assert data["outDate"] == "2023-12-01T12:00:00Z"
    assert data["createDate"] == "2023-12-01T11:00:00Z"
    assert data["userIds"] == ["user-1", "user-2"]
    assert data["isOpen"] is True
    assert data["activityTags"] == ["tag1", "tag2"]
    assert data["hasAttachments"] is True
    assert data["emailTemplateIds"] == ["tmpl-1"]
    assert data["custom"] == {"key": "value"}

    # Ensure excluded None fields are not present
    assert "description" not in data
    assert "starred" not in data


def test_conversation_deserialization_from_api_response():
    """Test parsing Conversation from API response JSON."""
    api_response = {
        "_id": "conv-123",
        "companyId": "comp-456",
        "type": "call",
        "subject": "Sales Call",
        "description": "Discussed pricing options",
        "date": "2023-11-30T14:00:00Z",
        "users": [{"id": "user-1", "name": "Sales Rep"}],
        "tags": ["sales", "pricing"],
        "starred": True,
        "custom": {"outcome": "positive"},
    }

    conversation = Conversation(**api_response)

    assert conversation.id == "conv-123"
    assert conversation.company_id == "comp-456"
    assert conversation.type == "call"
    assert conversation.subject == "Sales Call"
    assert conversation.description == "Discussed pricing options"
    assert conversation.date == "2023-11-30T14:00:00Z"
    assert conversation.users == [{"id": "user-1", "name": "Sales Rep"}]
    assert conversation.tags == ["sales", "pricing"]
    assert conversation.starred is True
    assert conversation.custom == {"outcome": "positive"}


def test_conversation_custom_fields_default_factory():
    """Test that custom fields use default factory correctly."""
    conv1 = Conversation(company_id="comp-1")
    conv2 = Conversation(company_id="comp-2")

    # Both should have empty dict for custom fields
    assert conv1.custom == {}
    assert conv2.custom == {}

    # They should be independent (not same object)
    assert conv1.custom is not conv2.custom


def test_conversation_field_population_by_name():
    """Test that fields can be populated by both name and alias."""
    # Using field names (snake_case)
    conv1 = Conversation(
        company_id="comp-1",
        external_id="ext-1",
        out_date="2023-12-01",
        create_date="2023-12-02",
        user_ids=["user-1"],
        is_open=True,
        activity_tags=["tag1"],
    )

    # Using aliases (camelCase)
    conv2 = Conversation(
        companyId="comp-2",
        externalId="ext-2",
        outDate="2023-12-03",
        createDate="2023-12-04",
        userIds=["user-2"],
        isOpen=False,
        activityTags=["tag2"],
    )

    assert conv1.company_id == "comp-1"
    assert conv1.external_id == "ext-1"
    assert conv1.out_date == "2023-12-01"
    assert conv1.create_date == "2023-12-02"
    assert conv1.user_ids == ["user-1"]
    assert conv1.is_open is True
    assert conv1.activity_tags == ["tag1"]

    assert conv2.company_id == "comp-2"
    assert conv2.external_id == "ext-2"
    assert conv2.out_date == "2023-12-03"
    assert conv2.create_date == "2023-12-04"
    assert conv2.user_ids == ["user-2"]
    assert conv2.is_open is False
    assert conv2.activity_tags == ["tag2"]


# CRUD Tests for Conversations Resource


@pytest.mark.asyncio
async def test_list_conversations_success(async_client, httpx_mock):
    """Test listing all conversations successfully."""
    mock_response = [
        {
            "_id": "conv-1",
            "companyId": "comp-123",
            "type": "email",
            "subject": "Follow-up Email",
            "date": "2023-12-01T10:00:00Z",
            "starred": True,
        },
        {
            "_id": "conv-2",
            "companyId": "comp-123",
            "type": "call",
            "subject": "Discovery Call",
            "date": "2023-11-30T15:00:00Z",
            "starred": False,
        },
    ]

    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/conversations",
        json=mock_response,
    )

    conversations = await async_client.conversations.list()

    assert len(conversations) == 2
    assert conversations[0].id == "conv-1"
    assert conversations[0].type == "email"
    assert conversations[0].subject == "Follow-up Email"
    assert conversations[0].starred is True

    assert conversations[1].id == "conv-2"
    assert conversations[1].type == "call"
    assert conversations[1].subject == "Discovery Call"
    assert conversations[1].starred is False


@pytest.mark.asyncio
async def test_list_conversations_by_company(async_client, httpx_mock):
    """Test listing conversations filtered by company."""
    mock_response = [
        {
            "_id": "conv-1",
            "companyId": "comp-123",
            "type": "note",
            "subject": "Meeting Notes",
        },
    ]

    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies/comp-123/conversations",
        json=mock_response,
    )

    conversations = await async_client.conversations.list(company_id="comp-123")

    assert len(conversations) == 1
    assert conversations[0].id == "conv-1"
    assert conversations[0].company_id == "comp-123"


@pytest.mark.asyncio
async def test_list_conversations_empty(async_client, httpx_mock):
    """Test listing conversations when no conversations exist."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/conversations",
        json=[],
    )

    conversations = await async_client.conversations.list()

    assert conversations == []


@pytest.mark.asyncio
async def test_get_conversation_success(async_client, httpx_mock):
    """Test getting a specific conversation successfully."""
    mock_response = {
        "_id": "conv-123",
        "companyId": "comp-456",
        "type": "email",
        "subject": "Important Update",
        "description": "Details about the update",
        "date": "2023-12-01T10:00:00Z",
        "custom": {"priority": "high"},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/conversations/conv-123",
        json=mock_response,
    )

    conversation = await async_client.conversations.get("conv-123")

    assert conversation.id == "conv-123"
    assert conversation.company_id == "comp-456"
    assert conversation.type == "email"
    assert conversation.subject == "Important Update"
    assert conversation.description == "Details about the update"
    assert conversation.custom == {"priority": "high"}


@pytest.mark.asyncio
async def test_get_conversation_not_found(async_client, httpx_mock):
    """Test getting a non-existent conversation raises error."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/conversations/nonexistent",
        status_code=404,
        text="Conversation not found",
    )

    with pytest.raises(InvalidRequestError) as exc_info:
        await async_client.conversations.get("nonexistent")

    assert exc_info.value.status_code == 404
    assert "Conversation not found" in exc_info.value.response_body


@pytest.mark.asyncio
async def test_create_conversation_success(async_client, httpx_mock):
    """Test creating a new conversation successfully."""
    new_conversation = Conversation(
        company_id="comp-123",
        type="note",
        subject="New Note",
        description="Important information",
        custom={"category": "internal"},
    )

    mock_response = {
        "_id": "conv-new",
        "companyId": "comp-123",
        "type": "note",
        "subject": "New Note",
        "description": "Important information",
        "custom": {"category": "internal"},
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.planhat.com/conversations",
        status_code=201,
        json=mock_response,
    )

    created_conversation = await async_client.conversations.create(new_conversation)

    assert created_conversation.id == "conv-new"
    assert created_conversation.company_id == "comp-123"
    assert created_conversation.type == "note"
    assert created_conversation.subject == "New Note"
    assert created_conversation.description == "Important information"
    assert created_conversation.custom == {"category": "internal"}


@pytest.mark.asyncio
async def test_create_conversation_validation_error(async_client, httpx_mock):
    """Test creating a conversation with invalid data raises error."""
    httpx_mock.add_response(
        method="POST",
        url="https://api.planhat.com/conversations",
        status_code=400,
        text="Invalid request: missing required field",
    )

    conversation = Conversation(company_id="comp-123")

    with pytest.raises(APIError) as exc_info:
        await async_client.conversations.create(conversation)

    assert exc_info.value.status_code == 400
    assert "Invalid request" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_conversation_success(async_client, httpx_mock):
    """Test updating an existing conversation successfully."""
    updated_conversation = Conversation(
        company_id="comp-123",
        subject="Updated Subject",
        description="Updated description",
        starred=True,
    )

    mock_response = {
        "_id": "conv-123",
        "companyId": "comp-123",
        "subject": "Updated Subject",
        "description": "Updated description",
        "starred": True,
    }

    httpx_mock.add_response(
        method="PUT",
        url="https://api.planhat.com/conversations/conv-123",
        json=mock_response,
    )

    result = await async_client.conversations.update("conv-123", updated_conversation)

    assert result.id == "conv-123"
    assert result.subject == "Updated Subject"
    assert result.description == "Updated description"
    assert result.starred is True


@pytest.mark.asyncio
async def test_update_conversation_not_found(async_client, httpx_mock):
    """Test updating a non-existent conversation raises error."""
    httpx_mock.add_response(
        method="PUT",
        url="https://api.planhat.com/conversations/nonexistent",
        status_code=404,
        text="Conversation not found",
    )

    conversation = Conversation(company_id="comp-123")

    with pytest.raises(InvalidRequestError) as exc_info:
        await async_client.conversations.update("nonexistent", conversation)

    assert exc_info.value.status_code == 404
    assert "Conversation not found" in exc_info.value.response_body


@pytest.mark.asyncio
async def test_delete_conversation_success(async_client, httpx_mock):
    """Test deleting a conversation successfully."""
    httpx_mock.add_response(
        method="DELETE",
        url="https://api.planhat.com/conversations/conv-123",
        status_code=204,
    )

    # Should not raise any exception
    await async_client.conversations.delete("conv-123")


@pytest.mark.asyncio
async def test_delete_conversation_not_found(async_client, httpx_mock):
    """Test deleting a non-existent conversation raises error."""
    httpx_mock.add_response(
        method="DELETE",
        url="https://api.planhat.com/conversations/nonexistent",
        status_code=404,
        text="Conversation not found",
    )

    with pytest.raises(InvalidRequestError) as exc_info:
        await async_client.conversations.delete("nonexistent")

    assert exc_info.value.status_code == 404
    assert "Conversation not found" in exc_info.value.response_body


@pytest.mark.asyncio
async def test_conversation_authentication_error(async_client, httpx_mock):
    """Test authentication error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/conversations",
        status_code=401,
        text="Invalid API key",
    )

    with pytest.raises(AuthenticationError) as exc_info:
        await async_client.conversations.list()

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.response_body


@pytest.mark.asyncio
async def test_conversation_rate_limit_error(async_client, httpx_mock):
    """Test rate limit error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/conversations",
        status_code=429,
        text="Rate limit exceeded",
    )

    with pytest.raises(RateLimitError) as exc_info:
        await async_client.conversations.list()

    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_conversation_server_error(async_client, httpx_mock):
    """Test server error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/conversations",
        status_code=500,
        text="Internal server error",
    )

    with pytest.raises(ServerError) as exc_info:
        await async_client.conversations.list()

    assert exc_info.value.status_code == 500
    assert "Internal server error" in str(exc_info.value)
