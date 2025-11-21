import logging
import os
import typing as t
from typing import Any

import requests
from dapla_auth_client import AuthClient

from ssb_guardian_client.const import GUARDIAN_URLS
from ssb_guardian_client.const import DaplaEnvironment

logger = logging.getLogger(__name__)


class GuardianClient:
    """Client for interacting with the Maskinporten Guardian."""

    @staticmethod
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

    @staticmethod
    def call_api(
        api_endpoint_url: str,
        maskinporten_client_id: str,
        scopes: str,
        labid: str | None = None,
    ) -> Any:
        """Call an external API using Maskinporten Guardian.

        Args:
            api_endpoint_url: URL to the target API
            maskinporten_client_id: the Maskinporten client id
            scopes: the Maskinporten scopes
            labid: the user's personal token. Automatic fetch attempt will be made if left empty.

        Raises:
            RuntimeError: If the API call fails

        Returns:
            The endpoint json response
        """
        logger.info(f"Calling external API: {api_endpoint_url}")
        logger.debug(
            f"Maskinporten client ID: {maskinporten_client_id}, scopes: {scopes}"
        )

        guardian_endpoint_url = GuardianClient.get_guardian_url()

        if labid is None:
            logger.debug("No labid provided, fetching personal token automatically")
            labid = AuthClient.fetch_personal_token()

        body = {"maskinportenClientId": maskinporten_client_id, "scopes": scopes}
        logger.debug("Requesting Maskinporten token from Guardian")
        maskinporten_token = GuardianClient.get_maskinporten_token(
            guardian_endpoint_url, labid, body=body
        )

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

    @staticmethod
    def get_maskinporten_token(
        guardian_endpoint: str, keycloak_token: str, body: dict[str, str]
    ) -> str:
        """Retrieve access token from Maskinporten Guardian.

        Args:
            guardian_endpoint: URL to the maskinporten guardian
            keycloak_token: the user's Keycloak token
            body: maskinporten request body

        Raises:
            RuntimeError: If the Guardian token request fails

        Returns:
            The maskinporten access token
        """
        logger.info(f"Requesting Maskinporten token from Guardian: {guardian_endpoint}")
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
