"""
Main Avela API client.
"""

from typing import Any

import requests

from .__version__ import __version__
from .auth import OAuth2Authenticator
from .exceptions import (
    APIError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .resources import EndpointProxy


class AvelaAPI:
    """
    Main client for interacting with the Avela API.

    This client provides dynamic access to all Avela API endpoints without
    requiring hardcoded methods for each endpoint.

    Example:
        ```python
        from avela import AvelaAPI

        # Initialize client
        api = AvelaAPI(
            client_id="your_client_id",
            client_secret="your_client_secret",
            environment="uat"
        )

        # Use dynamic endpoint access
        applicants = api.applicants.list(limit=100)
        form = api.forms.get("form-id-123")
        api.forms.call("POST", "form-id/questions", json={"questions": [...]})
        ```
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        environment: str = 'uat',
        timeout: int = 30,
    ):
        """
        Initialize the Avela API client.

        Args:
            client_id: OAuth2 client ID from Avela
            client_secret: OAuth2 client secret from Avela
            environment: Environment to connect to (dev, qa, uat, prod)
            timeout: Request timeout in seconds (default: 30)
        """
        self.environment = environment
        self.timeout = timeout

        # Initialize authenticator
        self.auth = OAuth2Authenticator(client_id, client_secret, environment)

        # Build base URL
        self.base_url = f'https://{environment}.execute-api.apply.avela.org/api/rest/v2'

        # Create a requests session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(
            {
                'User-Agent': f'avela-python/{__version__}',
                'Content-Type': 'application/json',
            }
        )

    def __getattr__(self, name: str) -> EndpointProxy:
        """
        Dynamically handle resource access.

        This allows accessing resources like:
            api.applicants
            api.forms
            api.{any_resource}

        Args:
            name: Resource name

        Returns:
            EndpointProxy for the resource
        """
        # Avoid infinite recursion for private attributes
        if name.startswith('_'):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        return EndpointProxy(self, name)

    def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Make an authenticated request to the Avela API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path (without base URL)
            **kwargs: Additional arguments to pass to requests

        Returns:
            JSON response from the API

        Raises:
            APIError: For various API errors
            NotFoundError: When resource is not found (404)
            RateLimitError: When rate limit is exceeded (429)
            ServerError: For server errors (5xx)
            ValidationError: For validation errors (400)
        """
        # Build full URL
        url = f'{self.base_url}/{endpoint}'

        # Get authentication headers
        headers = kwargs.pop('headers', {})
        headers.update(self.auth.get_auth_headers())

        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        try:
            # Make the request
            response = self.session.request(
                method=method.upper(), url=url, headers=headers, **kwargs
            )

            # Handle different status codes
            if response.status_code == 404:
                raise NotFoundError(
                    message='Resource not found', response_body=response.text
                )
            elif response.status_code == 429:
                raise RateLimitError(
                    message='Rate limit exceeded', response_body=response.text
                )
            elif response.status_code == 400:
                raise ValidationError(f'Validation error: {response.text}')
            elif 500 <= response.status_code < 600:
                raise ServerError(
                    message='Server error',
                    status_code=response.status_code,
                    response_body=response.text,
                )

            # Raise for other HTTP errors
            response.raise_for_status()

            # Parse and return JSON response
            result: dict[str, Any] | list[dict[str, Any]] = response.json()
            return result

        except requests.exceptions.RequestException as e:
            # Wrap requests exceptions in our custom exception
            if hasattr(e, 'response') and e.response is not None:
                raise APIError(
                    message=str(e),
                    status_code=e.response.status_code
                    if hasattr(e.response, 'status_code')
                    else None,
                    response_body=e.response.text,
                )
            else:
                raise APIError(message=str(e))

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> 'AvelaAPI':
        """Support for context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Close session when exiting context."""
        self.close()
