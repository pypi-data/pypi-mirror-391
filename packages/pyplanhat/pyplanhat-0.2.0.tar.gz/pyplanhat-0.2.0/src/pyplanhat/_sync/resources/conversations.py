"""Conversation resource for PyPlanhat SDK."""

from typing import Any, cast

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from pyplanhat._exceptions import InvalidRequestError
from pyplanhat._sync.resources.base import BaseResource


class Conversation(BaseModel):
    """Conversation resource from Planhat API.

    Represents a conversation/activity with all documented fields from the Planhat API schema.
    Note: The Planhat API requires companyId, but this field is optional at the model
    level for flexibility.
    """

    # Required by Planhat API
    company_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("companyId", "company_id"),
        serialization_alias="companyId",
    )

    # Key properties
    id: str | None = Field(
        default=None, validation_alias=AliasChoices("_id", "id"), serialization_alias="_id"
    )
    external_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("externalId", "external_id"),
        serialization_alias="externalId",
    )
    type: str | None = None  # Defaults to "note" if not specified

    # Core content fields
    subject: str | None = None  # Conversation title
    description: str | None = None  # Conversation content
    snippet: str | None = None  # Formatted content

    # Timestamps
    date: str | None = None  # ISO timestamp
    out_date: str | None = Field(
        default=None,
        validation_alias=AliasChoices("outDate", "out_date"),
        serialization_alias="outDate",
    )  # ISO timestamp
    create_date: str | None = Field(
        default=None,
        validation_alias=AliasChoices("createDate", "create_date"),
        serialization_alias="createDate",
    )  # ISO timestamp

    # Participant management
    users: list[Any] | None = None  # User objects with id, name, isOwner
    endusers: list[str] | None = None  # Involved contact IDs (auto-generated)
    user_ids: list[str] | None = Field(
        default=None,
        validation_alias=AliasChoices("userIds", "user_ids"),
        serialization_alias="userIds",
    )  # All participant IDs (auto-generated)

    # Status flags
    starred: bool | None = None
    pinned: bool | None = None
    archived: bool | None = None
    is_open: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("isOpen", "is_open"),
        serialization_alias="isOpen",
    )  # Open/closed state

    # Categorization
    tags: list[str] | None = None
    activity_tags: list[str] | None = Field(
        default=None,
        validation_alias=AliasChoices("activityTags", "activity_tags"),
        serialization_alias="activityTags",
    )

    # Content metadata
    has_attachments: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("hasAttachments", "has_attachments"),
        serialization_alias="hasAttachments",
    )
    has_more: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("hasMore", "has_more"),
        serialization_alias="hasMore",
    )

    # Advanced features
    email_template_ids: list[str] | None = Field(
        default=None,
        validation_alias=AliasChoices("emailTemplateIds", "email_template_ids"),
        serialization_alias="emailTemplateIds",
    )
    time_bucket: list[Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("timeBucket", "time_bucket"),
        serialization_alias="timeBucket",
    )
    sender: list[Any] | None = None  # Sender information
    history: list[Any] | None = None  # Change history
    is_custom_type: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("isCustomType", "is_custom_type"),
        serialization_alias="isCustomType",
    )

    # Internal tracking
    assignee_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("assigneeName", "assignee_name"),
        serialization_alias="assigneeName",
    )
    number_of_parts: int | None = Field(
        default=None,
        validation_alias=AliasChoices("numberOfParts", "number_of_parts"),
        serialization_alias="numberOfParts",
    )
    number_of_relevant_parts: int | None = Field(
        default=None,
        validation_alias=AliasChoices("numberOfRelevantParts", "number_of_relevant_parts"),
        serialization_alias="numberOfRelevantParts",
    )

    # Custom fields
    custom: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class Conversations(BaseResource):
    """Conversations resource for PyPlanhat API."""

    def list(self, company_id: str | None = None) -> list[Conversation]:
        """List all conversations, optionally filtered by company.

        Args:
            company_id: Optional company ID to filter conversations.

        Returns:
            List of conversations.
        """
        url = "/conversations"
        if company_id:
            url = f"/companies/{company_id}/conversations"

        response = self._client.get(url)
        data = self._handle_response(response)
        if not isinstance(data, list):
            return []
        return [Conversation(**cast(dict[str, Any], item)) for item in data]

    def get(self, conversation_id: str) -> Conversation:
        """Get a specific conversation by ID.

        Args:
            conversation_id: The ID of the conversation to retrieve.

        Returns:
            The requested conversation.

        Raises:
            InvalidRequestError: If the conversation is not found.
        """
        response = self._client.get(f"/conversations/{conversation_id}")
        data = self._handle_response(response)
        if data is None:
            raise InvalidRequestError("Conversation not found", 404, "")
        return Conversation(**data)

    def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation.

        Args:
            conversation: The conversation data to create.

        Returns:
            The created conversation.
        """
        response = self._client.post(
            "/conversations", json=conversation.model_dump(exclude_none=True, by_alias=True)
        )
        data = self._handle_response(response)
        assert data is not None  # POST should never return 204
        return Conversation(**data)

    def update(self, conversation_id: str, conversation: Conversation) -> Conversation:
        """Update an existing conversation.

        Args:
            conversation_id: The ID of the conversation to update.
            conversation: The updated conversation data.

        Returns:
            The updated conversation.

        Raises:
            InvalidRequestError: If the conversation is not found.
        """
        response = self._client.put(
            f"/conversations/{conversation_id}",
            json=conversation.model_dump(exclude_none=True, by_alias=True),
        )
        data = self._handle_response(response)
        assert data is not None  # PUT should never return 204
        return Conversation(**data)

    def delete(self, conversation_id: str) -> None:
        """Delete a conversation.

        Args:
            conversation_id: The ID of the conversation to delete.

        Raises:
            InvalidRequestError: If the conversation is not found.
        """
        response = self._client.delete(f"/conversations/{conversation_id}")
        self._handle_response(response)
