import logging
import os
import typing as t
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any

import requests
from dapla_auth_client import AuthClient

from ssb_guardian_client.const import GUARDIAN_URLS
from ssb_guardian_client.const import DaplaEnvironment

logger = logging.getLogger(__name__)


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


def call_api(
    api_endpoint_url: str,
    maskinporten_client_id: str,
    scopes: str,
) -> Any:
    """Call an external API using Maskinporten Guardian.

    Args:
        api_endpoint_url: URL to the target API
        maskinporten_client_id: the Maskinporten client id
        scopes: the Maskinporten scopes as a space-separated string (e.g., "scope1 scope2").
            Note: This will be converted to a list for the Guardian API request.

    Raises:
        RuntimeError: If the API call fails

    Returns:
        The endpoint json response
    """
    logger.info(f"Calling external API: {api_endpoint_url}")
    logger.debug(f"Maskinporten client ID: {maskinporten_client_id}, scopes: {scopes}")

    body = {"maskinportenClientId": maskinporten_client_id, "scopes": scopes}
    logger.debug("Requesting Maskinporten token from Guardian")
    maskinporten_token = get_maskinporten_token(body=body)

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


def get_maskinporten_token(body: Mapping[str, str | Sequence[str]]) -> str:
    """Retrieve access token from Maskinporten Guardian.

    Args:
        body: maskinporten request body containing:
            - maskinportenClientId (str): The Maskinporten client ID
            - scopes (list[str] | str): The Maskinporten scopes.
                **IMPORTANT**: When calling this function directly, scopes MUST be a list/array.
                Example: {"maskinportenClientId": "...", "scopes": ["scope1", "scope2"]}
                Using a string value will result in a 400 Bad Request error from Guardian.

    Raises:
        RuntimeError: If the Guardian token request fails

    Returns:
        The maskinporten access token
    """
    guardian_endpoint = get_guardian_url()
    keycloak_token = AuthClient.fetch_personal_token()

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
