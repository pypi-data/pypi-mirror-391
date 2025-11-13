"""
Avela Python SDK

Official Python SDK for the Avela Education Platform API.

Example usage:
    ```python
    from avela import AvelaAPI

    # Initialize the client
    api = AvelaAPI(
        client_id="your_client_id",
        client_secret="your_client_secret",
        environment="uat"
    )

    # Use dynamic endpoint access
    applicants = api.applicants.list(limit=100, offset=0)
    form = api.forms.get("form-id-123")

    # Update form questions
    api.forms.call("POST", "form-id/questions", json={
        "questions": [
            {
                "key": "question_key",
                "type": "FreeText",
                "answer": {"free_text": {"value": "Answer"}}
            }
        ]
    })
    ```
"""

from .__version__ import __version__
from .client import AvelaAPI
from .exceptions import (
    APIError,
    AuthenticationError,
    AvelaError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)

__all__ = [
    '__version__',
    'AvelaAPI',
    'AvelaError',
    'APIError',
    'AuthenticationError',
    'ValidationError',
    'NotFoundError',
    'RateLimitError',
    'ServerError',
]
