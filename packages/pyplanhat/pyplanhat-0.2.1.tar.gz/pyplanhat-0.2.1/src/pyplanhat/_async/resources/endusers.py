"""EndUser resource for PyPlanhat SDK."""

from typing import Any, cast

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from pyplanhat._async.resources.base import BaseResource
from pyplanhat._exceptions import InvalidRequestError


class EndUser(BaseModel):
    """EndUser resource from Planhat API.

    Represents an end user with all documented fields from the Planhat API schema.
    Note: The Planhat API requires companyId + (email OR externalId OR sourceId),
    but these fields are optional at the model level for flexibility.
    """

    # Required by Planhat API
    company_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("companyId", "company_id"),
        serialization_alias="companyId",
    )

    # Key properties for upsert operations
    id: str | None = Field(
        default=None, validation_alias=AliasChoices("_id", "id"), serialization_alias="_id"
    )
    email: str | None = None  # Primary identifier
    external_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("externalId", "external_id"),
        serialization_alias="externalId",
    )
    source_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("sourceId", "source_id"),
        serialization_alias="sourceId",
    )

    # Core identity fields
    first_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("firstName", "first_name"),
        serialization_alias="firstName",
    )
    last_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("lastName", "last_name"),
        serialization_alias="lastName",
    )
    name: str | None = None  # Full name
    position: str | None = None  # Role/position (e.g., "CFO")
    phone: str | None = None

    # User flags
    featured: bool | None = None
    primary: bool | None = None
    archived: bool | None = None

    # Organization
    tags: list[str] | None = None
    other_emails: list[str] | None = Field(
        default=None,
        validation_alias=AliasChoices("otherEmails", "other_emails"),
        serialization_alias="otherEmails",
    )

    # Activity & Engagement (auto-generated, read-only)
    last_active: str | None = Field(
        default=None,
        validation_alias=AliasChoices("lastActive", "last_active"),
        serialization_alias="lastActive",
    )  # ISO timestamp
    beats: int | None = None
    beats_total: int | None = Field(
        default=None,
        validation_alias=AliasChoices("beatsTotal", "beats_total"),
        serialization_alias="beatsTotal",
    )
    beat_trend: str | None = Field(
        default=None,
        validation_alias=AliasChoices("beatTrend", "beat_trend"),
        serialization_alias="beatTrend",
    )
    convs14: int | None = None  # Conversations in last 14 days
    convs_total: int | None = Field(
        default=None,
        validation_alias=AliasChoices("convsTotal", "convs_total"),
        serialization_alias="convsTotal",
    )
    experience: str | None = None
    last_touch: str | None = Field(
        default=None,
        validation_alias=AliasChoices("lastTouch", "last_touch"),
        serialization_alias="lastTouch",
    )  # ISO timestamp
    last_touch_type: str | None = Field(
        default=None,
        validation_alias=AliasChoices("lastTouchType", "last_touch_type"),
        serialization_alias="lastTouchType",
    )
    last_touch_by_type: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("lastTouchByType", "last_touch_by_type"),
        serialization_alias="lastTouchByType",
    )

    # NPS Data (auto-generated, read-only)
    nps: int | None = None  # NPS score
    nps_comment: str | None = Field(
        default=None,
        validation_alias=AliasChoices("npsComment", "nps_comment"),
        serialization_alias="npsComment",
    )
    nps_date: str | None = Field(
        default=None,
        validation_alias=AliasChoices("npsDate", "nps_date"),
        serialization_alias="npsDate",
    )  # ISO date
    nps_sent: str | None = Field(
        default=None,
        validation_alias=AliasChoices("npsSent", "nps_sent"),
        serialization_alias="npsSent",
    )  # ISO date
    nps_unsubscribed: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("npsUnsubscribed", "nps_unsubscribed"),
        serialization_alias="npsUnsubscribed",
    )

    # Conversation Integration
    last_activities: list[Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("lastActivities", "last_activities"),
        serialization_alias="lastActivities",
    )  # Activity objects
    related_endusers: list[str] | None = Field(
        default=None,
        validation_alias=AliasChoices("relatedEndusers", "related_endusers"),
        serialization_alias="relatedEndusers",
    )  # Related/duplicate user IDs

    # Custom fields
    custom: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class EndUsers(BaseResource):
    """EndUsers resource for PyPlanhat API."""

    async def list(self, company_id: str | None = None) -> list[EndUser]:
        """List all end users, optionally filtered by company.

        Args:
            company_id: Optional company ID to filter end users.

        Returns:
            List of end users.
        """
        url = "/endusers"
        if company_id:
            url = f"/companies/{company_id}/endusers"

        response = await self._client.get(url)
        data = await self._handle_response(response)
        if not isinstance(data, list):
            return []
        return [EndUser(**cast(dict[str, Any], item)) for item in data]

    async def get(self, enduser_id: str) -> EndUser:
        """Get a specific end user by ID.

        Args:
            enduser_id: The ID of the end user to retrieve.

        Returns:
            The requested end user.

        Raises:
            InvalidRequestError: If the end user is not found.
        """
        response = await self._client.get(f"/endusers/{enduser_id}")
        data = await self._handle_response(response)
        if data is None:
            raise InvalidRequestError("EndUser not found", 404, "")
        return EndUser(**data)

    async def create(self, enduser: EndUser) -> EndUser:
        """Create a new end user.

        Args:
            enduser: The end user data to create.

        Returns:
            The created end user.
        """
        response = await self._client.post(
            "/endusers", json=enduser.model_dump(exclude_none=True, by_alias=True)
        )
        data = await self._handle_response(response)
        assert data is not None  # POST should never return 204
        return EndUser(**data)

    async def update(self, enduser_id: str, enduser: EndUser) -> EndUser:
        """Update an existing end user.

        Args:
            enduser_id: The ID of the end user to update.
            enduser: The updated end user data.

        Returns:
            The updated end user.

        Raises:
            InvalidRequestError: If the end user is not found.
        """
        response = await self._client.put(
            f"/endusers/{enduser_id}", json=enduser.model_dump(exclude_none=True, by_alias=True)
        )
        data = await self._handle_response(response)
        assert data is not None  # PUT should never return 204
        return EndUser(**data)

    async def delete(self, enduser_id: str) -> None:
        """Delete an end user.

        Args:
            enduser_id: The ID of the end user to delete.

        Raises:
            InvalidRequestError: If the end user is not found.
        """
        response = await self._client.delete(f"/endusers/{enduser_id}")
        await self._handle_response(response)
