"""
Dynamic resource proxy for Avela API endpoints.

This module provides dynamic access to API resources without hardcoding endpoints.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import AvelaAPI


class EndpointProxy:
    """
    Proxy class that dynamically handles API resource endpoints.

    This allows calling endpoints like:
        api.applicants.list()
        api.forms.get("form-id")
        api.forms.update("form-id", data={...})

    Without needing to predefine every endpoint in the SDK.
    """

    def __init__(self, api: AvelaAPI, resource_name: str):
        """
        Initialize endpoint proxy.

        Args:
            api: Parent AvelaAPI instance
            resource_name: Name of the resource (e.g., "applicants", "forms")
        """
        self._api = api
        self._resource_name = resource_name

    def list(self, **params: Any) -> dict[str, Any] | builtins.list[dict[str, Any]]:
        """
        List resources with optional query parameters.

        Example:
            api.applicants.list(limit=100, offset=0)

        Args:
            **params: Query parameters to pass to the API

        Returns:
            List of resource dictionaries or dict response
        """
        return self._api._request('GET', self._resource_name, params=params)

    def get(self, resource_id: str) -> dict[str, Any] | builtins.list[dict[str, Any]]:
        """
        Get a single resource by ID.

        Example:
            api.forms.get("form-id-123")

        Args:
            resource_id: ID of the resource to retrieve

        Returns:
            Resource dictionary or list response
        """
        endpoint = f'{self._resource_name}/{resource_id}'
        return self._api._request('GET', endpoint)

    def create(
        self, data: dict[str, Any]
    ) -> dict[str, Any] | builtins.list[dict[str, Any]]:
        """
        Create a new resource.

        Example:
            api.applicants.create({"first_name": "John", "last_name": "Doe"})

        Args:
            data: Resource data to create

        Returns:
            Created resource dictionary or list response
        """
        return self._api._request('POST', self._resource_name, json=data)

    def update(
        self, resource_id: str, data: dict[str, Any]
    ) -> dict[str, Any] | builtins.list[dict[str, Any]]:
        """
        Update an existing resource.

        Example:
            api.forms.update("form-id", {"status": "submitted"})

        Args:
            resource_id: ID of the resource to update
            data: Updated resource data

        Returns:
            Updated resource dictionary or list response
        """
        endpoint = f'{self._resource_name}/{resource_id}'
        return self._api._request('PUT', endpoint, json=data)

    def patch(
        self, resource_id: str, data: dict[str, Any]
    ) -> dict[str, Any] | builtins.list[dict[str, Any]]:
        """
        Partially update an existing resource.

        Example:
            api.applicants.patch("applicant-id", {"email": "new@email.com"})

        Args:
            resource_id: ID of the resource to patch
            data: Partial resource data

        Returns:
            Updated resource dictionary or list response
        """
        endpoint = f'{self._resource_name}/{resource_id}'
        return self._api._request('PATCH', endpoint, json=data)

    def delete(self, resource_id: str) -> dict[str, Any] | builtins.list[dict[str, Any]]:
        """
        Delete a resource.

        Example:
            api.forms.delete("form-id")

        Args:
            resource_id: ID of the resource to delete

        Returns:
            Deletion response dictionary or list response
        """
        endpoint = f'{self._resource_name}/{resource_id}'
        return self._api._request('DELETE', endpoint)

    def call(
        self, method: str, path: str = '', **kwargs: Any
    ) -> dict[str, Any] | builtins.list[dict[str, Any]]:
        """
        Make a custom API call to this resource.

        Example:
            api.forms.call("POST", "form-id/questions", json={"questions": [...]})

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: Additional path after resource name
            **kwargs: Additional arguments to pass to the request

        Returns:
            API response
        """
        endpoint = f'{self._resource_name}/{path}' if path else self._resource_name
        return self._api._request(method.upper(), endpoint, **kwargs)
