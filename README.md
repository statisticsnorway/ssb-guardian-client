# SSB Guardian Client

[![PyPI](https://img.shields.io/pypi/v/ssb-guardian-client.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/ssb-guardian-client.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/ssb-guardian-client)][pypi status]
[![License](https://img.shields.io/pypi/l/ssb-guardian-client)][license]

[![Documentation](https://github.com/statisticsnorway/ssb-guardian-client/actions/workflows/docs.yml/badge.svg)][documentation]
[![Tests](https://github.com/statisticsnorway/ssb-guardian-client/actions/workflows/tests.yml/badge.svg)][tests]
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_ssb-guardian-client&metric=coverage)][sonarcov]
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_ssb-guardian-client&metric=alert_status)][sonarquality]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)][poetry]

[pypi status]: https://pypi.org/project/ssb-guardian-client/
[documentation]: https://statisticsnorway.github.io/ssb-guardian-client
[tests]: https://github.com/statisticsnorway/ssb-guardian-client/actions?workflow=Tests
[sonarcov]: https://sonarcloud.io/summary/overall?id=statisticsnorway_ssb-guardian-client
[sonarquality]: https://sonarcloud.io/summary/overall?id=statisticsnorway_ssb-guardian-client
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[poetry]: https://python-poetry.org/

## Features

- **Maskinporten Integration**: Seamless integration with Maskinporten for secure API authentication
- **Guardian Token Management**: Automatic retrieval and management of Maskinporten access tokens via Guardian
- **Multi-Environment Support**: Works across DEV, TEST, and PROD environments in the Dapla platform
- **Simple API**: Easy-to-use client interface for calling external APIs with Maskinporten authentication
- **Automatic Token Handling**: Fetches personal tokens automatically using dapla-auth-client

## Requirements

- Python 3.10 or higher
- Access to Statistics Norway's Dapla platform
- Valid Maskinporten client credentials
- `DAPLA_ENVIRONMENT` environment variable set to one of: `DEV`, `TEST`, or `PROD`

## Installation

You can install _SSB Guardian Client_ via [pip] from [PyPI]:

```console
pip install ssb-guardian-client
```

## Usage

### Basic Usage

The simplest way to call an external API with Maskinporten authentication:

```python
from ssb_guardian_client import call_api

# Call an external API with Maskinporten authentication
response = call_api(
    api_endpoint_url="https://api.example.com/data",
    maskinporten_client_id="your-maskinporten-client-id",
    scopes="scope1 scope2",
)

# The response contains the JSON data from the API
print(response)
```

The `call_api` function automatically:
- Fetches your personal Keycloak token using `dapla-auth-client`
- Requests a Maskinporten access token from Guardian
- Calls the target API with the Maskinporten token
- Returns the JSON response

### Getting Maskinporten Tokens Directly

If you need more control or only want to retrieve the Maskinporten token:

```python
from ssb_guardian_client import get_maskinporten_token

# Get a Maskinporten token for custom use
maskinporten_token = get_maskinporten_token(
    body={
        "maskinportenClientId": "your-client-id",
        "scopes": "scope1 scope2"
    }
)

# Use the token for custom API calls
import requests
response = requests.get(
    "https://api.example.com/data",
    headers={"Authorization": f"Bearer {maskinporten_token}"}
)
```

The `get_maskinporten_token` function automatically fetches your personal Keycloak token and retrieves the appropriate Guardian URL based on your environment.

### Working with Guardian URLs

To get the Guardian URL for your current environment:

```python
from ssb_guardian_client import get_guardian_url

# Get the Guardian URL based on DAPLA_ENVIRONMENT
guardian_url = get_guardian_url()
print(guardian_url)
```

### Environment Configuration

The client automatically detects the Dapla environment from the `DAPLA_ENVIRONMENT` environment variable and uses the appropriate Guardian URL:

- **DEV/TEST**: `https://guardian.intern.test.ssb.no/maskinporten/access-token`
- **PROD**: `https://guardian.intern.ssb.no/maskinporten/access-token`

Make sure the `DAPLA_ENVIRONMENT` variable is set to one of: `DEV`, `TEST`, or `PROD`.

### Complete Example

Here's a complete example showing typical usage:

```python
import os
from ssb_guardian_client import call_api

# Ensure environment is set (usually already set in Dapla notebooks)
# os.environ["DAPLA_ENVIRONMENT"] = "TEST"

# Call an external API
try:
    response = call_api(
        api_endpoint_url="https://api.external-service.no/v1/data",
        maskinporten_client_id="my-maskinporten-client",
        scopes="nav:some/scope nav:another/scope",
    )
    
    # Process the response
    for item in response.get("data", []):
        print(item)
        
except RuntimeError as e:
    print(f"API call failed: {e}")
```

Please see the [Reference Guide] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## Development

### Setting Up a Development Environment

1. Clone the repository:
   ```console
   git clone https://github.com/statisticsnorway/ssb-guardian-client.git
   cd ssb-guardian-client
   ```

2. Install [Poetry](https://python-poetry.org/) if you haven't already.

3. Install dependencies:
   ```console
   poetry install
   ```

4. Set up pre-commit hooks:
   ```console
   poetry run pre-commit install
   ```

### Running Tests

Run tests with pytest:

```console
poetry run pytest
```

Run tests with coverage:

```console
poetry run coverage run -m pytest
poetry run coverage report
```

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting and code quality checks
- **MyPy**: Static type checking
- **pre-commit**: Git hooks for automated checks

Run all checks:

```console
poetry run pre-commit run --all-files
```

## License

Distributed under the terms of the [MIT license][license],
_SSB Guardian Client_ is free and open source software.

## Troubleshooting

### Common Issues

**ValueError: Unknown environment**
- Ensure the `DAPLA_ENVIRONMENT` environment variable is set to one of: `DEV`, `TEST`, or `PROD`

**RuntimeError: Error getting maskinporten access-token from guardian**
- Verify your Maskinporten client ID and scopes are correct
- Ensure you have the necessary permissions to use the specified Maskinporten client
- Check that your Keycloak token is valid

**RuntimeError: Error calling target API**
- Verify the API endpoint URL is correct
- Ensure the Maskinporten scopes match what the API requires
- Check that the API is accessible from your environment

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [Statistics Norway]'s [SSB PyPI Template].

[statistics norway]: https://www.ssb.no/en
[pypi]: https://pypi.org/
[ssb pypi template]: https://github.com/statisticsnorway/ssb-pypitemplate
[file an issue]: https://github.com/statisticsnorway/ssb-guardian-client/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/statisticsnorway/ssb-guardian-client/blob/main/LICENSE
[contributor guide]: https://github.com/statisticsnorway/ssb-guardian-client/blob/main/CONTRIBUTING.md
[reference guide]: https://statisticsnorway.github.io/ssb-guardian-client/reference.html
