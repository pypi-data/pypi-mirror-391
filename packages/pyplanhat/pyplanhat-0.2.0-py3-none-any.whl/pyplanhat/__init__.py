"""PyPlanhat SDK - Async-first Python SDK for Planhat API."""

from pyplanhat._async.client import AsyncPyPlanhat
from pyplanhat._async.resources import Company, Conversation, EndUser
from pyplanhat._exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InvalidRequestError,
    PyPlanhatError,
    RateLimitError,
    ServerError,
)

__version__ = "0.2.0"

__all__ = [
    "APIConnectionError",
    "APIError",
    "AsyncPyPlanhat",
    "AuthenticationError",
    "Company",
    "Conversation",
    "EndUser",
    "InvalidRequestError",
    "PyPlanhatError",
    "RateLimitError",
    "ServerError",
]

# Sync client will be available after code generation
try:
    from pyplanhat._sync.client import PyPlanhat  # noqa: F401

    __all__.append("PyPlanhat")
except ImportError:
    # Sync code not yet generated
    pass


def main() -> None:
    """Entry point for CLI."""
    print("PyPlanhat SDK v0.2.0")
    print("Documentation: https://github.com/ddlaws0n/pyplanhat")
