import logging
import os
import typing as t
from collections.abc import Sequence
from typing import Any

import requests
from dapla_auth_client import AuthClient

from ssb_guardian_client.const import GUARDIAN_URLS
from ssb_guardian_client.const import DaplaEnvironment

logger = logging.getLogger(__name__)


class GuardianClient:
    """Client for interacting with the SSB Guardian service.

    This class provides methods to retrieve Maskinporten tokens via Guardian
    and make authenticated API calls to external services.

    Example:
        >>> import os
        >>> os.environ["DAPLA_ENVIRONMENT"] = "TEST"  # doctest: +SKIP
        >>> client = GuardianClient()  # doctest: +SKIP
        >>> response = client.call_api(  # doctest: +SKIP
        ...     "https://api.example.com/data",
        ...     "my-client-id",
        ...     "scope1 scope2"
        ... )
    """

    def __init__(self) -> None:
        """Initialize the GuardianClient."""
        self.guardian_url = get_guardian_url()

    def get_maskinporten_token(
        self, maskinporten_client_id: str, scopes: str | Sequence[str]
    ) -> str:
        """Retrieve access token from Maskinporten Guardian.

        Args:
            maskinporten_client_id: The Maskinporten client ID
            scopes: The Maskinporten scopes. Can be either:
                - A space-separated string (e.g., "scope1 scope2")
                - A list/sequence of scopes (e.g., ["scope1", "scope2"])

        Returns:
            The maskinporten access token

        Raises:
            RuntimeError: If the Guardian token request fails
        """
        guardian_endpoint = self.guardian_url
        keycloak_token = AuthClient.fetch_personal_token()

        logger.info(f"Requesting Maskinporten token from Guardian: {guardian_endpoint}")
        body = {"maskinportenClientId": maskinporten_client_id, "scopes": scopes}
        logger.debug(f"Request body: {body}")

        guardian_response = requests.post(
            guardian_endpoint,
            headers={
                "Authorization": f"Bearer {keycloak_token}",
                "Content-type": "application/json",
            },
            json=body,
        )
        if guardian_response.status_code == 200:
            logger.info("Successfully received Maskinporten token from Guardian")
            return t.cast(str, guardian_response.json()["accessToken"])
        else:
            error_msg = (
                f"Error getting maskinporten access-token from guardian: <{guardian_response.status_code}: "
                f"{guardian_response.text or guardian_response.reason}>"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def call_api(
        self,
        api_endpoint_url: str,
        maskinporten_client_id: str,
        scopes: str,
    ) -> Any:
        """Call an external API using Maskinporten Guardian.

        Args:
            api_endpoint_url: URL to the target API
            maskinporten_client_id: The Maskinporten client ID
            scopes: The Maskinporten scopes as a space-separated string (e.g., "scope1 scope2")

        Returns:
            The endpoint json response

        Raises:
            RuntimeError: If the API call fails
        """
        logger.info(f"Calling external API: {api_endpoint_url}")
        logger.debug(
            f"Maskinporten client ID: {maskinporten_client_id}, scopes: {scopes}"
        )

        logger.debug("Requesting Maskinporten token from Guardian")
        maskinporten_token = self.get_maskinporten_token(maskinporten_client_id, scopes)

        logger.debug(f"Making GET request to target API: {api_endpoint_url}")
        api_response = requests.get(
            api_endpoint_url,
            headers={
                "Authorization": f"Bearer {maskinporten_token}",
                "Accept": "application/json",
            },
        )
        if api_response.status_code == 200:
            logger.info(f"Successfully called API: {api_endpoint_url}")
            return api_response.json()
        else:
            error_msg = (
                f"Error calling target API ({api_endpoint_url}): Status code <{api_response.status_code}"
                f" - {api_response.text or api_response.reason}>"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)


def get_guardian_url() -> str:
    """Get the Guardian URL for the current environment."""
    env = DaplaEnvironment(os.getenv("DAPLA_ENVIRONMENT"))
    logger.debug(f"Resolved DAPLA_ENVIRONMENT to: {env}")
    try:
        url = GUARDIAN_URLS[env]
        logger.info(f"Using Guardian URL: {url}")
        return url
    except KeyError as err:
        logger.error(f"Unknown environment: {env}")
        raise ValueError(f"Unknown environment: {env}") from err
