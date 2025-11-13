"""
OAuth2 authentication for the Avela API.
"""

from datetime import datetime, timedelta

import requests

from .exceptions import AuthenticationError


class OAuth2Authenticator:
    """Handles OAuth2 client credentials authentication for Avela API."""

    def __init__(self, client_id: str, client_secret: str, environment: str = 'uat'):
        """
        Initialize OAuth2 authenticator.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            environment: Avela environment (dev, qa, uat, prod)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment

        self.access_token: str | None = None
        self.token_expires_at: datetime | None = None

        # Build auth URL and audience
        if environment == 'prod':
            self.auth_url = 'https://auth.avela.org/oauth/token'
            self.audience = 'https://api.apply.avela.org/v1/graphql'
        else:
            self.auth_url = f'https://{environment}.auth.avela.org/oauth/token'
            self.audience = f'https://{environment}.api.apply.avela.org/v1/graphql'

    def authenticate(self) -> str:
        """
        Authenticate and get access token using OAuth2 client credentials flow.

        Returns:
            Access token string

        Raises:
            AuthenticationError: If authentication fails
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': self.audience,
        }

        try:
            response = requests.post(
                self.auth_url, data=data, headers=headers, timeout=30
            )
            response.raise_for_status()

            token_data = response.json()

            self.access_token = token_data.get('access_token')
            if not self.access_token:
                raise AuthenticationError('No access token in response')

            # Calculate token expiration (default 24 hours)
            expires_in = token_data.get('expires_in', 86400)
            # Subtract 5 minutes as buffer
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

            return self.access_token

        except requests.exceptions.RequestException as e:
            error_msg = f'Authentication failed: {str(e)}'
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f'{error_msg}\nResponse: {e.response.text}'
            raise AuthenticationError(error_msg)

    def get_token(self) -> str:
        """
        Get valid access token, refreshing if needed.

        Returns:
            Valid access token

        Raises:
            AuthenticationError: If authentication fails
        """
        if self.is_token_expired():
            self.authenticate()

        if not self.access_token:
            raise AuthenticationError('No access token available')

        return self.access_token

    def is_token_expired(self) -> bool:
        """
        Check if current token is expired or will expire soon.

        Returns:
            True if token is expired or about to expire
        """
        if not self.access_token or not self.token_expires_at:
            return True

        return datetime.now() >= self.token_expires_at

    def get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers with valid token.

        Returns:
            Dictionary with Authorization header

        Raises:
            AuthenticationError: If authentication fails
        """
        token = self.get_token()
        return {'Authorization': f'Bearer {token}'}
