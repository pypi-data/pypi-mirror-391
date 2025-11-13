"""
Basic tests for the Avela API client.

Note: These are placeholder tests. Full test suite would require mocking.
"""

import pytest

from avela import AuthenticationError, AvelaAPI, AvelaError


def test_client_initialization():
    """Test that client can be initialized with proper parameters."""
    api = AvelaAPI(client_id='test_id', client_secret='test_secret', environment='uat')

    assert api.environment == 'uat'
    assert api.base_url == 'https://uat.execute-api.apply.avela.org/api/rest/v2'
    assert api.timeout == 30


def test_client_custom_timeout():
    """Test custom timeout setting."""
    api = AvelaAPI(
        client_id='test_id', client_secret='test_secret', environment='uat', timeout=60
    )

    assert api.timeout == 60


def test_dynamic_resource_access():
    """Test that dynamic resource access returns EndpointProxy."""
    api = AvelaAPI(client_id='test_id', client_secret='test_secret', environment='uat')

    # Should not raise an error
    applicants_proxy = api.applicants
    forms_proxy = api.forms

    assert hasattr(applicants_proxy, 'list')
    assert hasattr(applicants_proxy, 'get')
    assert hasattr(applicants_proxy, 'create')


def test_context_manager():
    """Test that client works as a context manager."""
    with AvelaAPI(
        client_id='test_id', client_secret='test_secret', environment='uat'
    ) as api:
        assert api is not None
        assert hasattr(api, 'session')


# Add more tests here for:
# - Authentication
# - Error handling
# - Request making
# - Token refresh
# etc.
